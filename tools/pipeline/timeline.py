import subprocess, json, os
SP='/tmp/claude-0/-home-user-Advisers/43f3f876-332f-5c13-8812-05a26eedb0e5/scratchpad'
OUTRO=2.6
TEMPO=1.42
os.makedirs(f'{SP}/narr_f',exist_ok=True)
durs=[]
for i in range(1,17):
    src=f'{SP}/narr_t/n{i:02d}.wav'; dst=f'{SP}/narr_f/n{i:02d}.wav'
    subprocess.run(['ffmpeg','-y','-v','error','-i',src,'-af',f'highpass=f=70,atempo={TEMPO}','-ar','44100','-ac','1',dst],check=True)
    d=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',dst],capture_output=True,text=True).stdout)
    durs.append(d)
pre=[0.9,0.45]+[0.3]*14
post=[0.4]*15+[0.0]
base=sum(durs)+sum(pre)+sum(post)
hold=OUTRO
TOTAL=round(base+hold,2)
print('narration',round(sum(durs),2),'base',round(base,2),'outro hold',round(hold,2),'TOTAL',TOTAL)
post[-1]=hold
scenes=[]; t=0.0
for i,d in enumerate(durs):
    s=t; v=s+pre[i]; e=v+d+post[i]
    scenes.append({'n':i+1,'start':round(s,3),'voice':round(v,3),'voice_end':round(v+d,3),'end':round(e,3)})
    t=e
json.dump({'total':TOTAL,'tempo':TEMPO,'scenes':scenes},open(f'{SP}/build/timeline.json','w'),indent=1)
for sc in scenes: print(sc)
