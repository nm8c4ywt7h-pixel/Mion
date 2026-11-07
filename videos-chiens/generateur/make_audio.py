import json, subprocess, sys
lang=sys.argv[1]; S=json.load(open(f"script_{lang}.json"))
gap=0.16; t=0.15; segs=[]
for i,l in enumerate(S["lines"]):
    f=f"a_{lang}_{i}.mp3"
    subprocess.run(["python3","tts.py",S["voice"],l["say"],f,S["rate"]],check=True)
    # trim leading/trailing silence
    w=f"a_{lang}_{i}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",f,"-af","silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse","-ar","44100","-ac","1",w],check=True)
    d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",w]))
    segs.append({"start":round(t,3),"end":round(t+d,3),"file":w}); t+=d+gap
total=round(t+0.6,2)
json.dump({"segs":segs,"total":total},open(f"timeline_{lang}.json","w"),indent=1)
print(segs,total)
