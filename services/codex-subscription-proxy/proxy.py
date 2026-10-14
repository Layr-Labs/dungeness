"""Allowlisted HTTP CONNECT proxy for Codex subscription token refresh."""

from __future__ import annotations

import asyncio
import os


MAX_HEADER_BYTES = 64 * 1024
BUFFER_SIZE = 64 * 1024


def allowed_hosts() -> tuple[str, ...]:
    values = os.environ.get("CODEX_ALLOWED_HOSTS", "")
    return tuple(value.strip().lower() for value in values.split(",") if value.strip())


def host_is_allowed(host: str, allowlist: tuple[str, ...]) -> bool:
    normalized = host.rstrip(".").lower()
    for pattern in allowlist:
        if pattern.startswith("."):
            suffix = pattern[1:]
            if normalized == suffix or normalized.endswith(f".{suffix}"):
                return True
        elif normalized == pattern:
            return True
    return False


async def relay(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    try:
        while data := await reader.read(BUFFER_SIZE):
            writer.write(data)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        writer.close()


async def reject(writer: asyncio.StreamWriter, status: str) -> None:
    writer.write(
        f"HTTP/1.1 {status}\r\nConnection: close\r\nContent-Length: 0\r\n\r\n".encode()
    )
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    try:
        header = await reader.readuntil(b"\r\n\r\n")
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError):
        await reject(writer, "400 Bad Request")
        return
    if len(header) > MAX_HEADER_BYTES:
        await reject(writer, "431 Request Header Fields Too Large")
        return

    try:
        request_line = header.split(b"\r\n", 1)[0].decode("ascii")
        method, authority, _version = request_line.split(" ", 2)
        host, separator, port_text = authority.rpartition(":")
        port = int(port_text) if separator else 443
    except (UnicodeDecodeError, ValueError):
        await reject(writer, "400 Bad Request")
        return

    if method.upper() != "CONNECT":
        await reject(writer, "405 Method Not Allowed")
        return
    if port != 443 or not host_is_allowed(host, allowed_hosts()):
        await reject(writer, "403 Forbidden")
        return

    try:
        upstream_reader, upstream_writer = await asyncio.open_connection(host, port)
    except OSError:
        await reject(writer, "502 Bad Gateway")
        return

    writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
    await writer.drain()
    await asyncio.gather(
        relay(reader, upstream_writer),
        relay(upstream_reader, writer),
    )


async def main() -> None:
    port = int(os.environ.get("PORT", "8081"))
    server = await asyncio.start_server(handle_client, "0.0.0.0", port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
