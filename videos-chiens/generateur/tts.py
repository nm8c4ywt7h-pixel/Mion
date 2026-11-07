import sys, asyncio, certifi
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts
async def main(voice, text, out, rate="+0%"):
    c = edge_tts.Communicate(text, voice, rate=rate)
    await c.save(out)
asyncio.run(main(*sys.argv[1:]))
