import json, numpy as np, sys
SR=44100; B=sys.argv[1]
TL=json.load(open(f"{B}/timeline.json")); SH=json.load(open(sys.argv[2]))
T=TL['total']+0.3; N=int(T*SR); rng=np.random.default_rng(7)
L={str(l['id']):l for l in TL['lines']}
def A(s):
    b,_,o=s.partition('+'); o=float(o or 0); neg=0
    if '-' in b: b,neg=b.split('-'); neg=float(neg)
    i,c=b.split(':'); l=L[i]
    t=l['echo']['t0'] if c=='echo' else l['t1'] if c=='end' else l['t0'] if c=='start' else l['chunks'][int(c)]['t0']
    return t+o-neg
mus=np.zeros((N,2)); fx=np.zeros((N,2))
tt=lambda d: np.arange(int(d*SR))/SR
def env(n,a=.005,r=.3):
    e=np.ones(n); ai=max(1,int(a*SR)); e[:ai]=np.linspace(0,1,ai); ri=min(n,int(r*SR)); e[-ri:]*=np.linspace(1,0,ri)**2; return e
def put(buf,t0,x,g=1.,pan=0.):
    i=int(t0*SR); 
    if i>=N: return
    x=x[:N-i]; 
    if x.ndim==1: x=np.stack([x*(1-max(0,pan)),x*(1+min(0,pan))],1)
    buf[i:i+len(x)]+=x*g
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x); s=0.
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
def lpf(x,cut):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*=1/(1+(f/cut)**4); return np.fft.irfft(X,len(x))
def bpf(x,lo,hi):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); X*=((f>lo)&(f<hi)); return np.fft.irfft(X,len(x))
# --- SFX generators
def boom(d=2.2):
    t=tt(d); f=55*np.exp(-t*1.2)+28; ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)*np.exp(-t*2.2)+lpf(rng.standard_normal(len(t)),180)*np.exp(-t*6)*2
    return x/np.abs(x).max()
def hit(d=.5):
    t=tt(d); x=np.sin(2*np.pi*(90*np.exp(-t*10)+40)*t)*np.exp(-t*9)+lpf(rng.standard_normal(len(t)),2500)*np.exp(-t*30)*.6
    return x/np.abs(x).max()
def whoosh(d=.55,rev=False):
    t=tt(d); n=rng.standard_normal(len(t)); e=np.sin(np.pi*t/d)**2
    x=bpf(n,300,4000)*e; 
    if rev: e2=(t/d)**3; x=bpf(n,200,6000)*e2*env(len(t),.001,.03)
    return x/np.abs(x).max()
def riser(d=2.):
    t=tt(d); f=200+1400*(t/d)**2; x=np.sin(2*np.pi*np.cumsum(f)/SR)*.3+bpf(rng.standard_normal(len(t)),800,8000)*.7
    x*=(t/d)**2; x*=env(len(t),.01,.02); return x/np.abs(x).max()
def heartbeat(n=4,bpm=78):
    per=60/bpm; out=np.zeros(int(per*n*SR)+SR)
    for k in range(n):
        for dt,g in ((0,1),(.22,.7)):
            t=tt(.25); b=np.sin(2*np.pi*(60*np.exp(-t*8)+35)*t)*np.exp(-t*18)*g; put_i=int((k*per+dt)*SR); out[put_i:put_i+len(b)]+=b
    return out/np.abs(out).max()
def scratch(d=1.6):
    t=tt(d); x=np.zeros(len(t))
    for k in range(4):
        s=int((.15+k*.33)*SR); l=int(.24*SR); n=bpf(rng.standard_normal(l),1500,7000)*(1+np.sin(2*np.pi*35*tt(l/SR)))*np.hanning(l); x[s:s+l]+=n
    return x/np.abs(x).max()
def creak(d=1.2):
    t=tt(d); f=180+120*np.sin(2*np.pi*.7*t)+40*rng.standard_normal(len(t)).cumsum()/SR*3
    p=(np.cumsum(f)/SR)%1; x=(p<.08).astype(float)-.08; x=bpf(x,150,3000)*np.sin(np.pi*t/d)
    return x/np.abs(x).max()
def jingle(d=1.0,n=3):
    out=np.zeros(int(d*SR))
    for k in range(n):
        t=tt(.6); fr=[2637,3520,4186,5274]; x=sum(np.sin(2*np.pi*f*(1+.002*k)*t)*np.exp(-t*(7+i*2)) for i,f in enumerate(fr))
        s=int(k*.12*SR+rng.random()*.03*SR); out[s:s+len(x)]+=x[:len(out)-s]
    return out/np.abs(out).max()
def growl(d=1.8):
    t=tt(d); f=70+15*np.sin(2*np.pi*3*t); saw=2*((np.cumsum(f)/SR)%1)-1
    am=.6+.4*np.abs(np.sin(2*np.pi*11*t+rng.random()))
    x=lpf(saw*am+bpf(rng.standard_normal(len(t)),100,900)*.8*am,900)*env(len(t),.15,.4)
    return x/np.abs(x).max()
def glitch(d=.4):
    t=tt(d); x=np.sign(np.sin(2*np.pi*(rng.integers(200,1800))*t))*(rng.random(len(t))<.5)
    st=(np.floor(t*40)%2)
    x=x*st+bpf(rng.standard_normal(len(t)),2000,9000)*(1-st); return .6*x*env(len(t),.001,.05)
