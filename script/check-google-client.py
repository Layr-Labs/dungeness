#!/usr/bin/env python3
"""Exercise Google's real SDK against a local gateway and synthetic upstream.

Run: uv run --frozen --group gateway --with google-genai==3.6.1 python -B script/check-google-client.py
No provider traffic, account credentials, Docker or VM is used.
"""
import asyncio
import copy
import json
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / p) for p in ("src", "services/gateway", "services/gateway/tests")]

from google import genai
from google.genai import types
import httpx
import uvicorn
from test_google_routes import registered_route, MODEL, RESULT
import gateway
from test_gateway import canonical_events
from test_history_roundtrip import Fragments


async def check(provider):
    async with registered_route(provider) as (_, runtime, _):
        requests = []
        tool_content = {"role": "model", "parts": [{
            "functionCall": {"name": "evaluate", "args": {"candidate": "local"}},
            "thoughtSignature": "c2lnbmVkLWNhbGw=",
        }]}

        def upstream(request):
            requests.append(request)
            result = copy.deepcopy(RESULT)
            if len(requests) % 2:
                result["candidates"][0]["content"] = tool_content
            if ":streamGenerateContent" in request.url.path:
                raw = ("data: " + json.dumps(result) + "\r\n\r\n").encode()
                return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=Fragments(raw))
            return httpx.Response(200, json=result)

        await runtime.client.aclose()
        runtime.client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(gateway.app, log_level="error", lifespan="off"))
        task = asyncio.create_task(server.serve(sockets=[listener]))
        try:
            async with asyncio.timeout(10):
                while not server.started:
                    if task.done():
                        await task
                        raise AssertionError("Gateway did not start")
                    await asyncio.sleep(.01)
            client = genai.Client(
                api_key="testbed",
                http_options=types.HttpOptions(
                    base_url=f"http://127.0.0.1:{port}/model/{provider}", api_version="v1beta",
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
            config = types.GenerateContentConfig(
                max_output_tokens=512,
                thinking_config=types.ThinkingConfig(thinking_level="LOW"),
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                tools=[types.Tool(function_declarations=[types.FunctionDeclaration(
                    name="evaluate", parameters_json_schema={
                        "type": "object", "properties": {"candidate": {"type": "string"}},
                    },
                )])],
            )
            try:
                for streaming in (False, True):
                    history = [types.Content(role="user", parts=[types.Part(text="Evaluate locally.")])]

                    async def generate():
                        if streaming:
                            chunks = [chunk async for chunk in await client.aio.models.generate_content_stream(
                                model=MODEL, contents=history, config=config)]
                            return chunks[-1]
                        return await client.aio.models.generate_content(model=MODEL, contents=history, config=config)

                    first = await generate()
                    assert first.function_calls[0].name == "evaluate"
                    history.extend([first.candidates[0].content, types.Content(role="user", parts=[
                        types.Part.from_function_response(name="evaluate", response={"score": 42}),
                    ])])
                    final = await generate()
                    assert final.text == "42"
                    assert json.loads(requests[-1].content)["contents"][1] == tool_content
                    assert final.usage_metadata.thoughts_token_count == 20
            finally:
                await client.aio.aclose()
                client.close()
            receipts = canonical_events(runtime.ledger.directory, "model.accounting")
            assert len(requests) == len(receipts) == 4
            assert all(r["input_tokens"] == 100 and r["output_tokens"] == 30 for r in receipts)
            assert not runtime.ledger.model_accounting_incomplete
            print(f"{provider}: SDK JSON + SSE tool rounds, signatures and accounting passed")
        finally:
            server.should_exit = True
            await asyncio.wait_for(task, 10)
            listener.close()


async def main():
    for provider in ("google", "google-vertex"):
        await check(provider)


if __name__ == "__main__":
    asyncio.run(main())
