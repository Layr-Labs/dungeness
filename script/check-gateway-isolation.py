#!/usr/bin/env python3
"""Run the gateway image with production hardening and synthetic model access.

Requires local Docker (use --sudo if needed). No provider or model credentials
are read. The synthetic provider and gateway use an isolated Docker network.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SECRET = 'synthetic-isolation-access-token-0123456789'
ID_TOKEN = 'synthetic-isolation-id-token-0123456789'
ACCOUNT = 'synthetic-isolation-account-id-0123456789'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sudo', action='store_true')
    args = parser.parse_args()
    docker = (['sudo', '-n'] if args.sudo else []) + ['docker']
    tag = 'gateway-isolation-' + uuid.uuid4().hex[:12]
    names = [tag + '-mock', tag + '-gateway']

    def run(*cmd, **kwargs):
        return subprocess.run([*docker, *cmd], check=True, text=True, **kwargs)

    # Exact compiler flags are also checked in test_command_harness.py.
    hardening = ['--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges:true',
                 '--pids-limit=128', '--memory=1g', '--cpus=2',
                 '--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=128m,mode=1777']
    with tempfile.TemporaryDirectory(prefix='gateway-isolation-') as tmp:
        root = Path(tmp)
        usage = root / 'usage'; usage.mkdir()
        auth = root / 'auth.json'
        auth.write_text(json.dumps({'tokens': {'access_token': SECRET,
            'account_id': ACCOUNT, 'id_token': ID_TOKEN}})); auth.chmod(0o600)
        mock = root / 'mock.py'
        mock.write_text('''from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, threading
RESOURCE=b'x'*(2*1024*1024)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args): pass
 def do_GET(self):
  if self.path=='/task': body=json.dumps(TASK,sort_keys=True,separators=(',',':')).encode()
  elif self.path=='/task/files/fixture.bin': body=RESOURCE
  else: self.send_error(404); return
  self.send_response(200); self.send_header('Content-Length',str(len(body)))
  self.end_headers(); self.wfile.write(body)
 def do_POST(self):
  self.rfile.read(int(self.headers.get('content-length','0')))
  assert self.headers['authorization'] == 'Bearer '+SECRET
  body=json.dumps({'output_text':SECRET+' '+ID_TOKEN+' '+ACCOUNT,
                   'usage':{'input_tokens':100,'output_tokens':10}}).encode()
  self.send_response(200); self.send_header('Content-Type','application/json')
  self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
threading.Thread(target=ThreadingHTTPServer(('0.0.0.0',8091),Handler).serve_forever,daemon=True).start()
ThreadingHTTPServer(('0.0.0.0',8081),Handler).serve_forever()
''')
        task={'schema_version':1,'attachments':[{'name':'fixture.bin','bytes':2*1024*1024,
              'sha256':hashlib.sha256(b'x'*(2*1024*1024)).hexdigest(),'media_type':'application/octet-stream'}]}
        mock.write_text('TASK='+repr(task)+'\n'+'SECRET='+repr(SECRET)+'\nID_TOKEN='+repr(ID_TOKEN)+'\nACCOUNT='+repr(ACCOUNT)+'\n'+mock.read_text())
        try:
            run('build', '-q', '-t', tag, str(ROOT / 'services/gateway'))
            run('network', 'create', '--internal', tag, stdout=subprocess.DEVNULL)
            run('run', '-d', '--name', names[0], '--network', tag, '--network-alias', 'mock', '--network-alias', 'problem',
                *hardening, '--mount', f'type=bind,src={mock},dst=/mock.py,readonly',
                tag, 'python', '/mock.py', stdout=subprocess.DEVNULL)
            env = {'TESTBED_RUN_ID': 'synthetic-isolation', 'TESTBED_USAGE_DIR':'/var/lib/testbed/usage',
                   'MAX_SEARCHES':'0','MAX_FETCHES':'0','MAX_MODEL_REQUESTS':'5',
                   'MAX_MODEL_TOKENS':'10000','MAX_MODEL_USD':'1',
                   'EXA_END_PUBLISHED_DATE':'2026-10-23T00:00:00Z',
                   'DUNGENESS_TASK_SHA256':hashlib.sha256(json.dumps(task,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                   'DUNGENESS_REQUIRE_MODEL_ALLOWLIST':'1',
                   'DUNGENESS_ALLOWED_MODELS':'[["openai-chatgpt","gpt-6-astra"]]',
                   'DUNGENESS_CHATGPT_AUTH_FILE':'/run/dungeness/auth.json',
                   'CHATGPT_UPSTREAM_BASE_URL':'http://mock:8081/v1'}
            command = ['run','-d','--name',names[1],'--network',tag,*hardening,
                       '--user',f'{os.getuid()}:{os.getgid()}',
                       '--mount',f'type=bind,src={usage},dst=/var/lib/testbed/usage',
                       '--mount',f'type=bind,src={auth},dst=/run/dungeness/auth.json,readonly']
            for key,value in env.items(): command += ['-e',key+'='+value]
            run(*command,tag,stdout=subprocess.DEVNULL)
            # Query from inside the container, avoiding any public port exposure.
            request_code = '''import json,urllib.request
r=urllib.request.Request('http://localhost:8080/model/chatgpt/v1/responses',
 data=json.dumps({'model':'gpt-6-astra','input':'synthetic fixture','stream':False}).encode(),
 headers={'Content-Type':'application/json'})
body=urllib.request.urlopen(r).read().decode()
assert body.count('[REDACTED]')==3,body
status=json.load(urllib.request.urlopen('http://localhost:8080/status'))
assert status['usage']['normalized_usd']>0
assert urllib.request.urlopen('http://localhost:8080/task/files/fixture.bin').read()==b'x'*(2*1024*1024)
print('Inference, accounting and a resource download that spills to temporary disk work; credentials redacted.')
'''
            for attempt in range(60):
                probe = subprocess.run([*docker,'exec',names[1],'python','-c',
                    "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')"],
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                if probe.returncode == 0: break
                time.sleep(1)
            else: raise RuntimeError('Gateway failed to become healthy')
            run('exec',names[1],'python','-c',request_code)
            run('exec',names[1],'python','-c','''from pathlib import Path
import errno
try: Path('/app/should-not-write').write_text('no')
except OSError as e: assert e.errno in (errno.EROFS,errno.EACCES)
else: raise AssertionError('Gateway root is writable')
Path('/tmp/probe').write_text('temporary workspace works')
s=Path('/proc/self/status').read_text()
assert 'NoNewPrivs:\\t1' in s and 'CapEff:\\t0000000000000000' in s
try: Path('/run/dungeness/auth.json').write_text('no')
except OSError: pass
else: raise AssertionError('Credential mount is writable')
print('Root and credential mount read-only; temporary writes work; no capabilities or privilege escalation.')
''')
            assert (usage/'events.jsonl').is_file() and (usage/'summary.json').is_file()
            for path in usage.rglob('*'):
                if path.is_file():
                    raw=path.read_bytes()
                    for value in (SECRET,ID_TOKEN,ACCOUNT): assert value.encode() not in raw
            logs=run('logs',names[1],capture_output=True)
            for value in (SECRET,ID_TOKEN,ACCOUNT): assert value not in logs.stdout+logs.stderr
            print('PASS: local hardened gateway, read-only secret file, inference, accounting and non-disclosure.')
        finally:
            for name in names:
                subprocess.run([*docker,'rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            subprocess.run([*docker,'network','rm',tag],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            subprocess.run([*docker,'image','rm',tag],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    main()
