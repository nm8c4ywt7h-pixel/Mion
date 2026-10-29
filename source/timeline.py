import json, subprocess, sys, re
import numpy as np
B=sys.argv[1]; SR=44100
S=json.load(open(f"{B}/script.json")); W=json.load(open(f"{B}/words.json"))
def load(fn, af=None):
    cmd=['ffmpeg','-v','error','-i',fn]+(['-af',af] if af else [])+['-f','f32le','-ac','1','-ar',str(SR),'-']
    return np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32).copy()
FX={"N":None,
    "MOM":"aecho=0.8:0.6:70|140:0.25|0.15,highpass=f=120,volume=0.95",
    "KID":"volume=2.6,aecho=0.8:0.4:40:0.15,alimiter=limit=0.9"}
tracks=[]; lines=[]; t=0.35   # small lead-in
prev_end=t
for l in S:
    key=str(l['id']); words=W[key]
    a=load(f"{B}/vo_{key}.mp3", FX[l['who']])
    lead=words[0]['t']; last=words[-1]['t']+words[-1]['d']
    start=prev_end+l['gap']
    off=start-lead            # audio placed so that first word hits 'start'
    tracks.append((off,a))
    # chunks
    raw=l['text']
    chunks=[]; wi=0
    for part in [p.strip() for p in re.split(r'\|\|?',raw) if p.strip()]:
        toks=part.split()
        n=sum(1 for tk in toks if re.search(r'\w',tk))
        ws=words[wi:wi+n]; wi+=n
        if not ws: continue
        chunks.append({"text":part,"t0":off+ws[0]['t'],"t1":off+ws[-1]['t']+ws[-1]['d']})
    if wi!=len(words): print("WARN word count",key,wi,len(words),[w['w'] for w in words])
    lines.append({"id":l['id'],"who":l['who'],"label":l.get('label'),"join":l.get('join',False),
                  "t0":off+lead,"t1":off+last,"chunks":chunks,
                  "words":[{"w":w['w'],"t0":off+w['t'],"t1":off+w['t']+w['d']} for w in words]})
    prev_end=off+last
    if l['id']==9:
        a9=load(f"{B}/vo_9.mp3","asetrate=44100*0.86,aresample=44100,aecho=0.8:0.85:180|360|540:0.5|0.35|0.2")
        lw=words[-3:]
        s0=int(lw[0]['t']/0.86*SR); s1=int((lw[-1]['t']+lw[-1]['d'])/0.86*SR)
        echo=a9[s0:s1+int(1.1*SR)]*0.6
        e0=prev_end+0.2
        lines[-1]['echo']={"t0":e0,"t1":e0+(s1-s0)/SR}
        tracks.append((e0,echo)); prev_end=e0+(s1-s0)/SR+0.2
total=prev_end+3.2
N=int((total+1)*SR); mix=np.zeros(N,np.float32)
for off,a in tracks:
    i=int(off*SR); mix[i:i+len(a)]+=a[:max(0,N-i)]
mix/=max(1e-6,np.abs(mix).max())/0.9
mix.astype(np.float32).tofile(f"{B}/voice.f32")
json.dump({"total":total,"lines":lines},open(f"{B}/timeline.json","w"),ensure_ascii=False,indent=0)
print("total",round(total,2))
for x in lines: print(x['id'],x['who'],round(x['t0'],2),round(x['t1'],2),[c['text'] for c in x['chunks']])
