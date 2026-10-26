# Second independent review – batch 2

Pieces: haydn76_3_1, haydn76_3_2, haydn76_3_3, haydn76_3_4, d929_1, passacaglia.
I read every sentence of the EN and ZH guides and checked each one against `*_facts.txt`. Where the same problem appears in both languages, it is listed as one finding.

Severity: **ERROR** = a fact is wrong. **MISLEADING** = technically defensible, but a listener would take away something the facts don't support, or a rule is broken in a way the listener notices (an unhedged estimate, "gradual" with no cresc/dim, a headline that contradicts the text). **STYLE** = wording, terminology or editing debris.

---

## haydn76_3_1 (I. Allegro)

### 1. MISLEADING – EN point 10 / ZH point 11 – how the key at the theme return is described
- EN quote: "The computer labels the key just before it as E minor, but from [m. 80] the music follows the opening closely, back in C major."
- ZH quote: "软件把前面几小节的调性估计为 E 小调,但从 [m. 80] 起,音乐几乎和开头一样,回到 C 大调。"
- Problem: the facts label the return itself E minor, not the bars before it. The theme-return line says the key is E minor, and m. 78–79 are labelled E minor in the measure table. The sentence implies the software got the return right and only the lead-in was labelled E minor.
- Evidence: "main theme: Violin 1 78-80, exact, transposed 0 semitones, key E minor"; "78|Part 2|E minor|…", "79|Part 2|E minor|…", "80|Part 2|C major|…".
- Fix EN: "The computer labels the key of these bars as E minor, but the tune is at the opening's pitch, and from [m. 80] the key is C major again."
- Fix ZH: "软件把这几小节的调性估计为 E 小调,但旋律的音高和开头相同;从 [m. 80] 起调性又回到 C 大调。"

### 2. MISLEADING – ZH point 11 – headline contradicts the text and the EN version
- Quote: HEADLINE "变弱变暗,主旋律在 E 小调回来"
- Problem: the headline says the theme comes back in E minor. The text (and EN point 10) says it is at the opening's pitch and that the music is back in C major from m. 80. A listener told "in E minor" will expect a minor-key version of the tune.
- Evidence: "transposed 0 semitones"; "80|Part 2|C major".
- Fix ZH: HEADLINE "变弱变暗,主旋律原样回来"

### 3. STYLE – EN point 6 – suggests a gradual fade, and the sentences are out of order
- Quote: "It gets even quieter, down to pp at [m. 36]. Three instruments seem to play at [m. 36]. Cello probably takes the tune briefly at [m. 33]."
- Problem: no dim is marked. The dynamic is p from m. 32 to 35, then a new pp marking at m. 36, so "gets even quieter" reads as a gradual fade. The m. 33 sentence also comes after the m. 36 sentences.
- Evidence: "32…|p|p", "35…|p|||", "36…|pp|pp"; no <dim> in m. 32–36.
- Fix EN: "Cello probably takes the tune briefly at [m. 33]. At [m. 36] the music is marked even softer, pp, and three instruments seem to play."

### 4. STYLE – EN point 3 – theory claim that isn't in the facts
- Quote: "The computer estimates this as a move to a nearby key."
- Problem: "nearby key" (key relationship) is outside knowledge. The facts only give the key label.
- Fix EN: "The computer estimates this key change."

---

## haydn76_3_2 (II. Poco adagio cantabile)

### 1. STYLE (must fix) – EN point 1 – duplicated sentence
- Quote: "The other three parts accompany it softly. The other three parts accompany it softly."
- Fix EN: "Violin 1 plays the tune on top [m. 0-5]. The other three parts accompany it softly. The tune is plain and steady, so it is easy to remember."

