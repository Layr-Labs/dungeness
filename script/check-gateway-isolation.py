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
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SECRET = 'synthetic-isolation-access-token-0123456789'
ID_TOKEN = 'synthetic-isolation-id-token-0123456789'
ACCOUNT = 'synthetic-isolation-account-id-0123456789'
SECRETS = {name: 'synthetic-' + name.lower() + '-0123456789' for name in (
    'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'OPENROUTER_API_KEY', 'XAI_API_KEY',
    'CLAUDE_ACCESS_TOKEN', 'GEMINI_API_KEY', 'VERTEX_ACCESS_TOKEN',
)}
MODELS = {
    'openai-chatgpt': 'gpt-6-astra', 'openai': 'gpt-6-astra',
    'anthropic': 'claude-opus-5', 'claude-subscription': 'claude-opus-5',
    'openrouter': 'openai/gpt-5.6-sol', 'xai': 'grok-4.7',
    'google': 'gemini-4-carbon', 'google-vertex': 'gemini-4-carbon',
}


def interrupt(_signum, _frame):
    raise KeyboardInterrupt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sudo', action='store_true')
    parser.add_argument('--image', help='Use this prebuilt local gateway image without pulling.')
    parser.add_argument('--bind-owner', default=f'{os.getuid()}:{os.getgid()}',
                        help='UID:GID that Docker assigns to the shared fixture directory.')
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, interrupt)
    docker = (['sudo', '-n'] if args.sudo else []) + ['docker']
    tag = 'gateway-isolation-' + uuid.uuid4().hex[:12]
    image = args.image or tag
    names = [tag + '-mock', tag + '-gateway', tag + '-uid-probe']

    def run(*cmd, timeout=90, **kwargs):
        return subprocess.run([*docker, *cmd], check=True, text=True, timeout=timeout, **kwargs)

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
        credentials = root / 'credentials.json'
        credentials.write_text(json.dumps({
            **SECRETS, 'CLAUDE_ACCESS_TOKEN_EXPIRES_AT': '2099-01-01T00:00:00Z',
            'VERTEX_ACCESS_TOKEN_EXPIRES_AT': '2099-01-01T00:00:00Z', 'VERTEX_PROJECT_ID': 'sample-project',
        })); credentials.chmod(0o600)
        # Fixture-only trusted code replaces destinations before gateway import.
        # Production has no environment switch for arbitrary provider URLs.
        gateway_fixture = root / 'gateway_fixture.py'
        gateway_fixture.write_text(
            "from model_access import MODEL_ACCESS\n"
            f"for name in {tuple(MODELS)!r}:\n"
            "    MODEL_ACCESS[name]['upstream_default'] = 'http://mock:8081/v1'\n"
            "import runpy\nrunpy.run_path('/app/gateway.py', run_name='__main__')\n")
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
  request=json.loads(self.rfile.read(int(self.headers.get('content-length','0'))))
  access=(self.headers.get('authorization','').removeprefix('Bearer ')
          or self.headers.get('x-api-key') or self.headers.get('x-goog-api-key'))
  assert access in [SECRET,*SECRETS.values()]
  if request.get('input')=='cut-stream':
   content=b'data: {"type":"response.output_text.delta","delta":"partial"}\\n\\n'
   self.send_response(200)
   self.send_header('Content-Type','text/event-stream')
   self.send_header('Content-Length',str(len(content)+100))
   self.end_headers(); self.wfile.write(content)
   return
  echo=SECRET+' '+ID_TOKEN+' '+ACCOUNT if access==SECRET else access
  if access == SECRETS['OPENROUTER_API_KEY']:
   reply={'id':'gen-fixture','choices':[{'message':{'role':'assistant','content':echo}}],
          'usage':{'prompt_tokens':100,'completion_tokens':10,'cost':0.0001}}
  elif 'generateContent' in self.path:
   if access == SECRETS['VERTEX_ACCESS_TOKEN']:
    assert '/projects/sample-project/locations/global/publishers/google/' in self.path
   else:
    assert access == SECRETS['GEMINI_API_KEY']
   reply={'candidates':[{'content':{'role':'model','parts':[{'text':echo}]},'finishReason':'STOP'}],
          'usageMetadata':{'promptTokenCount':100,'candidatesTokenCount':10,'totalTokenCount':110}}
  elif self.path.endswith('/messages'):
   reply={'id':'msg_fixture','type':'message','role':'assistant',
          'content':[{'type':'text','text':echo}],'stop_reason':'end_turn','stop_sequence':None,
          'usage':{'input_tokens':100,'output_tokens':10}}
  else:
   reply={'id':'resp_fixture','object':'response','status':'completed',
          'output':[{'type':'message','role':'assistant','content':[{'type':'output_text','text':echo}]}],
          'usage':{'input_tokens':100,'output_tokens':10}}
  body=json.dumps(reply).encode()
  self.send_response(200); self.send_header('Content-Type','application/json')
  self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
