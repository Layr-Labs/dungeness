"""Completion must never overtake accounting; no provider calls in these tests."""
import asyncio
import json
import unittest
from unittest.mock import patch

import httpx
from starlette.requests import Request

import test_gateway
from test_request_policy import harness, request_body, route
from gateway_runtime import BACKGROUND_TASKS
from gateway_stream import CompletionBarrier


class FramingTests(unittest.TestCase):
    def test_terminal_frames_at_every_chunk_boundary_preserve_bytes(self):
        for operation, terminal in (
            ('responses', b'data: {"type":"response.completed","response":{"output":[]}}'),
            ('responses', b'event: response.incomplete\ndata: {}'),
            ('responses', b'data: {"type":"response.failed"}'),
            ('messages', b'event: message_stop\ndata: {"type":"message_stop"}'),
            ('chat/completions', b'data: {"choices":[{"finish_reason":"tool_calls"}]}'),
            ('completions', b'data: {"choices":[{"finish_reason":"stop"}]}'),
            ('responses', b'data: [DONE]'),
        ):
            for newline in (b'\n', b'\r\n', b'\r'):
                prefix = b'data: {"type":"response.output_item.done","text":"response.completed"}' + newline * 2
                suffix = terminal.replace(b'\n', newline) + newline * 2 + b'data: [DONE]' + newline * 2
                original = prefix + suffix
                for split in range(len(original) + 1):
                    with self.subTest(operation=operation, newline=newline, split=split):
                        barrier = CompletionBarrier(operation)
                        sent = barrier.feed(original[:split]) + barrier.feed(original[split:], final=True)
                        self.assertEqual(sent, prefix)
                        self.assertEqual(sent + barrier.settled(), original)

    def test_single_byte_fragments_multiline_data_and_missing_final_delimiter(self):
        prefix = b': keepalive\n\ndata: {"type":"response.output_text.delta","delta":"hello"}\n\n'
        terminal = b'data: {"type":\ndata: "response.completed"}'
        barrier = CompletionBarrier('responses')
        sent = b''.join(barrier.feed(bytes([c])) for c in prefix + terminal)
        sent += barrier.feed(b'', final=True)
        self.assertEqual(sent, prefix)
        self.assertEqual(sent + barrier.settled(), prefix + terminal)

    def test_nonterminal_and_unknown_frames_are_not_rewritten(self):
        original = b'data: {"type":"response.output_item.done","item":{"signature":"exact"}}\n\ndata: invalid\n\n'
        barrier = CompletionBarrier('responses')
        self.assertEqual(barrier.feed(original), original)
        self.assertFalse(barrier.completed)