### 2. MISLEADING – EN point 4 – unsupported detail, and the hedging contradicts itself
- Quote: "Now Violin 2 probably has the tune [m. 20-31]. Violin 1 weaves a busier line above it. … The tune itself is clearly in Violin 2. The computer is less sure which violin stands out more."
- Problems: (a) nothing in the facts says Violin 1 is busier or higher. The facts give only "duet" with Vn1 as co-lead. (b) "probably has the tune" and "the tune itself is clearly in Violin 2" contradict each other. The tune is certain (presence 1.0); only the lead heuristic is unsure.
- Evidence: "Var. I (20-40): tune presence [Vn1 0.21, Vn2 1.0 …]; main texture: duet"; "20-39 Vn2 (conf 0.44)"; "21|…|Vn2+Vn1|0.09|duet".
- Fix EN: "Now Violin 2 has the tune [m. 20-31]. Violin 1 plays alongside it, so the two violins sound like a duet. The computer is less sure which violin stands out more. Around [m. 26] the key shifts to D major again."

### 3. MISLEADING – ZH point 12 – headline says gradual
- Quote: HEADLINE "渐弱到极轻,安静收束"
- Problem: the drop to pp at m. 100 is a new marking with no dim before it. The only dim is at m. 104, after a cresc at m. 103. "极轻" is also not the standard term for pp.
- Evidence: "99…|p|||", "100…|pp|pp", "103…|<cresc>", "104…|pp,<dim>".
- Fix ZH: HEADLINE "降到很弱,安静收束"

### 4. STYLE – EN point 12 – headline states an estimate as fact
- Quote: HEADLINE "The busiest moment of the movement"
- Problem: the loudest/busiest point is a heuristic. The text hedges it, but the headline doesn't.
- Fix EN: HEADLINE "The estimated busiest moment of the movement"

### 5. STYLE – ZH (overview, point 1, point 12, glossary) – non-standard dynamic terms
- Quotes: "本乐章基本都很轻柔(p)" / "力度轻柔(p)" / "[m. 100] 起力度降到很轻(pp)" / glossary "p: 轻柔。"
- Problem: the standard terms are 弱 for p and 很弱 for pp. "很轻柔(p)" sounds like pp.
- Fix ZH: "本乐章基本都是弱(p),结尾更弱(pp)。" / "力度为弱(p)。" / "[m. 100] 起力度降到很弱(pp)。" / glossary "p: 弱。"

### 6. STYLE – ZH overview – "all about 21 measures" doesn't fit Var. IV
- Quote: "主题和每个变奏都差不多长(约21小节)"
- Evidence: "Var. IV: 80-104 (25 measures)".
- Fix ZH: "主题和前三个变奏都约21小节,最后一个变奏稍长(25小节),所以很容易分辨。"

### 7. STYLE – ZH point 2 – one measure reference for several accents
- Quote: "后半段出现几处突然加重的音(fz)[m. 12]。然后马上回到轻柔。"
- Evidence: fz at m. 12, 13, 16, 17; p at m. 14, 18.
- Fix ZH: "后半段出现几处突然加重的音(fz)[m. 12-13, 16-17],每次之后马上回到弱(p)。"

### 8. STYLE – ZH glossary – fz definition includes this movement's context
- Quote: "fz: 突然加重的一个音,然后马上回到轻柔。"
- Problem: "then back to soft" is not part of what fz means. It only happens to fit here.
- Fix ZH: "fz: 某个音突然加重。"

### 9. STYLE – EN point 2 and glossary – "nearby key"
- Quotes: "This is a nearby key." / glossary "D major: A nearby key. …"
- Problem: key relationships are outside knowledge. The facts only say D major is visited in each section.
- Fix EN: delete "This is a nearby key." Glossary: "D major: A second key the music visits in the middle of the theme and of every variation, before returning to G major."

### 10. STYLE – ZH point 3 – leans further than EN and the facts
- Quote: "所以可以理解为两把小提琴共同主导。"
- Problem: the tune is clearly in Vn2 (presence 1.0, lead share 0.95). Only the per-measure lead confidence is low. EN says the tune is clearly in Violin 2.
- Fix ZH: "主题清楚地在第二小提琴里;只是软件不太确定两把小提琴哪一把听起来更突出。"

---

## haydn76_3_3 (III. Menuetto)