def sting(d=1.6):  # dissonant cluster
    t=tt(d); x=sum(np.sin(2*np.pi*f*t+np.sin(2*np.pi*5.5*t)*.3) for f in (311,329.6,466,493.9))*np.exp(-t*2.2)
    return x/np.abs(x).max()
def melt(d=2.6):
    t=tt(d); f=420*np.exp(-t*1.1)+40; x=np.sin(2*np.pi*np.cumsum(f)/SR+3*np.sin(2*np.pi*7*t))
    x=x*.5+lpf(rng.standard_normal(len(t)),600)*1.5; x*=env(len(t),.2,.8); return x/np.abs(x).max()
def gulp(d=.6):
    t=tt(d); x=np.sin(2*np.pi*(300*np.exp(-t*12)+60)*t)*np.exp(-t*7); return x/np.abs(x).max()
def tick():
    t=tt(.04); return bpf(rng.standard_normal(len(t)),2500,7000)*np.exp(-t*160)
# --- music bed: dark drone + pulse
t=np.arange(N)/SR
dr=sum(np.sin(2*np.pi*f*t+np.sin(2*np.pi*.08*t+i)*2)*a for i,(f,a) in enumerate(((43.65,.5),(65.4,.35),(87.3,.18),(92.5,.12))))
air=lpf(rng.standard_normal(N),400)*.6
bed=(dr+air)*(.85+.15*np.sin(2*np.pi*.11*t))
mus[:,0]+=bed*.16; mus[:,1]+=np.roll(bed,900)*.16
# clock ticks through the room scenes
for k in np.arange(0.5, T-3, 1.0): put(fx,k,tick(),.10,-.3)
# --- event list
ev=[
 ('1:0-0.33',boom(),.75),('1:0-0.33',whoosh(.35,True),.25),
 ('1:1',whoosh(.4),.18),('2:0',hit(),.35),('2:0+0.1',heartbeat(5,84),.45),
 ('4:0',jingle(.6,2),.18),('5:1',whoosh(.5),.18),('6:0',sting(2.2),.18),
 ('6:5',hit(),.45),('6:5+0.5',hit(.3),.25),('7:0',boom(2.),.4),
 ('8:0',creak(1.3),.32),('8:1',whoosh(.5),.12),('9:1',heartbeat(4,70),.4),
 ('9:echo',boom(2.5),.6),('9:echo',glitch(.35),.25),
 ('10:0-0.3',whoosh(.6,True),.25),('10:1+0.2',scratch(1.8),.45),('11:0+0.3',creak(1.4),.35),
 ('13:start',boom(2.6),.85),('13:start+0.28',hit(),.5),('13:start-0.4',riser(.45),.25),
 ('14:0',heartbeat(4,96),.5),('15:start+1.2',sting(1.4),.25),
 ('16:0',hit(),.7),('16:0',glitch(.35),.35),('16:1',boom(1.6),.4),('16:1',bpf(rng.standard_normal(int(.8*SR)),1500,9000)*np.exp(-tt(.8)*5),.25),
 ('17:0+0.6',melt(2.6),.45),('17:3',gulp(),.5),
 ('18:0',whoosh(.6),.12),('19:0',bpf(rng.standard_normal(int(1.3*SR)),300,3000)*(.5+.5*np.sin(2*np.pi*4*tt(1.3)))*.5,.25),
 ('20:0',jingle(.8,3),.32),('20:1',jingle(1.0,4),.32),('20:2',hit(.3),.18),
 ('21:start',sting(1.8),.12),('22:3',hit(),.35),('23:0',heartbeat(4,100),.5),('24:0',riser(2.0),.12),
 ('26:2',growl(1.9),.75),('26:2',boom(1.6),.35),
 ('27:start',riser(3.2),.22),('27:1+0.9',hit(),.6),('27:1+0.9',glitch(.3),.3),
 ('28:start-0.25',boom(3.),.75),('28:1',hit(),.4),
]
for a,x,gain in ev: put(fx,A(a),x,gain)
for i in range(len(L['24']['words'])): pass
l=L['24']; dur=l['t1']-l['t0']
for i in range(7): put(fx,l['t0']+i*dur/7.5,hit(.15),.12)  # calendar X marks
# small whoosh on every shot cut
for s in SH[1:]: put(fx,s['t0']-0.06,whoosh(.22,True),.08)
# duck music under voice slightly
voice=np.fromfile(f"{B}/voice.f32",np.float32)[:N]; voice=np.pad(voice,(0,N-len(voice)))
ve=np.convolve(np.abs(voice),np.ones(4410)/4410,'same'); duck=1-.35*np.clip(ve*8,0,1)
# music drops out before the big cards, then back
for a,d in (('13:start-0.1',.9),('28:start-0.4',.5)):
    i=int(A(a)*SR); n=int(d*SR); duck[i:i+n]*=np.linspace(1,.1,n)[::-1]*0+.15
mix=mus*duck[:,None]+fx+np.stack([voice,voice],1)*1.0
mix*=np.clip((np.arange(N)/SR)/0.05,0,1)[:,None]
fade=np.clip((T-np.arange(N)/SR)/1.2,0,1); mix*=fade[:,None]
mix/=np.abs(mix).max()/0.95
mix.astype(np.float32).tofile(f"{B}/mix.f32"); print('ok',mix.shape[0]/SR)
