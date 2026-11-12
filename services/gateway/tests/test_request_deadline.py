"""Absolute deadlines cover active streaming and detached accounting drains."""
import asyncio
import json
import os
import unittest
from unittest.mock import patch
import httpx
from starlette.requests import Request

from test_gateway import canonical_events
from test_request_policy import harness, request_body, route
from gateway_runtime import BACKGROUND_TASKS, Gateway

COMPLETE=b'data: {"type":"response.completed","response":{"id":"gen-fixture","usage":{"input_tokens":2,"output_tokens":1,"total_tokens":3,"cost":0.1}}}\n\n'


class Trickle(httpx.AsyncByteStream):
    def __init__(self,complete=False):self.closed=False;self.complete=complete
    async def __aiter__(self):
        if self.complete:yield COMPLETE
        while True:
            yield b': heartbeat\n\n'
            await asyncio.sleep(.005)
    async def aclose(self):self.closed=True


class RequestDeadlineTests(unittest.IsolatedAsyncioTestCase):
    async def response(self,runtime,stream,headers_delay=0,streaming=True):
        async def upstream(req):
            await asyncio.sleep(headers_delay)
            return httpx.Response(200,headers={'content-type':'text/event-stream' if streaming else 'application/json'},stream=stream)
        await runtime.client.aclose()
        runtime.client=httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        req=Request({'type':'http','method':'POST','path':route('openrouter','responses'),'query_string':b'','headers':[]})
        req._body=json.dumps({**request_body('openrouter','responses'),'stream':streaming}).encode()
        req.state.request_id='deadline-test'
        return await runtime.proxy_model('openrouter','responses',req)

    async def test_stream_deadline_with_consumer_disconnect_and_stall(self):
        for consumer in ('reading','disconnected','stalled'):
            with self.subTest(consumer=consumer):
                async with harness() as (_,runtime,__):
                    runtime.request_timeout_seconds=.12
                    stream=Trickle();start=asyncio.get_running_loop().time()
                    response=await self.response(runtime,stream)
                    if consumer=='reading':
                        async for _ in response.body_iterator:pass
                    elif consumer=='disconnected':
                        await anext(response.body_iterator)
                        await response.body_iterator.aclose()
                    await asyncio.wait_for(asyncio.gather(*list(BACKGROUND_TASKS)),1)
                    self.assertLess(asyncio.get_running_loop().time()-start,1)
                    self.assertTrue(stream.closed)
                    self.assertFalse(runtime.ledger.model_inflight)
                    self.assertTrue(runtime.ledger.model_accounting_incomplete)
                    events = canonical_events(runtime.ledger.directory, 'model.accounting')
                    self.assertEqual(len(events), 1)
                    self.assertEqual(events[0]['failure_category'], 'upstream_request_deadline_exceeded')
                    if consumer=='stalled':await response.body_iterator.aclose()
                    self.assertTrue(all(t.done() for t in BACKGROUND_TASKS))

    async def test_complete_usage_survives_deadline_and_completion_waits_for_settlement(self):
        async with harness() as (_,runtime,__):
            runtime.request_timeout_seconds=.05
            stream=Trickle(complete=True)
            response=await self.response(runtime,stream)
            output=b''
            async for chunk in response.body_iterator:
                if b'response.completed' in chunk:
                    self.assertFalse(runtime.ledger.model_inflight)
                    self.assertAlmostEqual(runtime.ledger.budget_usd_spent,.1)
                output+=chunk
            await asyncio.gather(*list(BACKGROUND_TASKS))
            self.assertIn(COMPLETE,output)
            self.assertEqual(runtime.ledger.counts['model_requests'],1)
            self.assertFalse(runtime.ledger.model_accounting_incomplete)
            self.assertAlmostEqual(runtime.ledger.budget_usd_spent,.1)

    async def test_headers_and_nonstreaming_share_one_deadline(self):
        from gateway_runtime import RequestDeadlineExceeded
        async with harness() as (_,runtime,__):
            runtime.request_timeout_seconds=.08
            stream=Trickle();start=asyncio.get_running_loop().time()
            with self.assertRaises(RequestDeadlineExceeded):
                await self.response(runtime,stream,headers_delay=.04,streaming=False)
            self.assertLess(asyncio.get_running_loop().time()-start,.15)
            self.assertTrue(stream.closed)
            self.assertTrue(runtime.ledger.model_accounting_incomplete)
            self.assertFalse(runtime.ledger.model_inflight)

    async def test_header_timeout_has_safe_diagnostic_and_no_retry(self):
        async with harness() as (client,runtime,calls):
            runtime.request_timeout_seconds=.03
            async def upstream(req):
                calls.append('sent');await asyncio.sleep(10)
            await runtime.client.aclose()
            runtime.client=httpx.AsyncClient(transport=httpx.MockTransport(upstream))
            response=await client.post(route('openrouter','responses'),json=request_body('openrouter','responses'))
            self.assertEqual(response.status_code,502)
            diagnostic=response.json()['diagnostic']
            self.assertEqual(diagnostic['failure_category'],'upstream_request_deadline_exceeded')
            self.assertEqual(diagnostic['run_action'],'stop')
            self.assertFalse(diagnostic['retryable'])
            self.assertTrue(diagnostic['upstream_request_sent'])
            self.assertEqual(len(calls),1)

    async def test_stuck_accounting_lookup_is_bounded_and_not_free(self):
        async with harness() as (_,runtime,__):
            runtime.request_timeout_seconds=.03
            async def stalled(*a,**kw):await asyncio.sleep(10)
            with patch('gateway_runtime.ACCOUNTING_CLEANUP_SECONDS',.03),patch('gateway_runtime.openrouter_charge',side_effect=stalled):
                response=await self.response(runtime,Trickle(complete=True))
                async def consume():
                    async for _ in response.body_iterator:pass
                await asyncio.wait_for(consume(),1)
                await asyncio.gather(*list(BACKGROUND_TASKS))
            self.assertTrue(runtime.ledger.model_accounting_incomplete)
            self.assertEqual(runtime.ledger.counts['model_tokens'],3)
            self.assertFalse(runtime.ledger.model_inflight)

    async def test_stuck_transport_close_does_not_prevent_accounting(self):
        class StuckClose(Trickle):
            async def aclose(self):
                await asyncio.sleep(10)
        async with harness() as (_, runtime, __):
            runtime.request_timeout_seconds = .03
            with patch('gateway_runtime.UPSTREAM_CLOSE_SECONDS', .03):
                response = await self.response(runtime, StuckClose(complete=True))
                async def consume():
                    async for _ in response.body_iterator:
                        pass
                await asyncio.wait_for(consume(), 1)
                await asyncio.gather(*list(BACKGROUND_TASKS))
            self.assertFalse(runtime.ledger.model_inflight)
            self.assertFalse(runtime.ledger.model_accounting_incomplete)
            self.assertEqual(len(canonical_events(runtime.ledger.directory, 'model.accounting')), 1)

    async def test_duration_configuration_rejects_invalid_values(self):
        for value in ('0','-1','nan','inf','bad'):
            with self.subTest(value=value),patch.dict(os.environ,{'DUNGENESS_MODEL_REQUEST_TIMEOUT_SECONDS':value}):
                with self.assertRaisesRegex(ValueError,'finite and positive'):Gateway()
