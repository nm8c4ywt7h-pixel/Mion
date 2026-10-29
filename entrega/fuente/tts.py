import asyncio, sys, json, certifi
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts
async def main(spec, out):
    allw = []
    for i, (voice, rate, pitch, text) in enumerate(json.load(open(spec))):
        c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
        words = []
        with open(f"{out}/l{i:02d}.mp3", "wb") as f:
            async for ch in c.stream():
                if ch["type"] == "audio": f.write(ch["data"])
                elif ch["type"] == "WordBoundary":
                    words.append([ch["text"], ch["offset"]/1e7, ch["duration"]/1e7])
        allw.append(words)
    json.dump(allw, open(f"{out}/words.json", "w"), ensure_ascii=False, indent=0)
asyncio.run(main(sys.argv[1], sys.argv[2]))
