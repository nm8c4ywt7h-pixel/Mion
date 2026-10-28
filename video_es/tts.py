import certifi; certifi.where=lambda:'/root/.ccr/ca-bundle.crt'
import asyncio, edge_tts, json, sys
lines=[l.strip() for l in open(sys.argv[1],encoding='utf8') if l.strip()]
voice,rate,out=sys.argv[2],sys.argv[3],sys.argv[4]
async def one(i,t):
    c=edge_tts.Communicate(t,voice,rate=rate,boundary='WordBoundary')
    words=[]
    with open(f'{out}/l{i:02d}.mp3','wb') as f:
        async for ch in c.stream():
            if ch['type']=='audio': f.write(ch['data'])
            elif ch['type']=='WordBoundary': words.append([ch['offset']/1e7,(ch['offset']+ch['duration'])/1e7,ch['text']])
    return {'i':i,'text':t,'words':words}
async def main():
    res=[await one(i,t) for i,t in enumerate(lines)]
    json.dump(res,open(f'{out}/words.json','w'),ensure_ascii=False,indent=0)
asyncio.run(main())
