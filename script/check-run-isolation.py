#!/usr/bin/env python3
"""Probe two concurrent generated run topologies, using only synthetic services.

Requires local Linux Docker, Docker Compose and the gateway dependency group.
No model credentials, existing services, metadata endpoints or paid APIs are used.
--baseline proves the old internal bridge can reach a synthetic host listener.
"""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import uuid

import yaml
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from dungeness.compiler import build_compose

SERVER = '''from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json,os,socket
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  body=TASK if self.path=='/task' else (b'public-fixture' if self.path=='/task/files/paper.txt' else RUN.encode())
  self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_POST(self):
  self.rfile.read(int(self.headers.get('Content-Length','0')))
  if PORT==8081: assert self.headers.get('authorization')=='Bearer '+CANARY
  body=json.dumps({'run':RUN,'output_text':'synthetic result','usage':{'input_tokens':100,'output_tokens':10}}).encode()
  self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
class Server(ThreadingHTTPServer):
 address_family=socket.AF_INET6
 def server_bind(self):
  self.socket.setsockopt(socket.IPPROTO_IPV6,socket.IPV6_V6ONLY,0)
  super().server_bind()
Server(('::',PORT),Handler).serve_forever()
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', action='store_true')
    parser.add_argument('--ipv6', action='store_true', help='Also exercise dual-stack bridges.')
    args = parser.parse_args()
    prefix = 'run-isolation-' + uuid.uuid4().hex[:10]
    image = prefix + ':test'
    projects = []
    def docker(*cmd, **kwargs):
        try:
            return subprocess.run(['docker', *cmd], check=True, text=True, capture_output=True,
                                  timeout=300, **kwargs).stdout
        except subprocess.CalledProcessError as error:
            print(error.stderr, file=sys.stderr)
            raise
    def inspect(cid):
        return json.loads(docker('inspect', cid))[0]
    class Canary(BaseHTTPRequestHandler):
        def log_message(self, *_):pass
        def do_GET(self):
            self.send_response(200);self.end_headers();self.wfile.write(b'host-canary')
    server = ThreadingHTTPServer(('0.0.0.0', 0), Canary)
    thread = threading.Thread(target=server.serve_forever, daemon=True);thread.start()
    ipv6_server = None
    if args.ipv6:
        class IPv6Canary(ThreadingHTTPServer):
            address_family = socket.AF_INET6
            def server_bind(self):
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                super().server_bind()
        ipv6_server = IPv6Canary(('::', server.server_port), Canary)
        threading.Thread(target=ipv6_server.serve_forever, daemon=True).start()
    temporary = tempfile.TemporaryDirectory(prefix=prefix)
    try:
        tmp = temporary.name
        root = Path(tmp)
        docker('build', '-q', '-t', image, str(ROOT/'services/gateway'))
        runs = []
        for suffix in ('a', 'b'):
            run = prefix + '-' + suffix
            folder = root/suffix;folder.mkdir()
            usage = folder/'usage';usage.mkdir()
            # Public synthetic marker; no real credential is read by this test.
            canary = 'synthetic-fixture-' + run
            credential = folder/'credentials.json'
            credential.write_text(json.dumps({'OPENAI_API_KEY':canary}));credential.chmod(0o600)
            task = json.dumps({'schema_version':1, 'attachments':[{'name':'paper.txt',
                'bytes':14,'sha256':hashlib.sha256(b'public-fixture').hexdigest(),
                'media_type':'text/plain'}]},sort_keys=True,separators=(',',':')).encode()
            doc = yaml.safe_load(build_compose(run, {}, {'model':{'requests':10,'total_tokens':10000}},
                run_dir=folder, max_usd=1,
                dev_scorer={'port':8090,'context':'scorer','submissions':10},
                problem_service={'context':'problem','sha256':hashlib.sha256(task).hexdigest()},
                command_policy={'models':[{'provider':'openai','request_model':'gpt-6-astra',
                    'base_url':'http://gateway:8080/model/openai/v1'}]}))
            doc['services']['main'].update(image=image,command=['python','-c',
                f'RUN={run!r}\nPORT=8092\nTASK=b""\nCANARY=None\n'+SERVER])
            gateway = doc['services']['gateway'];gateway.pop('build');gateway['image']=image
            gateway['environment']['OPENAI_UPSTREAM_BASE_URL']='http://provider:8081/v1'
            gateway['volumes'][-1]['source']=str(credential)
            # Replace only trusted task/scorer/provider implementations with fixtures.
            for name,port in (('problem',8091),('dev-scorer',8090),('provider',8081)):
                service=doc['services'].setdefault(name,{'networks':['external_egress']})
                service.pop('build',None)
                fixture=folder/(name+'.py')
                fixture.write_text(f'RUN={run!r}\nPORT={port}\nCANARY={canary!r}\nTASK={task!r}\n'+SERVER)
                # Provider canary is not present in the problem/scorer fixture.
                if name!='provider':fixture.write_text(f'RUN={run!r}\nPORT={port}\nCANARY=None\nTASK={task!r}\n'+SERVER)
                service.update(image=image,command=['python','/fixture.py'],volumes=[str(fixture)+':/fixture.py:ro'])
            if args.ipv6:
                for net in doc['networks'].values():net['enable_ipv6']=True
            if args.baseline:
                for net in doc['networks'].values():net.pop('driver_opts',None)
            path=folder/'compose.yaml';path.write_text(yaml.safe_dump(doc,sort_keys=False))
            compose=['compose','-p',run,'-f',str(path)]
            projects.append(compose)
            docker(*compose,'up','-d','--wait','--wait-timeout','90')
            containers={name:inspect(docker(*compose,'ps','-q',name).strip()) for name in doc['services']}
            networks={name:json.loads(docker('network','inspect',run+'_'+name))[0] for name in doc['networks']}
            runs.append((run,containers,networks,canary))
        for run,containers,networks,canary in runs:
            main=containers['main']
            others=next(c for r,c,_,_ in runs if r!=run)
            addresses=[(f'other-{name}',net['IPAddress'],port) for name,port in
                       [('main',8092),('gateway',8080),('problem',8091),('dev-scorer',8090)]
                       for net in others[name]['NetworkSettings']['Networks'].values()]
            own_problem=next(iter(containers['problem']['NetworkSettings']['Networks'].values()))['IPAddress']
            own_provider=next(iter(containers['provider']['NetworkSettings']['Networks'].values()))['IPAddress']
            addresses += [('direct-problem',own_problem,8091),('direct-provider',own_provider,8081)]
            addresses += [('other-dns',other['Name'].lstrip('/'),port) for name,port in
                [('main',8092),('gateway',8080),('problem',8091),('dev-scorer',8090)] for other in [others[name]]]
            bridge = str(ipaddress.ip_network(networks['agent_internal']['IPAM']['Config'][0]['Subnet']).network_address+1)
            host_ips={str(ipaddress.ip_network(n['IPAM']['Config'][0]['Subnet']).network_address+1)
                      for _,_,ns,_ in runs for n in ns.values()}
            if args.ipv6:
                addresses += [(f'other-v6-{name}',net['GlobalIPv6Address'],port)
                    for name,port in [('main',8092),('gateway',8080),('problem',8091),('dev-scorer',8090)]
                    for net in others[name]['NetworkSettings']['Networks'].values() if net['GlobalIPv6Address']]
                host_ips.update(str(ipaddress.ip_network(pool['Subnet']).network_address+1)
                    for _,_,ns,_ in runs for n in ns.values() for pool in n['IPAM']['Config'])
            addresses += [('host',ip,server.server_port) for ip in sorted(host_ips)]
            probe='''import json,socket,urllib.request,urllib.error,os
