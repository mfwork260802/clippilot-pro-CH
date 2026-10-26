import asyncio
import json
from typing import AsyncIterator


def _sse(data: dict) -> str:
    """Format a dict as a Server-Sent Event string."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def with_heartbeat(events: AsyncIterator[str], interval: float = 15.0) -> AsyncIterator[str]:
    """Re-yields SSE events and inserts a comment line whenever the source is idle for `interval` seconds.

    Long steps (transcript fetching, audio download, Whisper) can go minutes without an event;
    hosting proxies may drop such idle connections, which the browser reports as "Error in input stream".
    """
    iterator = events.__aiter__()
    pending = asyncio.ensure_future(iterator.__anext__())
    try:
        while True:
            done, _ = await asyncio.wait({pending}, timeout=interval)
            if not done:
                yield ": heartbeat\n\n"
                continue
            try:
                item = pending.result()
            except StopAsyncIteration:
                return
            yield item
            pending = asyncio.ensure_future(iterator.__anext__())
    finally:
        # Client disconnected or stream ended: stop the in-flight step, then close the source.
        if not pending.done():
            pending.cancel()
            try:
                await pending
            except (asyncio.CancelledError, StopAsyncIteration, Exception):
                pass
        aclose = getattr(iterator, "aclose", None)
        if aclose:
            try:
                await aclose()
            except Exception:
                pass