threading.Thread(target=ThreadingHTTPServer(('0.0.0.0',8091),Handler).serve_forever,daemon=True).start()
ThreadingHTTPServer(('0.0.0.0',8081),Handler).serve_forever()
''')
        task={'schema_version':1,'attachments':[{'name':'fixture.bin','bytes':2*1024*1024,
              'sha256':hashlib.sha256(b'x'*(2*1024*1024)).hexdigest(),'media_type':'application/octet-stream'}]}
        mock.write_text('SECRETS='+repr(SECRETS)+'\nTASK='+repr(task)+'\n'+'SECRET='+repr(SECRET)+'\nID_TOKEN='+repr(ID_TOKEN)+'\nACCOUNT='+repr(ACCOUNT)+'\n'+mock.read_text())
        try:
            if args.image:
                run('image', 'inspect', image, stdout=subprocess.DEVNULL)
            else:
                run('build', '-q', '-t', image, str(ROOT / 'services/gateway'), timeout=None)
            run('network', 'create', '--internal', tag, stdout=subprocess.DEVNULL)
            run('run', '--pull=never', '-d', '--name', names[0], '--network', tag, '--network-alias', 'mock', '--network-alias', 'problem',
                *hardening, '--mount', f'type=bind,src={mock},dst=/mock.py,readonly',
                image, 'python', '/mock.py', stdout=subprocess.DEVNULL)
            env = {'TESTBED_RUN_ID': 'synthetic-isolation', 'TESTBED_USAGE_DIR':'/var/lib/testbed/usage',
                   'MAX_SEARCHES':'0','MAX_FETCHES':'0','MAX_MODEL_REQUESTS':'10',
                   'MAX_MODEL_TOKENS':'10000','MAX_MODEL_USD':'1',
                   'DUNGENESS_TASK_SHA256':hashlib.sha256(json.dumps(task,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                   'DUNGENESS_REQUIRE_MODEL_ALLOWLIST':'1',
                   'DUNGENESS_ALLOWED_MODELS':json.dumps(list(MODELS.items())),
                   'DUNGENESS_OPENROUTER_INFERENCE_ONLY':'1',
                   'DUNGENESS_CREDENTIALS_FILE':'/run/dungeness/credentials.json',
                   'DUNGENESS_CHATGPT_AUTH_FILE':'/run/dungeness/auth.json'}
            command = ['run','--pull=never','-d','--name',names[1],'--network',tag,*hardening,
                       '--user',args.bind_owner,
                       '--mount',f'type=bind,src={usage},dst=/var/lib/testbed/usage',
                       '--mount',f'type=bind,src={auth},dst=/run/dungeness/auth.json,readonly',
                       '--mount',f'type=bind,src={gateway_fixture},dst=/app/gateway_fixture.py,readonly',
                       '--mount',f'type=bind,src={credentials},dst=/run/dungeness/credentials.json,readonly']
            for key,value in env.items(): command += ['-e',key+'='+value]
            run(*command,image,'python','/app/gateway_fixture.py',stdout=subprocess.DEVNULL)
            inspection=json.loads(run('inspect',names[1],capture_output=True).stdout)[0]
            config_env=json.dumps(inspection['Config']['Env'])
            for value in (SECRET,ID_TOKEN,ACCOUNT,*SECRETS.values()): assert value not in config_env
            for name in SECRETS: assert not any(v.startswith(name+'=') for v in inspection['Config']['Env'])
            # Query from inside the container, avoiding any public port exposure.
            request_code = '''import json,urllib.request