### 1. MISLEADING – EN point 3 – unhedged headline that also contradicts the text
- Quote: HEADLINE "The busiest, loudest point"; TEXT "It is marked f, like the bars around it."
- Problem: the headline states a heuristic as fact and calls it the loudest point. The text then says it is no louder than its neighbours.
- Evidence: "LOUDEST/BUSIEST POINT (heuristic): measure 13 (f, Part 1)"; m. 0–25 are all f.
- Fix EN: HEADLINE "The estimated busiest point"

### 2. MISLEADING – EN overview and glossary, ZH overview and glossary – Trio called a "middle" section; ZH says the minuet comes back
- Quotes: EN overview "a contrasting middle section called the Trio"; EN glossary "The contrasting middle section of a minuet."; ZH overview "中段(Trio)"; ZH glossary "小步舞曲中与主体形成对比的中段,之后再回到小步舞曲。"
- Problem: in the facts the Trio is the last section (56–100). Nothing comes after it. "Middle" and "之后再回到小步舞曲" bring in outside knowledge about the minuet form. The ZH glossary also contradicts ZH point 13 ("乐章在 [m. 100] … 结束") and the ZH 主调 glossary entry ("这份乐谱最后是中段 Trio").
- Evidence: "Trio: 56-100 (45 measures, repeated)"; last_label "100".
- Fix EN: overview "…a main section (Part 1) and a contrasting second section called the Trio."; glossary "Trio: The contrasting second section of this movement. Here it is much softer."
- Fix ZH: overview "第一部分(Part 1)和对比性的第二段(Trio)"; glossary "Trio:本乐章中与第一部分形成对比的第二段,这里大多更轻。"

### 3. MISLEADING – ZH point 2 – overstates how uncertain the lead is
- Quote: "这一段第一小提琴的领奏地位不太确定,更像是大家共享。"
- Problem: only m. 7 has confidence below 0.4. m. 8–12 are Vn1 alone at 0.47–1.0 with no co-lead. EN doesn't make this claim.
- Evidence: "7|…|Vn1|0.35", "8|…|Vn1|0.49", "9|…|0.59", "10|…|0.51", "11|…|0.47", "12|…|1.0".
- Fix ZH: "这一段第一小提琴大多仍在领奏,只有 [m. 7] 判断把握不大。"

### 4. STYLE – EN point 6 – the contrast with the opening is only partly true
- Quote: "This time the other parts join in at once [m. 32], instead of Violin 1 starting alone."
- Problem: at m. 33 Violin 1 is solo again.
- Evidence: "32|…|melody + accompaniment", "33|…|solo".
- Fix EN: "This time the other parts join in at once [m. 32], although Violin 1 is briefly alone again at [m. 33]."

### 5. STYLE – EN point 14 – "unison" drops "or octaves"
- Quote: "The Trio ends with the instruments in unison, all playing the same notes [m. 100]."
- Evidence: "100|…|unison/octaves".
- Fix EN: "The Trio ends with the instruments playing the same notes, in unison or octaves [m. 100]."

### 6. STYLE – EN points 2 and 11 – measure references outside the point's range
- Quotes: P2 [m. 7-12] "…G major, a brighter neighbouring key [m. 9-21]."; P11 [m. 68-75] "The key returns to E major [m. 71-78]."
- Problem: the player highlights the point's range, so these references go past it. "Neighbouring key" is also outside knowledge.
- Fix EN: P2 "Then it settles in G major, which sounds brighter [m. 9-12]." P11 "The key returns to E major [m. 71]."

### 7. STYLE – ZH point 3 – measure given twice
- Quote: "第 13 小节是软件判断的最响最忙之处 [m. 13]。"
- Fix ZH: "在 G 大调里,软件估计这里是最响、最忙的地方 [m. 13]。"

---

## haydn76_3_4 (IV. Finale)

