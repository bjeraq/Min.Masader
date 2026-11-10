"""Trim silences, speed up narration clips, and build scene timing (8 scenes) -> build/timeline.json."""
import subprocess, json, os, sys
SP = os.environ.get('SP', '/tmp/claude-0/-home-user-Min-Masader/0d5c69df-74a2-5d9e-8326-acc5fdf4f588/scratchpad/fires')
TEMPO = float(sys.argv[1]) if len(sys.argv) > 1 else 1.18
N = 8
for d in ('narr_t', 'narr_f', 'build'):
    os.makedirs(f'{SP}/{d}', exist_ok=True)


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                capture_output=True, text=True).stdout)


durs = []
for i in range(1, N + 1):
    src = f'{SP}/audio/narr{i}.wav'; t = f'{SP}/narr_t/n{i:02d}.wav'; f = f'{SP}/narr_f/n{i:02d}.wav'
    # trim leading/trailing silence, shorten long internal pauses to 0.35 s
    af = ('silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,'
          'areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,'
          'silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-45dB')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-af', af, '-ar', '44100', '-ac', '1', t], check=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', t, '-af', f'highpass=f=70,atempo={TEMPO}', '-ar', '44100', '-ac', '1', f], check=True)
    durs.append(dur(f))
    print(i, round(dur(src), 2), '->', round(dur(t), 2), '->', round(durs[-1], 2))
pre = [0.8, 0.5] + [0.35] * (N - 2)
post = [0.45] * (N - 1) + [3.2]
scenes = []; t = 0.0
for i, d in enumerate(durs):
    s = t; v = s + pre[i]; e = v + d + post[i]
    scenes.append({'n': i + 1, 'start': round(s, 3), 'voice': round(v, 3), 'voice_end': round(v + d, 3), 'end': round(e, 3)})
    t = e
TOTAL = round(t, 2)
json.dump({'total': TOTAL, 'tempo': TEMPO, 'scenes': scenes}, open(f'{SP}/build/timeline.json', 'w'), indent=1)
print('TOTAL', TOTAL)
