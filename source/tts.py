import asyncio, json, sys, os, re, subprocess
import edge_tts
B=sys.argv[1]
VOICES={"N":("es-MX-JorgeNeural","+22%","-6Hz"),
        "MOM":("es-MX-DaliaNeural","+8%","-4Hz"),
        "KID":("es-CO-SalomeNeural","+14%","+22Hz")}
async def one(l):
    v,r,p=VOICES[l['who']]
    plain=l['text'].replace('*','').replace('||',' ').replace('|',' ')
    plain=re.sub(r'\s+',' ',plain).strip()
    c=edge_tts.Communicate(plain,v,rate=r,pitch=p,boundary="WordBoundary")
    audio=b'';words=[]
    async for ch in c.stream():
        if ch['type']=='audio': audio+=ch['data']
        elif ch['type']=='WordBoundary':
            words.append({"t":ch['offset']/1e7,"d":ch['duration']/1e7,"w":ch['text']})
    fn=f"{B}/vo_{l['id']}.mp3"; open(fn,'wb').write(audio)
    return words
async def main():
    s=json.load(open(f"{B}/script.json"))
    res={}
    for l in s:
        for k in range(4):
            try: res[str(l['id'])]=await one(l); break
            except Exception as e: print('retry',l['id'],e); await asyncio.sleep(2)
    json.dump(res,open(f"{B}/words.json",'w'),ensure_ascii=False)
asyncio.run(main())