### 1. ERROR – ZH point 8 – lead alternation at the wrong measures; references after the wrong full stop
- Quote: "[m. 87-91] 第一、第二小提琴交替担任主角,但判断并不十分确定。中间短暂触及 C 小调。[m. 92-93] 之后又回到 Ab 大调。[m. 97-105]"
- Problems: (a) in m. 87–91 the lead is Vn2 for one bar, then Vn1. The violins trade the lead at m. 98–103, which is what EN point 8 says. (b) "[m. 92-93]" sits after the C-minor sentence's full stop, and "[m. 97-105]" hangs at the very end.
- Evidence: "87|…|Vn2|0.38", "88|…|Vn1|0.72", "89|…|Vn1|0.64", "90|…|Vn1|0.64", "91|…|Vn1+Va|0.19"; spans "98-99 Vn2; 100 Vn1; 101 Vn2; 102 Vn1; 103 Vn2"; keys "C minor: 92-93", "Ab major: 97-105".
- Fix ZH: "这一长段落以 Ab 大调为主 [m. 87-91]。中间短暂触及 C 小调 [m. 92-93],之后又回到 Ab 大调 [m. 97-105]。[m. 98-103] 第一、第二小提琴交替担任主角,但判断并不十分确定。"

### 2. MISLEADING – ZH point 5 – loudest point stated as fact
- Quote: "第一部分最响、最忙的地方在 [m. 56]。"
- Problem: this is a heuristic estimate, and m. 56 is marked f like the bars around it. EN hedges it ("The computer estimates…").
- Evidence: "LOUDEST/BUSIEST POINT (heuristic): measure 56 (f, Part 1)"; m. 46–67 all f.
- Fix ZH: "软件估计本乐章最响、最忙的地方在 [m. 56],力度和周围一样是强(f)。"

### 3. MISLEADING – EN point 13 – "quiet final section"
- Quote: HEADLINE "A new, quiet final section"
- Problem: the section starts p but is f from m. 157 to the end (m. 157–188). The guide's own point 14 says "It stays loud."
- Evidence: "151…|p|p"; "157…|f|f"; m. 159–188 all f.
- Fix EN: HEADLINE "A new final section begins quietly"

### 4. MISLEADING – ZH point 11 – headline says gradual; non-standard pp term
- Quote: HEADLINE "转向 F 小调和 Db 大调,声音越来越轻"; TEXT "力度降到最弱(pp)"
- Problem: m. 126–132 are p, then a new pp marking at m. 133. No dim is marked, so "越来越轻" is unsupported. pp should be 很弱.
- Evidence: "132…|p|||", "133…|pp|pp"; no <dim> in 123–136.
- Fix ZH: HEADLINE "转向 F 小调和 Db 大调,再降到很弱"; TEXT "[m. 133] 到达 Db 大调,力度降到很弱(pp),这是本乐章最轻的地方。"

### 5. STYLE – ZH point 3 – too uncertain for m. 18
- Quote: "[m. 18-19] 中提琴可能暂时领头,但这个判断把握不大,更像是多件乐器共同参与。"
- Evidence: "18|…|Va|0.99"; "19|…|Va+Vc|0.0".
- Fix ZH: "[m. 18] 中提琴清楚地领头,[m. 19] 则更像中提琴和大提琴共同参与。"

### 6. STYLE (must fix) – EN point 9 – duplicated content
- Quote: "It stays loud. The first violin mostly leads. It stays loud, with the first violin mostly in front, right up to the return of the opening tune."
- Fix EN: "The key returns to C minor [m. 110]. It stays loud, with the first violin mostly in front, right up to the return of the opening tune."

### 7. STYLE (must fix) – ZH point 6 – duplicated sentence
- Quote: "[m. 68] 突然变弱(p),第一小提琴继续带着旋律。[m. 68] 突然变弱(p),一直轻到 [m. 71a]。"
- Fix ZH: "[m. 68] 突然变弱(p),一直弱到 [m. 71a],第一小提琴继续带着旋律。"

### 8. STYLE – EN point 2 – "gets louder" for a sudden f
- Quote: "It returns to C minor and gets louder [m. 12-17]."
- Evidence: "12|…|f|f"; no cresc.
- Fix EN: "It returns to C minor and turns loud at [m. 12]."

