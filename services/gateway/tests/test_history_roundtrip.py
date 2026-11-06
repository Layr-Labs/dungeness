"""Offline provider-output -> next-request checks against the actual gateway app."""
import copy
import json
import unittest

import httpx
from test_request_policy import harness, request_body, route
from gateway_request_policy import validate_model_request, validate_model_transport, MAX_MODEL_REQUEST_BYTES


REASONING = {'type': 'reasoning', 'id': 'rs_synthetic', 'status': 'completed',
    'format': 'openai-responses-v1', 'signature': 'signed-opaque-α==',
    'encrypted_content': 'opaque-encoded==', 'summary': [],
    'content': [{'type': 'reasoning_text', 'text': 'synthetic reasoning'}]}
OUTPUT = [REASONING,
    {**REASONING, 'id': 'rs_second', 'format': 'future-provider-v2', 'signature': None, 'content': None},
    {'type': 'message', 'role': 'assistant', 'content': [{'type': 'refusal', 'refusal': 'synthetic refusal'}]},
    {'type': 'function_call', 'call_id': 'call_test', 'name': 'evaluate', 'arguments': '{}'}]
USAGE = {'input_tokens': 2, 'output_tokens': 1, 'total_tokens': 3, 'cost': 0.00001}


class Fragments(httpx.AsyncByteStream):
    def __init__(self, body, interrupted=False):
        self.body, self.interrupted = body, interrupted

    async def __aiter__(self):
        for i in range(0, len(self.body), 7):
            yield self.body[i:i+7]
        if self.interrupted:
            raise httpx.ReadError('synthetic interruption')


def stream_body(items, *, complete=True):
    events = [{'type': 'response.output_item.done', 'output_index': i, 'item': item}
              for i, item in enumerate(items)]
    if complete:
        # The final envelope need not repeat already-delivered output items.
        events.append({'type': 'response.completed', 'response': {
            'id': 'resp_test', 'status': 'completed', 'output': [], 'usage': USAGE}})
    else:
        events.append({'type': 'response.output_item.added', 'output_index': len(items),
                       'item': {**REASONING, 'id': 'incomplete', 'status': 'in_progress'}})
    return ''.join('event: '+e['type']+'\ndata: '+json.dumps(e, ensure_ascii=False)+'\n\n' for e in events).encode()


class HistoryRoundTripTests(unittest.IsolatedAsyncioTestCase):
    async def test_nonstreaming_and_fragmented_streaming_history_survive_two_turns(self):
        for streaming in (False, True):
            async with harness() as (client, runtime, _):
                captured = []
                body = stream_body(OUTPUT)
                def upstream(request):
                    captured.append(json.loads(request.content))
                    if streaming:
                        return httpx.Response(200, headers={'content-type': 'text/event-stream'}, stream=Fragments(body))
                    return httpx.Response(200, json={'id': 'resp_test', 'status': 'completed', 'output': OUTPUT, 'usage': USAGE})
                await runtime.client.aclose()
                runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
                payload = {**request_body('openrouter', 'responses'), 'stream': streaming}
                first = await client.post(route('openrouter', 'responses'), json=payload)
                self.assertEqual(first.status_code, 200, first.text)
                if streaming:
                    self.assertEqual(first.content, body)
                    events = [json.loads(line[6:]) for line in first.text.splitlines() if line.startswith('data: ')]
                    history = [e['item'] for e in events if e['type'] == 'response.output_item.done']
                    self.assertEqual(events[-1]['response']['output'], [])
                else:
                    history = first.json()['output']
                self.assertEqual(history, OUTPUT)
                history += [{'type': 'function_call_output', 'call_id': 'call_test', 'output': 'synthetic result'}]
                second = await client.post(route('openrouter', 'responses'), json={**payload, 'input': history})
                self.assertEqual(second.status_code, 200, second.text)
                self.assertEqual(captured[1]['input'], history)
                self.assertEqual(len(captured), 2)
                events = [json.loads(line) for line in (runtime.ledger.directory/'events.jsonl').read_text().splitlines()]
                self.assertEqual(sum(e['kind'] == 'model.accounting' for e in events), 2)
                # A later compatibility rejection cannot erase prior charges or candidate files.
                candidate = runtime.ledger.directory/'candidate.rs'; candidate.write_text('retained candidate')
                before = copy.deepcopy(runtime.ledger.counts)
                bad = copy.deepcopy(history); bad[0]['synthetic-secret-field-name'] = 'secret value'
                rejected = await client.post(route('openrouter', 'responses'), json={**payload, 'input': bad})
                self.assertEqual(rejected.status_code, 400)
                diagnostic = rejected.json()['diagnostic']
                self.assertEqual(diagnostic['code'], 'conversation_history_rejected')
                self.assertFalse(diagnostic['upstream_request_sent'])
                self.assertEqual(diagnostic['history_schema_version'], 1)
                self.assertEqual(diagnostic['item_index'], 0)
                self.assertTrue(diagnostic['request_id'])
                self.assertNotIn('secret', rejected.text)
                self.assertEqual(len(captured), 2)  # no paid retry
                self.assertEqual(runtime.ledger.counts, before)
                self.assertEqual(candidate.read_text(), 'retained candidate')
                last = [json.loads(l) for l in (runtime.ledger.directory/'events.jsonl').read_text().splitlines()
                        if 'gateway.model_request_rejected' in l][-1]
                self.assertNotIn('secret', json.dumps(last))
                self.assertEqual(last['data']['code'], diagnostic['code'])

    async def test_interrupted_stream_does_not_promote_partial_items_or_retry(self):
        async with harness() as (client, runtime, _):
            body = stream_body([REASONING], complete=False)
            calls = []
            def upstream(request):
                calls.append(request)
                return httpx.Response(200, headers={'content-type':'text/event-stream'}, stream=Fragments(body, True))
            await runtime.client.aclose()
            runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            result = await client.post(route('openrouter','responses'), json={**request_body('openrouter','responses'), 'stream':True})
            self.assertEqual(result.content, body)
            events = [json.loads(l[6:]) for l in result.text.splitlines() if l.startswith('data: ')]
            self.assertEqual([e['item']['id'] for e in events if e['type']=='response.output_item.done'], ['rs_synthetic'])
            self.assertEqual(events[-1]['item']['status'], 'in_progress')
            self.assertNotIn('response.completed', result.text)
            self.assertEqual(len(calls), 1)
            accounting = [json.loads(l) for l in (runtime.ledger.directory/'events.jsonl').read_text().splitlines()
                          if 'model.accounting' in l][-1]['data']
            self.assertEqual(accounting['status'], 'stream_interrupted')
            self.assertEqual(accounting['accounting_basis'], 'unavailable')

    async def test_metadata_cannot_enable_capabilities_or_bypass_budget(self):
        async with harness() as (client, runtime, calls):
            base = {**request_body('openrouter','responses'), 'input': [REASONING]}
            for extra in ({'model':'unauthorized/model'}, {'tools':[{'type':'web_search'}]},
                          {'plugins':[{'id':'web'}]}, {'previous_response_id':'hidden'},
                          {'input':[{'role':'user','content':[{'type':'input_image','image_url':'https://example.invalid'}]}]}):
                result = await client.post(route('openrouter','responses'), json={**base, **extra})
                self.assertEqual(result.status_code, 400, result.text)
            self.assertEqual(calls, [])
            runtime.ledger.counts['model_requests'] = 100
            result = await client.post(route('openrouter','responses'), json=base)
            self.assertIn(result.status_code, (400, 429), result.text)
            self.assertEqual(calls, [])