from pathlib import Path
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(url):return opener.open(url,timeout=3).read()
assert get('http://127.0.0.1:8092/healthz').decode()==RUN
assert get('http://[::1]:8092/healthz').decode()==RUN
assert get('http://gateway:8080/healthz')
assert get('http://gateway:8080/task/files/paper.txt')==b'public-fixture'
assert get('http://dev-scorer:8090/healthz').decode()==RUN
r=urllib.request.Request('http://gateway:8080/model/openai/v1/responses',data=json.dumps({'model':'gpt-6-astra','input':'synthetic','max_output_tokens':10}).encode(),headers={'Content-Type':'application/json'})
assert json.load(opener.open(r,timeout=10))['run']==RUN
r=urllib.request.Request('http://gateway:8080/internal/events',data=b'{}',headers={'Content-Type':'application/json'})
try:opener.open(r,timeout=3)
except urllib.error.HTTPError as error:assert error.code==403
else:raise AssertionError('Unauthenticated accounting accepted')
for label,host,port in TARGETS:
 try:s=socket.create_connection((host,port),timeout=.4)
 except OSError:continue
 else:s.close();raise AssertionError(f'Unexpected reachability: {label} {host}:{port}')
for name in ('/run/docker.sock','/var/run/docker.sock','/run/dungeness/credentials.json','/var/lib/testbed/usage/.event-token'):
 assert not Path(name).exists(),name
for canary in CANARIES:assert canary not in json.dumps(dict(os.environ))
if not BASELINE:
 for family,kind,proto in ((socket.AF_PACKET,socket.SOCK_RAW,0),(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_RAW)):
  try:s=socket.socket(family,kind,proto)
  except PermissionError:pass
  else:s.close();raise AssertionError('Raw socket allowed')
 assert 'NoNewPrivs:\\t1' in Path('/proc/self/status').read_text()
print(RUN+': own inference/papers/scorer work; host, other runs, private mounts and raw sockets blocked')
'''
            if args.baseline:
                code=f"import urllib.request; assert urllib.request.urlopen('http://{bridge}:{server.server_port}',timeout=3).read()==b'host-canary';print('CONFIRMED: ordinary internal bridge reaches synthetic host service')"
                print(docker('exec',main['Id'],'python','-c',code),end='')
            else:
                code=f'RUN={run!r}\nTARGETS={addresses!r}\nCANARIES={[s for _,_,_,s in runs]!r}\nBASELINE=False\n'+probe
                print(docker('exec','-i',main['Id'],'python','-',input=code),end='')
                for name,network in networks.items():
                    if name=='external_egress':continue
                    assert network['Internal'] is True
                    assert network['Options']['com.docker.network.bridge.gateway_mode_ipv4']=='isolated'
                    assert network['Options']['com.docker.network.bridge.gateway_mode_ipv6']=='isolated'
                print(docker('exec',containers['gateway']['Id'],'python','-c',
                    "from pathlib import Path; assert Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'; assert Path('/proc/sys/net/ipv6/conf/all/forwarding').read_text().strip()=='0'; print('Gateway kernel forwarding disabled')"),end='')
            assert not main['HostConfig']['Privileged']
            assert set(main['NetworkSettings']['Networks'])=={run+'_agent_internal'}
            for service in containers.values():assert not service['HostConfig'].get('PortBindings')
        print('PASS: two simultaneous generated run topologies; no paid inference')
    finally:
        for compose in reversed(projects):
            subprocess.run(['docker',*compose,'down','--timeout','1','--volumes','--remove-orphans'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        subprocess.run(['docker','image','rm',image],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if ipv6_server:ipv6_server.shutdown();ipv6_server.server_close()
        temporary.cleanup()
        server.shutdown();server.server_close();thread.join(timeout=2)


if __name__=='__main__':main()