### 9. STYLE – ZH point 2 – headline places the change to f inside a range where it is already in force
- Quote: HEADLINE "大提琴短暂接过旋律,声音转强" for [m. 13-17]
- Evidence: the f marking is at m. 12. m. 13 is already f.
- Fix ZH: HEADLINE "大提琴短暂接过旋律,保持强奏"

---

## d929_1 (Schubert, I. Allegro)

### 1. MISLEADING – EN point 7 – "fades" with no dim marked
- Quotes: HEADLINE "The first part fades out in F major"; TEXT "The sound fades to very soft by [m. 131]."
- Evidence: "130…|p|||", "131…|pp|p,pp"; the last cresc is at m. 126 and no dim follows.
- Fix EN: HEADLINE "The first part ends very softly in F major"; TEXT "The sound drops to very soft at [m. 131]."

### 2. MISLEADING – EN point 12 / ZH point 11 – "build-up" with no cresc; loudest point not marked as an estimate
- EN quotes: HEADLINE "Build-up to the loudest point"; TEXT "It reaches one of the loudest and busiest moments of the movement at [m. 254]."
- ZH quotes: HEADLINE "紧张攀升,到达最响的时刻之一"; TEXT "到 [m. 254] 达到本乐章最响、最忙的时刻之一(ff)"
- Problem: m. 249 is a sudden f with no cresc until m. 254 itself, so "build-up / 攀升" implies a gradual rise that isn't marked. The loudest point is also not called an estimate.
- Evidence: "248…|p|||", "249…|f|f", 250–253 f with no markings, "254…|ff|ff,sf,<cresc>,<dim>"; "LOUDEST/BUSIEST POINT (heuristic): measure 254".
- Fix EN: HEADLINE "A loud stretch to the estimated peak"; TEXT "From [m. 249] the music turns loud in F-sharp minor. The computer estimates [m. 254] as the loudest and busiest point of the movement, marked ff, in B minor."
- Fix ZH: HEADLINE "转强,到达估计的最高点"; TEXT "从 [m. 249] 起突然变强(f),调性在升F小调。软件估计 [m. 254] 是本乐章最响、最忙的地方(ff),调性为B小调。"

### 3. MISLEADING – EN point 15 – "build-up" over sudden dynamic changes
- Quote: HEADLINE "Final return to E-flat: a loud build-up, then a soft close"
- Problem: there is no cresc in m. 616–644. The dynamics jump: pp → f (624) → p (627) → ff (632) → p (637) → ff (638) → p (642).
- Fix EN: HEADLINE "Final return to E-flat: sudden loud outbursts, then a soft close"

### 4. MISLEADING – ZH point 14 – headline "渐强" with no cresc
- Quote: HEADLINE "最长的新段落开始,声音渐强"
- Evidence: f is marked at m. 347 and ff at m. 355, both as new markings. The first cresc marks come later (m. 360, 362).
- Fix ZH: HEADLINE "最长的新段落开始,声音转强"

### 5. STYLE – ZH point 9 – pp described as just "弱音", unlike EN
- Quote: "随后很快回落到弱音,并在F大调中再次变响。"
- Evidence: "181…|pp|pp". EN says "very soft".
- Fix ZH: "随后在 [m. 181] 突然降到很弱(pp),并在F大调中再次变响 [m. 187]。"

### 6. STYLE – ZH point 6 – non-standard pp term in the headline
- Quote: HEADLINE "极弱的B小调与G大调"
- Fix ZH: HEADLINE "很弱的B小调与G大调"

### 7. STYLE – ZH point 16 – "过渡" (transition) is a label the facts don't give
- Quote: "(前面 [m. 612-615] 是一小段过渡)"
- Evidence: "Section 12 (new key signature): 612-615 (4 measures)".
- Fix ZH: "(前面 [m. 612-615] 是很短的一段)"

### 8. STYLE – EN point 8 / ZH point 12 – silences stated as fact in an OCR score
- Quotes: EN "After a short silence (all parts are tacet)…"; ZH "在 [m. 308] 停下来。"
- Problem: the score is poor OCR, and the method notes say empty measures exist. The passacaglia guide hedges such bars; this one doesn't.
- Fix EN: "After a short silence in the score (which may be a recognition gap), the violin plays alone…"; ZH "在 [m. 308] 乐谱显示为空小节(可能是识别错误)。"