class HistorySchemaTests(unittest.TestCase):
    def test_route_specific_metadata_types_bounds_and_no_mutation(self):
        payload = {**request_body('openrouter','responses'), 'input':[REASONING]}
        before = copy.deepcopy(payload)
        validate_model_request('openrouter','responses',payload)
        self.assertEqual(payload, before)
        with self.assertRaises(ValueError): validate_model_request('openai','responses',payload)
        for field, value in [('format', {}), ('format','x'*129), ('signature',123), ('encrypted_content',[]), ('summary',{})]:
            bad = copy.deepcopy(payload); bad['input'][0][field] = value
            with self.assertRaises(ValueError): validate_model_request('openrouter','responses',bad)
        nested = {}; cursor = nested
        for _ in range(70): cursor['x'] = {}; cursor = cursor['x']
        with self.assertRaises(ValueError): validate_model_request('openrouter','responses',{**payload,'metadata':nested})
        with self.assertRaises(ValueError): validate_model_transport('responses','POST',[],b' '* (MAX_MODEL_REQUEST_BYTES+1))

    def test_native_thinking_and_chat_reasoning_remain_unchanged(self):
        payload = {**request_body('anthropic','messages'), 'messages':[
            {'role':'assistant','content':[{'type':'thinking','thinking':'synthetic','signature':'opaque=='}]},
            {'role':'user','content':'continue'}]}
        before = copy.deepcopy(payload)
        validate_model_request('anthropic','messages',payload)
        self.assertEqual(payload,before)
        chat = {**request_body('openrouter','chat/completions'), 'messages':[
            {'role':'assistant','content':None,'reasoning_details':[{'type':'reasoning.text','text':'synthetic','signature':'opaque==','format':'openai-responses-v1'}]},
            {'role':'user','content':'continue'}]}
        before = copy.deepcopy(chat)
        validate_model_request('openrouter','chat/completions',chat)
        self.assertEqual(chat,before)

    def test_chat_metadata_cannot_hide_server_tool_history(self):
        for item in ({'type':'openrouter:tool_call','id':'hidden'},
                     {'type':'reasoning.text','text':{'url':'https://example.invalid'}},
                     {'type':'reasoning.text','text':'synthetic','tools':[{'type':'web_search'}]}):
            payload = {**request_body('openrouter','chat/completions'), 'messages':[
                {'role':'assistant','content':None,'reasoning_details':[item]}]}
            with self.assertRaises(ValueError):
                validate_model_request('openrouter','chat/completions',payload)
