"""Phrase-level alignment of each narration clip: map a character index of the spoken text to a time.

Each clip is split into speech segments by short pauses; the text is split at punctuation. When the
counts match, phrase k maps to segment k; otherwise characters are spread over the speech-only time.
"""
import json, re, subprocess
import numpy as np

SP = '/tmp/claude-0/-home-user-Advisers/43f3f876-332f-5c13-8812-05a26eedb0e5/scratchpad'
SR = 16000
TTS = {
    1: 'علبة طاقة، ومشروب غازي، وعلبة سجائر... هل سترتفع أسعارها في الكويت؟',
    2: 'الضريبة الانتقائية الخليجية. ماذا قرر مجلس الوزراء؟',
    3: 'في السابع والعشرين من أكتوبر، وافق مجلس الوزراء على مشروع مرسوم الاتفاقية الخليجية للضريبة الانتقائية، ورفعه إلى سمو الأمير.',
    4: 'دول الخليج تطبقها منذ عام ألفين وسبعة عشر، أما الكويت فلم تطبقها حتى الآن.',
    5: 'هي ضريبة على سلع تُعدّ ضارة بالصحة، وتُحسب على سعر البيع بالتجزئة.',
    6: 'التبغ ومشتقاته، ومنها السجائر الإلكترونية، بنسبة مئة في المئة.',
    7: 'ومشروبات الطاقة أيضاً، بنسبة مئة في المئة.',
    8: 'والمشروبات الغازية، بنسبة خمسين في المئة.',
    9: 'أما المشروبات المحلّاة، فبنسب متدرجة حسب كمية السكر، ومشروبات الدايت معفاة.',
    10: 'مثال افتراضي: إذا انتقلت الضريبة كاملةً إلى المستهلك، فعلبة طاقة بخمسمئة فلس، قد تصبح بدينار كامل.',
    11: 'الهدف تقليل الاستهلاك وتنويع الإيرادات بعيداً عن النفط، بعائد مقدّر بنحو مئتي مليون دينار سنوياً.',
    12: 'متى التطبيق؟ لا موعد بعد، فهو يحتاج قانوناً محلياً يحدد الآلية والإجراءات.',
    13: 'ما لا نعرفه بعد: موعد التطبيق، والنسب النهائية في الكويت، وكم سترتفع الأسعار فعلياً.',
    14: 'هل هي خطوة إيجابية؟ منظمة الصحة العالمية توصي بهذه الضرائب، والسعودية والإمارات تطبقانها منذ سنوات، وفي المكسيك انخفض شراء المشروبات المحلّاة بعد الضريبة.',
    15: 'خلاصة مِن مصادر: الخطوة إيجابية من حيث المبدأ، صحة أفضل وإيرادات غير نفطية، بشرط قانون واضح وتطبيق متدرج ومراعاة محدودي الدخل.',
    16: 'مِن مصادر. أخبارٌ بمصادرها.',
}
PUNCT = '،,.:؟?!…'


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def segments(x):
    hop = int(0.01 * SR)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9
    db = 20 * np.log10(rms)
    thr = np.percentile(db, 90) - 30
    speech = db > thr
    segs, i = [], 0
    while i < n:
        if speech[i]:
            j = i
            while j < n and speech[j]:
                j += 1
            segs.append([i, j]); i = j
        else:
            i += 1
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < 10:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    merged = [s for s in merged if s[1] - s[0] >= 6]
    return [(a * 0.01, b * 0.01) for a, b in merged]


def phrases(text):
    out, cur, start = [], '', 0
    for i, ch in enumerate(text):
        if ch in PUNCT:
            if cur.strip():
                out.append((start, i))
            cur, start = '', i + 1
        else:
            cur += ch
    if cur.strip():
        out.append((start, len(text)))
    return out


result = {}
for n, text in TTS.items():
    x = load(f'{SP}/narr_f/n{n:02d}.wav')
    segs = segments(x)
    ph = phrases(text)
    def shares_ok():
        tot_t = sum(b - a for a, b in segs); tot_c = sum(c1 - c0 for c0, c1 in ph)
        return all(abs((b - a) / tot_t - (c1 - c0) / tot_c) < 0.22 for (a, b), (c0, c1) in zip(segs, ph))
    if len(segs) == len(ph) and shares_ok():
        mode = 'phrase'
        anchors = []  # (char_index, time)
        for (c0, c1), (t0, t1) in zip(ph, segs):
            anchors += [(c0, t0), (c1, t1)]
    else:
        mode = 'proportional'
        total = sum(b - a for a, b in segs)
        nch = len(text)
        anchors = []
        acc = 0.0
        for a, b in segs:
            anchors += [(round(nch * acc / total), a)]
            acc += b - a
            anchors += [(round(nch * acc / total), b)]
    result[n] = {'mode': mode, 'segments': segs, 'phrases': ph, 'anchors': anchors, 'text': text}
    print(n, mode, 'segs', len(segs), 'phrases', len(ph))
json.dump(result, open(f'{SP}/build/align.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
