"""Structural diagnostics must locate failures without copying submitted data."""
import copy
import json
import unittest

from gateway_request_policy import HistoryPolicyError, validate_model_request
from test_request_policy import harness, request_body, route

SECRET = 'synthetic-private-token-do-not-retain'


class ShapeDiagnosticsTests(unittest.TestCase):
    def reject(self, provider, operation, history, path, rule, **expected):
        payload = {**request_body(provider, operation), **history}
        original = copy.deepcopy(payload)
        with self.assertRaises(HistoryPolicyError) as caught:
            validate_model_request(provider, operation, payload)
        details = caught.exception.diagnostic
        self.assertEqual(details['path'], path)
        self.assertEqual(details['validation_rule'], rule)
        self.assertEqual(details['diagnostics_version'], 1)
        self.assertEqual(details['provider'], provider)
        self.assertEqual(details['operation'], operation)
        for key, value in expected.items():
            self.assertEqual(details[key], value)
        self.assertNotIn(SECRET, json.dumps(details) + str(caught.exception))
        self.assertEqual(payload, original)
        return details

    def test_responses_nested_locations_and_private_keys(self):
        cases = [
            ({'role':'user', 'content':[{'type':'input_image','image_url':SECRET}]},
             'input[1].content[0].type', 'unsupported_content_type'),
            ({'type':'custom_tool_call_output','call_id':SECRET,'output':[{'type':'text','text':SECRET,SECRET:SECRET}]},
             'input[1].output[0]', 'unknown_field'),
            ({'type':SECRET, SECRET:SECRET}, 'input[1].type', 'unsupported_item_type'),
            ({'role':SECRET,'content':SECRET}, 'input[1].role', 'unsupported_role'),
            ({'type':'shell_call_output','output':[{'stdout':SECRET,'outcome':{'type':SECRET}}]},
             'input[1].output[0].outcome', 'unsupported_shell_outcome'),
            ({'type':'shell_call_output','output':[{'outcome':SECRET}]},
             'input[1].output[0].outcome', 'expected_object'),
            ({'type':'tool_search_output','execution':'client','tools':[{'type':'namespace','tools':[{'type':SECRET}]}]},
             'input[1].tools[0].tools[0].type', 'unsupported_tool_type'),
            ({'type':'reasoning','summary':[{'type':'summary_text','text':SECRET},SECRET]},
             'input[1].summary[1]', 'invalid_history_field'),
        ]
        for item, path, rule in cases:
            with self.subTest(path=path, rule=rule):
                self.reject('openrouter','responses', {'input':[{'role':'user','content':SECRET},item]},
                            path, rule, item_index=1)

    def test_nested_messages_and_system(self):
        content = [{'type':'tool_result','tool_use_id':SECRET,'content':[
            {'type':'text','text':SECRET}, {'type':SECRET, 'data':SECRET}]}]
        self.reject('anthropic','messages',{'messages':[{'role':'user','content':content}]},
                    'messages[0].content[0].content[1].type', 'unsupported_content_type',
                    block_index=1, block_type='other', item_type='message')
        self.reject('anthropic','messages',{'system':content},
                    'system[0].content[1].type','unsupported_content_type', location='system')
        self.reject('openrouter','chat/completions',{'messages':[
            {'role':'assistant','tool_calls':[{'type':'function','function':SECRET}]}]},
            'messages[0].tool_calls[0].function','expected_object',actual_type='string',expected_type='object')
        self.reject('openrouter','chat/completions',{'messages':[
            {'role':'assistant','reasoning_details':[{'type':'reasoning.text','text':SECRET,'format':{SECRET:SECRET}}]}]},
            'messages[0].reasoning_details[0].format','invalid_history_field')

    def test_unknown_type_values_never_echo_and_text_is_unchanged(self):
        for value in (SECRET, {SECRET: SECRET}, [SECRET], None):
            self.reject('openrouter','responses',{'input':[{'role':'user','content':[{'type':value}]}]},
                'input[0].content[0].type','unsupported_content_type',block_type='other')
        payload = {**request_body('openrouter','responses'),'input':[
            {'type':'custom_tool_call_output','call_id':SECRET,'output':'A'*9448},
            {'type':'reasoning','signature':SECRET,'encrypted_content':SECRET,
             'format':'openai-responses-v1','summary':[]}]}
        before = copy.deepcopy(payload)
        validate_model_request('openrouter','responses',payload)
        self.assertEqual(payload,before)


class RejectionRetentionTests(unittest.IsolatedAsyncioTestCase):
    async def test_private_diagnostic_survives_http_and_event_without_raw_history(self):
        async with harness() as (client, runtime, calls):
            body = {**request_body('openrouter','responses'), 'input':[
                {'role':'user','content':SECRET},
                {'role':'assistant','content':[{'type':'text','text':SECRET,SECRET:SECRET}]}]}
            before = copy.deepcopy(runtime.ledger.counts)
            response = await client.post(route('openrouter','responses'),json=body)
            self.assertEqual(response.status_code,400)
            details = response.json()['diagnostic']
            self.assertEqual(details['path'],'input[1].content[0]')
            self.assertEqual(details['validation_rule'],'unknown_field')
            self.assertFalse(details['upstream_request_sent'])
            self.assertFalse(details['retryable'])
            self.assertEqual(details['run_action'],'continue')
            self.assertEqual(calls,[])
            self.assertEqual(runtime.ledger.counts,before)
            events_text = (runtime.ledger.directory/'events.jsonl').read_text()
            self.assertNotIn(SECRET,response.text + events_text)
            events = [json.loads(line) for line in events_text.splitlines()]
            rejection = next(e for e in events if e['kind']=='gateway.model_request_rejected')
            self.assertEqual(rejection['data']['path'],details['path'])
            self.assertEqual(rejection['data']['validation_rule'],details['validation_rule'])
            self.assertFalse(any(e['kind']=='model.request' for e in events))