### 9. STYLE – EN point 6 – "far-off keys" is a key-distance judgement not in the facts
- Quote: HEADLINE "A hush: far-off keys"
- Fix EN: HEADLINE "A hush in new keys"

---

## passacaglia (Handel–Halvorsen)

### 1. MISLEADING – EN point 3 / ZH point 3 – "suddenly softer" although a dim leads into it
- EN quote: HEADLINE "Variations 2–3: suddenly softer and more flowing"
- ZH quote: "第二变奏骤然转为中弱 [m. 9-12]。"
- Problem: m. 8 carries a dim marking, and EN point 2 itself says the music "eases off at the end [m. 8]". So the drop to mp is prepared, not sudden, and the two points contradict each other.
- Evidence: "8|Variation 1|…|f|<dim>"; "9|Variation 2|…|mp|…".
- Fix EN: HEADLINE "Variations 2–3: softer and more flowing"
- Fix ZH: "第二变奏转为中弱(mp)[m. 9-12]。"

### 2. STYLE – EN point 3 – "the tune is shared" in Variation 3
- Quote: "In Variation 3 the tune is shared between both players."
- Problem: the lead is shared, but the violin carries none of the theme's notes. In this guide "the tune" means the theme.
- Evidence: "Variation 3 (13-16): tune presence [Vn 0.0, Va 0.36]; tune mostly in: not clearly in one part"; "13|…|Vn+Va|0.14".
- Fix EN: "In Variation 3 the lead is shared between both players."

### 3. STYLE – EN point 14 / ZH point 14 – loudest point not marked as an estimate
- Quotes: EN "The two players then drive to the loudest point [m. 90]."; ZH "力度升到最强,最响处在 [m. 90]。"
- Note: the fff marking at m. 90 supports this, so it is a rule compliance issue only.
- Fix EN: "The two players then reach fff, extremely loud, which the computer estimates as the loudest point [m. 90]."
- Fix ZH: "力度升到最强(fff),软件估计最响处在 [m. 90]。"

### 4. STYLE – ZH points 12–13 – ff called "极强", so ff and fff blur together
- Quotes: "力度猛然升到极强 [m. 79]"; "第二十变奏保持极强"
- Problem: the standard term for ff is 很强. Point 14 then uses "最强" for fff.
- Fix ZH: "力度猛然升到很强(ff)[m. 79]。" / "第二十变奏保持很强(ff)"

### 5. STYLE – EN point 1 – "stay close to its tune"
- Quote: "…and the early ones stay close to its tune."
- Problem: only Variation 1 keeps much of the tune (Vn 0.53). Variation 2 is 0.38 and Variation 3 is 0.0/0.36. What stays closer is the harmony (0.53, 0.75). The overview says "close to the theme", which is safer.
- Fix EN: "…and the early ones stay closer to it than the later ones."

---

## Checked and found clean

- Hedging of leads with confidence below 0.4: correct in all six guides, apart from the over-hedging noted above.
- Section names, key labels and theme transpositions match the facts. The exceptions are haydn76_3_1 item 1 and haydn76_3_3 item 2.
- No dates, people or history about the hymn appear. The "like a hymn" texture analogy is generic and was left alone.
- 全曲 is used only in the passacaglia guide. The Haydn and Schubert ZH guides use 本乐章/全乐章 correctly.

## Counts

| Piece | ERROR | MISLEADING | STYLE |
|---|---|---|---|
| haydn76_3_1 | 0 | 2 | 2 |
| haydn76_3_2 | 0 | 2 | 8 |
| haydn76_3_3 | 0 | 3 | 4 |
| haydn76_3_4 | 1 | 3 | 5 |
| d929_1 | 0 | 4 | 5 |
| passacaglia | 0 | 1 | 4 |
| **Total** | **1** | **15** | **28** |
