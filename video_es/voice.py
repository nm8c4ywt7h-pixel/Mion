import json,subprocess,numpy as np,wave
SR=44100
d=json.load(open('tts/words.json'))
def load(p):
    raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-ac','1','-ar',str(SR),'-f','s16le','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.int16).astype(np.float32)/32768
out=[];t=0.35;tl=[]
pad=0.04
for l in d:
    a=load(f"tts/l{l['i']:02d}.mp3")
    s0=max(0,l['words'][0][0]-pad); s1=l['words'][-1][1]+0.12
    seg=a[int(s0*SR):int(s1*SR)]
    tl.append({'i':l['i'],'text':l['text'],'start':t,'end':t+len(seg)/SR,
               'words':[[t+w[0]-s0,t+w[1]-s0,w[2]] for w in l['words']]})
    out.append((int(t*SR),seg)); t+=len(seg)/SR+0.06
total=t+0.6
buf=np.zeros(int(total*SR)+SR,np.float32)
for p,seg in out: buf[p:p+len(seg)]+=seg
buf=buf[:int(total*SR)]
np.save('voice.npy',buf)
json.dump({'total':total,'lines':tl},open('timeline.json','w'),ensure_ascii=False,indent=1)
print(total)