class SettlementTests(unittest.IsolatedAsyncioTestCase):
    async def response(self, runtime, stream, *, operation='responses'):
        class Stream(httpx.AsyncByteStream):
            async def __aiter__(self):
                for part in stream:
                    if isinstance(part, Exception):
                        raise part
                    yield part
        await runtime.client.aclose()
        runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(
            lambda req: httpx.Response(200, headers={'content-type': 'text/event-stream'}, stream=Stream())))
        req = Request({'type': 'http', 'method': 'POST', 'path': route('openrouter', operation),
                       'query_string': b'', 'headers': []})
        req._body = json.dumps({**request_body('openrouter', operation), 'stream': True}).encode()
        req.state.request_id = 'first'
        return await runtime.proxy_model('openrouter', operation, req)

    async def test_next_turn_after_completion_waits_for_settlement(self):
        async with harness() as (client, runtime, calls):
            runtime.ledger.usd_limit = 1
            runtime.ledger.request_reservation_usd = 1
            entered, release = asyncio.Event(), asyncio.Event()
            async def delayed_charge(*args, **kwargs):
                entered.set()
                await release.wait()
                return 'gen-fixture', .1, 'fixture'
            prefix = b'data: {"type":"response.output_text.delta","delta":"hello"}\n\n'
            terminal = b'data: {"type":"response.completed","response":{"usage":{"input_tokens":2,"output_tokens":1,"total_tokens":3}}}\n\ndata: [DONE]\n\n'
            with patch('gateway_runtime.openrouter_charge', side_effect=delayed_charge):
                response = await self.response(runtime, [prefix, terminal])
                self.assertEqual(await asyncio.wait_for(anext(response.body_iterator), 2), prefix)
                await asyncio.wait_for(entered.wait(), 2)
                waiting = asyncio.create_task(anext(response.body_iterator))
                try:
                    await asyncio.sleep(0)
                    self.assertFalse(waiting.done(), 'completion escaped before settlement')
                    self.assertIn('first', runtime.ledger.model_inflight)
                    # Parallel requests must still respect active reservations.
                    rejected = await client.post(route('openrouter', 'responses'), json=request_body('openrouter', 'responses'))
                    self.assertEqual(rejected.status_code, 429)
                    self.assertEqual(rejected.headers['x-should-retry'], 'true')
                    self.assertEqual(rejected.headers['retry-after'], '1')
                finally:
                    release.set()
                self.assertEqual(await asyncio.wait_for(waiting, 2), terminal)
                self.assertFalse(runtime.ledger.model_inflight)
                self.assertAlmostEqual(runtime.ledger.budget_usd_spent, .1)
                # Start immediately on the terminal event, before consuming EOF.
                second = await client.post(route('openrouter', 'responses'), json=request_body('openrouter', 'responses'))
                self.assertEqual(second.status_code, 200, second.text)
                self.assertAlmostEqual(runtime.ledger.budget_usd_spent, .2)
                async for _ in response.body_iterator:
                    pass
                await asyncio.gather(*list(BACKGROUND_TASKS))

    async def test_unknown_or_exhausted_accounting_does_not_admit_next_turn(self):
        for usage, cost, expected_code in (
            ({'input_tokens': 2, 'output_tokens': 1, 'total_tokens': 3}, 1., 'model_budget_exhausted'),
            (None, .1, 'model_accounting_incomplete'),
            ({'input_tokens': 2, 'output_tokens': 1, 'total_tokens': 3}, None, 'model_accounting_incomplete'),
        ):
            async with harness() as (client, runtime, _):
                runtime.ledger.usd_limit = 1
                runtime.ledger.request_reservation_usd = 1
                terminal = b'data: ' + json.dumps({'type': 'response.completed', 'response': {'usage': usage}}).encode() + b'\n\n'
                async def charge(*args, **kwargs):
                    return 'gen-fixture', cost, 'fixture'
                with patch('gateway_runtime.openrouter_charge', side_effect=charge):
                    response = await self.response(runtime, [terminal])
                    self.assertEqual(await anext(response.body_iterator), terminal)
                    rejected = await client.post(route('openrouter', 'responses'), json=request_body('openrouter', 'responses'))
                    self.assertEqual(rejected.json()['code'], expected_code)
                    self.assertFalse(rejected.json()['retryable'])
                    self.assertEqual(rejected.headers['x-should-retry'], 'false')
                    async for _ in response.body_iterator:
                        pass
                    await asyncio.gather(*list(BACKGROUND_TASKS))

    async def test_disconnect_still_settles_without_replaying_inference(self):
        async with harness() as (_, runtime, __):
            entered, release = asyncio.Event(), asyncio.Event()
            async def charge(*args, **kwargs):
                entered.set()
                await release.wait()
                return 'gen-fixture', .1, 'fixture'
            prefix = b'data: {"type":"response.output_text.delta","delta":"hello"}\n\n'
            terminal = b'data: {"type":"response.completed","response":{"usage":{"input_tokens":2,"output_tokens":1,"total_tokens":3}}}\n\n'
            with patch('gateway_runtime.openrouter_charge', side_effect=charge):
                response = await self.response(runtime, [prefix, terminal])
                self.assertEqual(await anext(response.body_iterator), prefix)
                await entered.wait()
                await response.body_iterator.aclose()
                release.set()
                await asyncio.wait_for(asyncio.gather(*list(BACKGROUND_TASKS)), 2)
                self.assertFalse(runtime.ledger.model_inflight)
                self.assertAlmostEqual(runtime.ledger.budget_usd_spent, .1)
                self.assertEqual(runtime.ledger.counts['model_requests'], 1)

    async def test_interruption_does_not_invent_completion_or_free_unknown_spend(self):
        async with harness() as (_, runtime, __):
            prefix = b'data: {"type":"response.output_text.delta","delta":"hello"}\n\n'
            async def charge(*args, **kwargs):
                return None, None, 'unavailable'
            with patch('gateway_runtime.openrouter_charge', side_effect=charge):
                response = await self.response(runtime, [prefix, httpx.ReadError('synthetic interruption')])
                data = b''.join([part async for part in response.body_iterator])
                await asyncio.gather(*list(BACKGROUND_TASKS))
                self.assertEqual(data, prefix)
                self.assertTrue(runtime.ledger.model_accounting_incomplete)
                self.assertFalse(runtime.ledger.model_inflight)
