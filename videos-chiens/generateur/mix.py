import json, sys, wave, numpy as np, subprocess
lang=sys.argv[1]; SR=44100
tl=json.load(open(f"timeline_{lang}.json")); ev=json.load(open(f"events_{lang}.json"))
N=int(tl["total"]*SR); out=np.zeros(N)
def rd(f):
    w=wave.open(f); return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(float)/32768
def add(sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig));
    if i<N: out[i:j]+=sig[:j-i]*g
# music: cheerful plucked progression, 112 bpm
bpm=112; beat=60/bpm; music=np.zeros(N)
def pluck(f,d,amp):
    t=np.arange(int(d*SR))/SR; env=np.exp(-t*5)*np.minimum(1,t*200)
    return amp*env*(np.sin(2*np.pi*f*t)+0.35*np.sin(4*np.pi*f*t)+0.15*np.sin(6*np.pi*f*t))
chords=[[261.6,329.6,392.0],[196.0,246.9,293.7],[220.0,261.6,329.6],[174.6,220.0,261.6]]
pat=[0,2,1,2,0,2,1,2]
b=0;t=0
while t<tl["total"]:
    ch=chords[(b//8)%4]; n=ch[pat[b%8]%3]*(2 if b%8 in(2,6) else 1)
    s=pluck(n,0.5,0.18); i=int(t*SR); j=min(N,i+len(s)); music[i:j]+=s[:j-i]
    if b%2==0:
        s=pluck(ch[0]/2,0.7,0.22); j=min(N,i+len(s)); music[i:j]+=s[:j-i]
    # soft hat
    if b%2==1:
        h=np.random.RandomState(b).randn(int(0.04*SR))*np.exp(-np.arange(int(0.04*SR))/SR*90)*0.03; j=min(N,i+len(h)); music[i:j]+=h[:j-i]
    b+=1; t=b*beat/2
# no music at very start (sad), fade in after "il t'a toi"
env=np.ones(N); s2=int(tl["segs"][2]["start"]*SR); env[:s2]=0.35
duck=np.ones(N)
for sg in tl["segs"]:
    a=int(sg["start"]*SR); b=int(sg["end"]*SR); duck[a:b]=0.55
duck=np.convolve(duck,np.ones(2205)/2205,'same')
for k in ev.get("dream",[]):
    pass
out+=music*env*duck*0.6
def popsnd():
    t=np.arange(int(0.12*SR))/SR; f=600+2200*t/0.12
    return 0.35*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30)
def clicksnd():
    t=np.arange(int(0.5*SR))/SR
    return 0.3*(np.sin(2*np.pi*880*t)*(t<0.12)+np.sin(2*np.pi*1320*t)*(t>=0.12))*np.exp(-(t%0.12)*12)*(t<0.4)
def whoosh():
    t=np.arange(int(0.25*SR))/SR; n=np.random.RandomState(1).randn(len(t))
    n=np.convolve(n,np.ones(30)/30,'same'); return 0.25*n*np.sin(np.pi*t/0.25)
def coin():
    t=np.arange(int(0.6*SR))/SR
    return 0.25*(np.sin(2*np.pi*1975*t)*(t<0.08)+np.sin(2*np.pi*2637*t)*(t>=0.08))*np.exp(-t*6)
def sadsnd():
    t=np.arange(int(1.0*SR))/SR; f=440*np.power(0.5,t/1.0*0.9)
    return 0.22*np.sin(2*np.pi*np.cumsum(f)/SR)*(1+0.3*np.sin(2*np.pi*6*t))*np.exp(-t*1.5)
def shimmer():
    out=np.zeros(int(1.6*SR))
    for i,f in enumerate([1046,1318,1568,2093,2637,3136]):
        st=int(i*0.12*SR); t=np.arange(len(out)-st)/SR; out[st:]+=0.08*np.sin(2*np.pi*f*t)*np.exp(-t*3)
    return out
for x in ev.get("coins",[]):
    for k in range(5): add(coin(),x+k*0.22,0.8)
for x in ev.get("sad",[]): add(sadsnd(),x)
for x in ev.get("dream",[]): add(shimmer(),x)
for x in ev["pops"]: add(popsnd(),x)
for x in ev["click"]: add(clicksnd(),x)
for x in ev["whoosh"][1:]: add(whoosh(),x-0.12,0.6)
for s in tl["segs"]: add(rd(s["file"]),s["start"],1.35)
out=out/max(1,np.abs(out).max()/0.95)
w=wave.open(f"mix_{lang}.wav","w");w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
