import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import httpx
import test_gateway
import gateway
import gateway_pricing
from gateway_runtime import Gateway


class ClaudeSubscriptionTests(unittest.IsolatedAsyncioTestCase):
    async def test_stream_bearer_auth_cache_accounting_and_expiry_without_key_fallback(self):
        reference={'provider':'claude-subscription','upstream_id':'anthropic/claude-test',
                   'request_models':['claude-test'],'input_per_mtok':5,'output_per_mtok':25,
                   'cached_read_per_mtok':.5,'cache_write_per_mtok':6.25}
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ,{
                'TESTBED_USAGE_DIR':tmp,'DUNGENESS_ALLOWED_MODELS':'[["claude-subscription","claude-test"]]',
                'MAX_MODEL_REQUESTS':'20','MAX_MODEL_TOKENS':'100000','MAX_MODEL_USD':'1',
                'DUNGENESS_CREDENTIALS_FILE':str(Path(tmp)/'credentials.json'),
                'ANTHROPIC_API_KEY':'must-not-fallback'}), patch.object(gateway_pricing,'MODEL_PRICING',[reference]):
            file=Path(tmp)/'credentials.json'
            values={'CLAUDE_ACCESS_TOKEN':'synthetic-private-claude',
                    'CLAUDE_ACCESS_TOKEN_EXPIRES_AT':'2030-01-01T00:00:00Z'}
            file.write_text(json.dumps(values));file.chmod(0o600)
            runtime=Gateway();await runtime.client.aclose();calls=[]
            payload={'model':'claude-test','max_tokens':20,'stream':True,
                     'messages':[{'role':'user','content':'synthetic mechanics fixture'}]}
            def upstream(request):
                calls.append(request)
                self.assertEqual(str(request.url),'https://api.anthropic.com/v1/messages')
                self.assertEqual(request.headers['authorization'],'Bearer synthetic-private-claude')
                self.assertNotIn('x-api-key',request.headers)
                self.assertEqual(request.headers['anthropic-version'],'2023-06-01')
                self.assertEqual(json.loads(request.content),payload)
                self.assertNotIn('claude-cli',request.headers.get('user-agent',''))
                class Stream(httpx.AsyncByteStream):
                    async def __aiter__(self):
                        yield b'event: message_start\ndata: {"type":"message_start","message":{"usage":{"input_tokens":100,"output_tokens":0,"cache_read_input_tokens":20,"cache_creation_input_tokens":10}}}\n\n'
                        yield b'event: message_delta\ndata: {"type":"message_delta","usage":{"output_tokens":5}}\n\n'
                        yield b'event: message_stop\ndata: {"type":"message_stop"}\n\n'
                return httpx.Response(200,stream=Stream(),headers={'content-type':'text/event-stream'})
            runtime.client=httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            try:
                with patch.object(gateway,'gateway',runtime):
                    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway.app),base_url='http://gateway') as client:
                        result=await client.post('/model/claude-subscription/v1/messages',json=payload)
                        self.assertEqual(result.status_code,200,result.text)
                        values['CLAUDE_ACCESS_TOKEN_EXPIRES_AT']='2000-01-01T00:00:00Z'
                        file.write_text(json.dumps(values))
                        result=await client.post('/model/claude-subscription/v1/messages',json=payload)
                        self.assertEqual(result.status_code,400,result.text)
                        self.assertEqual(len(calls),1)
                        result=await client.post('/model/claude-subscription/v1/oauth/token',json={})
                        self.assertEqual(result.status_code,404)
                events=(Path(tmp)/'events.jsonl').read_text()
                self.assertNotIn('synthetic-private-claude',events)
                receipts=[e['data'] for e in map(json.loads,events.splitlines()) if e['kind']=='model.accounting']
                self.assertEqual(len(receipts),1)
                self.assertGreater(receipts[0]['normalized_usd'],0)
                self.assertEqual(receipts[0]['cached_input_tokens'],20)
                self.assertEqual(receipts[0]['cache_write_input_tokens'],10)
                self.assertIsNone(receipts[0].get('billed_usd'))
            finally:
                await runtime.client.aclose()