r=urllib.request.Request('http://localhost:8080/model/chatgpt/v1/responses',
 data=json.dumps({'model':'gpt-6-astra','input':'synthetic fixture','stream':False}).encode(),
 headers={'Content-Type':'application/json'})
body=urllib.request.urlopen(r).read().decode()
assert body.count('[REDACTED]')==3,body
for route,model in [('openai/v1/responses','gpt-6-astra'),
                    ('anthropic/v1/messages','claude-opus-5'),
                    ('claude-subscription/v1/messages','claude-opus-5'),
                    ('xai/v1/responses','grok-4.7'),
                    ('openrouter/v1/chat/completions','openai/gpt-5.6-sol')]:
 payload={'model':model,'stream':False}
 if route.endswith('/responses'): payload.update(input='fixture',max_output_tokens=10)
 else: payload.update(messages=[{'role':'user','content':'fixture'}],max_tokens=10)
 r=urllib.request.Request('http://localhost:8080/model/'+route,
  data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 try: body=urllib.request.urlopen(r).read().decode()
 except urllib.error.HTTPError as error: raise AssertionError(route+': '+error.read().decode()) from error
 assert body.count('[REDACTED]')==1,body
for route in ('google','google-vertex'):
 r=urllib.request.Request('http://localhost:8080/model/'+route+'/v1beta/models/gemini-4-carbon:generateContent',
  data=json.dumps({'contents':[{'role':'user','parts':[{'text':'fixture'}]}],
                   'generationConfig':{'maxOutputTokens':32}}).encode(),
  headers={'Content-Type':'application/json'})
 try: body=urllib.request.urlopen(r).read().decode()
 except urllib.error.HTTPError as error: raise AssertionError(route+': '+error.read().decode()) from error
 assert body.count('[REDACTED]')==1,body
from pathlib import Path
summary=Path('/var/lib/testbed/usage/summary.json')
usage=json.loads(summary.read_text())['usage']
assert usage['model_accounting_state']=='settled' and usage['model_requests']==8
assert usage['normalized_usd']>0
assert urllib.request.urlopen('http://localhost:8080/task/files/fixture.bin').read()==b'x'*(2*1024*1024)
for route in ('search','fetch'):
 r=urllib.request.Request('http://localhost:8080/web/'+route,data=b'{}',headers={'Content-Type':'application/json'})
 try: urllib.request.urlopen(r)
 except urllib.error.HTTPError as error:
  assert error.code==410
  assert json.loads(error.read())['error']['code']=='external_web_disabled'
 else: raise AssertionError('External web access was not disabled')
payload={'model':'gpt-6-astra','input':'cut-stream','stream':True,'max_output_tokens':10}
r=urllib.request.Request('http://localhost:8080/model/openai/v1/responses',
 data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
body=urllib.request.urlopen(r).read()
assert b'partial' in body and b'response.completed' not in body
usage=json.loads(summary.read_text())['usage']
assert usage['model_accounting_state']=='incomplete', 'VERIFY: cut stream left accounting unsettled'
assert usage['model_requests']==9
try:
 with urllib.request.urlopen(r): pass
except urllib.error.HTTPError as error:
 assert json.loads(error.read())['code']=='model_accounting_incomplete'
else: raise AssertionError('VERIFY: replay after ambiguous dispatch reached inference')
assert json.loads(summary.read_text())['usage']['model_requests']==9
print('Inference, accounting and a resource download that spills to temporary disk work; credentials redacted.')
'''
            for attempt in range(60):
                probe = subprocess.run([*docker,'exec',names[1],'python','-c',
                    "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')"],
                    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
                if probe.returncode == 0: break
                time.sleep(1)
            else:
                subprocess.run([*docker, 'logs', names[1]], timeout=15, check=False)
                raise RuntimeError('Gateway failed to become healthy')
            run('exec',names[1],'python','-c',request_code)
            run('exec',names[1],'python','-c','''from pathlib import Path
import errno
try: Path('/app/should-not-write').write_text('no')
except OSError as e: assert e.errno in (errno.EROFS,errno.EACCES)
else: raise AssertionError('Gateway root is writable')
Path('/tmp/probe').write_text('temporary workspace works')
s=Path('/proc/self/status').read_text()
assert 'NoNewPrivs:\\t1' in s and 'CapEff:\\t0000000000000000' in s
for name in ('auth.json','credentials.json'):
 try: Path('/run/dungeness',name).write_text('no')
 except OSError: pass
 else: raise AssertionError('Credential mount is writable')
print('Root and credential mount read-only; temporary writes work; no capabilities or privilege escalation.')
''')
            assert (usage/'events.jsonl').is_file() and (usage/'summary.json').is_file()
            assert usage.stat().st_mode & 0o777 == 0o700
            for filename in ('.event-token', 'events.jsonl', 'summary.json'):
                assert (usage/filename).stat().st_mode & 0o777 == 0o600
            # Even an accidental read-only mount does not make accounting
            # readable by a different, unprivileged candidate UID.
            denied_uid = 10002 if args.bind_owner.split(':')[0] == '10001' else 10001
            run('run', '--pull=never', '--rm', '--name', names[2], '--network', 'none',
                '--user', f'{denied_uid}:{denied_uid}',
                *hardening, '--mount', f'type=bind,src={usage},dst=/usage,readonly',
                '--mount', f'type=bind,src={credentials},dst=/credentials.json,readonly',
                image, 'python', '-c', '''from pathlib import Path
for name in ('/usage/.event-token', '/usage/events.jsonl', '/usage/summary.json', '/credentials.json'):
 try: Path(name).read_bytes()
 except PermissionError: pass
 else: raise AssertionError('Untrusted UID read accounting data')
print('Untrusted UID cannot read event token, ledger, summary or provider credential file.')
''')
            for path in usage.rglob('*'):
                if path.is_file():
                    raw=path.read_bytes()
                    for value in (SECRET,ID_TOKEN,ACCOUNT,*SECRETS.values()): assert value.encode() not in raw
            logs=run('logs',names[1],capture_output=True)
            for value in (SECRET,ID_TOKEN,ACCOUNT,*SECRETS.values()): assert value not in logs.stdout+logs.stderr
            print('PASS: Eight synthetic routes and interrupted-stream accounting; private credentials absent from Docker environment, logs and accounting.')
        finally:
            cleanup = [('rm', '-f', name) for name in names]
            cleanup.append(('network', 'rm', tag))
            if not args.image:
                cleanup.append(('image', 'rm', '--no-prune', image))
            errors = []
            for arguments in cleanup:
                try:
                    result = subprocess.run([*docker, *arguments], text=True, capture_output=True, timeout=30)
                    if result.returncode and 'No such' not in result.stderr and 'not found' not in result.stderr:
                        errors.append(result.stderr.strip())
                except (OSError, subprocess.TimeoutExpired) as error:
                    errors.append(str(error))
            for error in errors:
                print(f'Docker cleanup failed: {error}', file=sys.stderr)
            if errors and sys.exc_info()[0] is None:
                raise RuntimeError('Gateway isolation cleanup failed.')



if __name__ == '__main__':
    main()
