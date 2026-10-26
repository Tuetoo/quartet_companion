# Second independent review – batch 1

Pieces: op18no5_1–4 (Beethoven Op. 18 No. 5, expert harmony) and k525_1–4 (Mozart K. 525, OMR score, auto keys).
Source: /tmp/claude-0/review/digest2/. Every sentence of both languages was checked against `P_facts.txt`.

Severity:
- **ERROR**: a factual statement the facts contradict, or broken text that readers will see.
- **MISLEADING**: technically defensible, but it gives a wrong impression, such as a gradual change with no cresc/dim marking, an unhedged estimate, or an auto key stated as fact.
- **STYLE**: wording, terminology, ordering or consistency.

---

## op18no5_1 (I. Allegro)

### 1. EN, Point 3. MISLEADING
- Quote: "Then E minor returns, getting very quiet [m. 33-36]."
- Problem: This implies a gradual fade. No dim is marked, and the passage starts loud. The dynamic steps are f (m. 32–33), then p (m. 34), then pp (m. 36).
- Evidence: `32|…|f|f`, `33|…|f|||`, `34|…|p|p,sf`, `36|…|pp|pp`. No <dim> in 33–36.
- Fix: "Then E minor returns. It is loud at first [m. 33], then drops to soft [m. 34] and to very soft [m. 36]."

### 2. EN, Point 8 headline. MISLEADING
- Quote: "Quiet D major, with a loud peak at bar 101"
- Problem: The headline presents the heuristic loudest point as fact. By marking, m. 101 is only f, the same level as m. 82–87.
- Evidence: `LOUDEST/BUSIEST POINT (heuristic): measure 101`. `82|…|f|f` through `87|…|f`.
- Fix: "Quiet D major, with an estimated loud peak at bar 101"

### 3. ZH, Point 8 headline. MISLEADING
- Quote: "D 大调里先轻后响,最响点在第 101 小节"
- Problem: The estimate is stated as fact. "先轻后响" also leaves out the return to p at m. 103–107, which falls inside this point's range (the EN version does mention it).
- Evidence: heuristic line as in #2. `103|…|p|p`, `104|…|p|p`, `107|…|p`.
- Fix: "D 大调:轻—响—轻,估计第 101 小节最响"

### 4. ZH, Point 8 text. STYLE
- Quote: "先是很轻的 pp,轻声中,“旋律加伴奏”的小节和各声部独立进行的小节交替出现 [m. 89-98]。"
- Problem: The editing left a duplicated phrase: "很轻的 pp" and "轻声中" say the same thing. The text also never mentions the drop back to p after m. 101.
- Evidence: `89–98 … pp`, `103|…|p|p`.
- Fix: "先是很弱(pp),“旋律加伴奏”的小节和各声部独立进行的小节交替出现 [m. 89-98]。……之后又回到弱(p),只剩二重奏和三重奏 [m. 103-107]。"

### 5. EN, Point 11. STYLE
- Quote: "Just before this point, the first violin keeps the tune going [m. 140-150]."
- Problem: This is a dangling reference to bars outside the point's range (151–163). It reads as an editing leftover.
- Evidence: Point range is m. 151-163. The facts show Vn1 lead and melody + accompaniment at m. 140–150.
- Fix: Drop the sentence, or extend the point range to 140–163 and write: "The first violin keeps the tune going [m. 140-150]."

### 6. EN, Point 12. STYLE
- Quote: "For two bars it brightens to C major [m. 170-172]."
- Problem: "two bars" does not match the three-bar reference. In the measure table, only m. 171–172 are C major.
- Evidence: `170|…|A minor`, `171|…|C major`, `172|…|C major`.
- Fix: "For two bars it brightens to C major [m. 171-172]."

### 7. EN, Point 12. MISLEADING
- Quote: "It then returns to A minor and fades to very soft [m. 173-176]."
- Problem: No dim is marked. m. 172–173 are loud (f), then the music drops suddenly to p (m. 174) and pp (m. 176). "fades" hides the loud bars and suggests a gradual change.
- Evidence: `172|…|f|f`, `173|…|f|||`, `174|…|p|p,sf`, `176|…|pp|pp`.
- Fix: "It returns to A minor loudly [m. 173], then drops to soft and finally very soft [m. 174-176]."

### 8. ZH, Point 12. MISLEADING
- Quote: "第 159 到 164 小节的音乐像第一部分开头那段,又一路渐强。" and "随后回到 A 小调并减弱到 pp [m. 173-176]。"
- Problem:
  - Cresc is marked only at m. 161–162. It reaches f at m. 163, then drops to p at m. 164, so "一路渐强" is wrong for 159–164.
  - "减弱到 pp" again implies a gradual change, while m. 173 is f.
- Evidence: `161|…|<cresc>`, `162|…|<cresc>`, `163|…|f|f`, `164|…|p|p`. `173|…|f`, `174|…|p`, `176|…|pp`.
- Fix: "第 159 到 164 小节的音乐和第一部分第 19-24 小节相似:第 161-162 小节渐强,第 163 小节到强(f),第 164 小节又回到弱。……随后回到 A 小调,先强 [m. 173],再突然变弱,第 176 小节到很弱(pp)。"

### 9. EN, Point 13. STYLE
- Quote: "Loud accents burst out [m. 188-198]."
- Problem: This glosses over the soft bars m. 189–190 inside that span. Point 5 describes the parallel passage correctly.
- Evidence: `188|…|f|f`, `189|…|p|p`, `190|…|p`, `191|…|f|f`, `192–198 … sf`.
- Fix: "A loud bar [m. 188] is followed by soft and loud in turn [m. 189-191], then a run of loud accents [m. 192-198]."

### 10. ZH, Point 4. MISLEADING
- Quote: "第 37 小节转到 E 大调,色彩重新明亮。但声音降到很轻的 pp(很弱) [m. 37]。"
- Problem: The pp already starts at m. 36, so the volume does not "drop" at m. 37. "很轻的 pp(很弱)" is also redundant.
- Evidence: `36|…|pp|pp`, `37|…|pp|pp,<cresc>`.
- Fix: "第 37 小节转到 E 大调,色彩重新明亮,但声音仍保持很弱(pp)[m. 37]。"

### 11. ZH, glossary and text terminology. STYLE
- Quotes:
  - Glossary: "pp 是很轻,p 是轻,f 是响"
  - Point 1: "轻声(p)"
  - Point 6: "p(轻)"
- Problem: These are not the standard terms (强/弱/很弱). They are also inconsistent with "强(f)" and "pp(很弱)" elsewhere in the same guide.
- Fix: Glossary: "pp 是很弱,p 是弱,f 是强,sf 是突然加重某个音。" Use 弱(p) throughout the text.

**Checked and clean:** the EN overview and Points 1, 2, 4, 5, 6, 7, 9, 10, 14, 15. The ZH Points 1–3, 5–7, 9–11, 13–15 are clean apart from the terminology in #11.

---

## op18no5_2 (II. Menuetto)

### 1. EN, Overview. MISLEADING
- Quote: "The Trio stays soft but has a sharp accent in almost every bar."
- Problem: sf appears in only 12 of the Trio's 25 bars (m. 82–87 and m. 98–103). Bars 81 and 88–97 have none.
- Evidence: measure table, m. 81–105, "new markings" column.
- Fix: "The Trio stays soft but has two runs of sharp accents, one bar after another."

### 2. EN, Overview. MISLEADING
- Quote: "The Menuetto is mostly soft and has one sudden loud peak."
- Problem: The ff at m. 44 is prepared by a crescendo marked at m. 39, which Point 7 says itself. "Sudden" therefore contradicts Point 7.
- Evidence: `39|…|<cresc>`, `44|…|ff|ff`.
- Fix: "The Menuetto is mostly soft, with one very loud peak after a crescendo."

### 3. EN, Point 2. STYLE
- Quote: Headline "A first brightening shift to E major" vs. text "It sounds like a small step sideways, not a big change of mood."
- Problem: The headline and the text pull in opposite directions.
- Fix: Headline: "A first, small step to E major"

### 4. EN, Point 3. STYLE
- Quote: "The viola plays the main theme, one octave lower [m. 12-15]. It is exactly the same tune, one octave lower."
- Problem: The editing left the phrase "one octave lower" twice.
- Fix: "The viola plays the main theme, one octave lower [m. 12-15]. It is exactly the same tune."

### 5. EN, Point 8. STYLE
- Quote: Headline "The loudest moment of the Menuetto" and text "This is the peak of the Menuetto."
- Problem: The ff marking supports "loudest". But "peak/busiest" is a heuristic, and the rule says the loudest point must be framed as an estimate.
- Evidence: `LOUDEST/BUSIEST POINT (heuristic): measure 44 (ff)`.
- Fix: "This is the only ff, and the analysis estimates it as the peak of the Menuetto."

### 6. ZH, Point 8. STYLE
- Quote: Headline "全乐章最响一刻,随后突然静默" and text "[m. 44] 是这个乐章最响、最忙的地方"
- Problem: Same as #5. "最忙" is a heuristic stated as fact.
- Fix: "[m. 44] 是本乐章唯一的很强(ff),分析估计这里也是最忙的地方。"

### 7. EN, Point 12. STYLE
- Quote: "No one part clearly leads here. The lead is shared, perhaps with the second violin."
- Problem: "shared, perhaps with the second violin" does not make sense, because it is not clear who shares it with whom.
- Evidence: `82|Vn2+Va|0.0`, `83|Vn2+Va|0.0`, `84|Vn2|0.48`, `86|Vn2+Va|0.0`.
- Fix: "No one part clearly leads here. The lead is probably shared by the second violin and the viola."

### 8. ZH, terminology. STYLE
- Quotes:
  - Overview: "大部分时间很轻"
  - Point 1: "音量轻(p)"
- Problem: "很轻" reads as pp (很弱). The movement is p almost throughout, and pp never appears. Standard terms are 弱(p) and 很弱(pp).
- Evidence: `dynamic in force` is p everywhere except m. 44–45 (ff) and m. 72 (f).
- Fix: "也请留意音量的变化:大部分时间是弱(p),只有少数几处突然变强。" and "……音量弱(p)[m. 0]。"

### 9. ZH, Point 12. MISLEADING
- Quote: "一开始几件乐器同音或同八度演奏。"
- Problem: "同八度" literally means "in the same octave", which is the opposite of playing in octaves. The standard term is 齐奏.
- Evidence: `81|Trio|…|unison/octaves`.
- Fix: "一开始几件乐器齐奏(同音或相隔八度)。"

**Checked and clean:** the EN Points 1, 4, 6, 7, 9, 10, 11, 13, 14. The ZH Points 1–7, 9–11, 13–15 are clean apart from #8.

---

## op18no5_3 (III. Andante cantabile, variations)

### 1. EN, Glossary. STYLE
- Quote: "Two or more instruments play the same notes, or the same notes at different heights, or the same notes at different heights."
- Problem: The editing left a phrase duplicated.
- Fix: "Two or more instruments play the same notes, at the same height or at different heights."

### 2. EN, Point 3. MISLEADING
- Quote: "The other parts add more small notes than before."
- Problem: The density figure (1.52x) is for the whole variation, not for the accompanying parts. The facts do not say which parts add the notes.
- Evidence: `Var. 1 … note density vs theme: 1.52x` is not split by part.
- Fix: "There are more notes than before: about one and a half times as many as in the theme." Merge this with the last sentence.

### 3. EN, Point 4. STYLE
- Quote: "Later the tune passes around the middle parts [m. 26-31], and the leader is only probably Viola or Violin 2."
- Problem:
  - "only probably" is awkward.
  - The sentence treats the heuristic lead as the theme tune. The facts say the Var. 1 tune is mostly in the cello.
- Evidence: `Var. 1 … tune mostly in: Cello`. Leads 26–31 are Vn2 (0.39), Va (0.59) and Vn2 (0.36).
- Fix: "Later the lead seems to pass between the middle parts [m. 26-31], probably the viola and second violin, but this is uncertain."

### 4. EN, Point 6 headline. STYLE
- Quote: "Variation 3: the busiest, tune hidden in the middle"
- Problem:
  - "busiest" here means note density. It can be confused with the movement's estimated "loudest/busiest point", which is at m. 84 in Var. 5.
  - "hidden in the middle" goes beyond the facts, which say the tune is not clearly in one part.
- Evidence: `Var. 3 … note density 2.55x; tune mostly in: not clearly in one part`. `LOUDEST/BUSIEST POINT … 84`.
- Fix: "Variation 3: the most notes, the tune spread between parts"

### 5. ZH, terminology. STYLE
- Quotes:
  - Glossary: "p是轻,pp是极轻,f是强"
  - Point 10: "声音轻柔(pp)"
  - The text elsewhere uses "弱(p)" and "极弱(pp)".
- Problem: The terms are inconsistent within the guide and are not the standard ones (弱/很弱).
- Fix: Glossary: "p是弱,pp是很弱,f是强。" Point 10: "声音很弱(pp)。" Replace 极弱 with 很弱 in Points 4, 7 and 12.

**Checked and clean:** the EN overview and Points 1, 2, 5, 7–14. The ZH overview and Points 1–9, 11–13 are clean apart from #5. The claim "全乐章唯一的小调段落" is supported by the key plan.

---

## op18no5_4 (IV. Allegro)

### 1. EN, Point 10. ERROR
- Quote: Headline "C major build-up and the loudest peak" and text "The loudest and busiest point is at [m. 128]."
- Problem:
  - The loudest point is stated as fact, but it is only a heuristic. Every bar from m. 114 to m. 131 is ff, so the markings do not single out m. 128.
  - "build-up" has no support: there is no cresc in m. 117–131.
- Evidence: `LOUDEST/BUSIEST POINT (heuristic): measure 128 (ff)`. `114–131 … ff`. No <cresc> in 114–131.
- Fix:
  - Headline: "C major, very loud, and the estimated peak"
  - Text: "The analysis estimates the loudest and busiest point at [m. 128]."

### 2. EN, Overview. STYLE
- Quote: "Listen for the tune, for sudden jumps between very soft and very loud…"
- Problem: The actual jumps are loud to very soft (f to pp at m. 34–36, 65–67, 205–207, 236–238) and very loud to soft (ff to p at m. 131–132). There is no jump between pp and ff.
- Fix: "Listen for the tune, and for sudden drops from loud to very soft."

### 3. EN, Overview. STYLE
- Quote: "This is a quick finale in A major."
- Problem: "finale" is outside knowledge, because the facts give only "IV. Allegro".
- Fix: "This is a quick movement in A major."

### 4. EN, Point 13. STYLE
- Quote: "A short viola solo introduces it, as before [m. 167]."
- Problem: This repeats Point 12 word for word in content, and m. 167 is outside this point's range (168–183).
- Fix: Delete the sentence. Point 12 already says it.

### 5. ZH, Point 9 headline. STYLE
- Quote: "持续极强(ff),第 128 小节最密集"
- Problem: The headline states the heuristic as fact, although the text correctly says "按分析".
- Fix: "持续很强(ff),估计第 128 小节最密集"

### 6. ZH, terminology. STYLE
- Quotes:
  - Glossary: "pp是极弱,f是强,ff是极强"
  - Text: "极弱(pp)" and "极强(ff)"
- Problem: The standard terms are 很弱 and 很强.
- Fix: "p是弱,pp是很弱,f是强,ff是很强。" Replace these terms in Points 4, 5, 9, 10 and 13.

**Checked and clean:** the EN Points 1–9, 11, 12, 14–16. The ZH overview and Points 1–8, 10–15 are clean apart from #6.

---

## k525_1 (I. Allegro)

### 1. EN, Point 4. MISLEADING
- Quote: "It gets very loud. Just before, the viola and cello probably share the lead for a moment [m. 23-24]."
- Problem: "Just before" points to the wrong place. The ff starts at m. 21, and m. 23–24 come after it. The sentence was probably meant to sit before the m. 25 sentence.
- Evidence: `21|…|ff|f,ff,sf`, `23|Va+Vc|0.0`, `24|Va+Vc|0.0`.
- Fix: "It gets very loud [m. 21]. Then the viola and cello probably share the lead for a moment [m. 23-24]."

### 2. EN, Point 11. MISLEADING
- Quote: Headline "Soft music returns, fading to very soft" and text "Listen for the music fading to very soft around [m. 94]."
- Problem:
  - No dim is marked, so the pp at m. 94 is a sudden one-bar marking.
  - The music is back to p at m. 95, so the point does not end very soft.
- Evidence: `94|…|pp|p,pp`, `95|…|p|p`. No <dim>.
- Fix:
  - Headline: "Soft music returns, with a moment of very soft"
  - Text: "Listen for a brief very soft moment at [m. 94]."

### 3. EN, Point 13. STYLE
- Quote: "At [m. 111] it turns loud. The first violin probably leads at [m. 107]."
- Problem: The bar references go backwards in time. Also, m. 107 has lead confidence 1.0, so the hedge "probably" is not needed.
- Evidence: `107|…|Vn1|1.0`.
- Fix: "The music is soft at first, and the first violin clearly leads at [m. 107]. At [m. 111] it turns loud."

### 4. ZH, terminology. STYLE
- Quotes:
  - Point 4: "极弱(pp)"
  - Point 5: "极强(ff)"
  - Glossary: "ff是很强,pp是很弱"
- Problem: The text does not match this guide's own glossary or the standard terms.
- Fix: "然后在 [m. 19] 有一瞬间很弱(pp)" and "力度跳到很强(ff)". Make the same change in Point 12.

**Checked and clean:** the EN overview and Points 1–3, 5–10, 12, 14, 15. The ZH guide is clean apart from #4. Its m. 83–94 vs m. 10–19 comparison is supported by the chord table.

---

## k525_2 (II. Romanze)

### 1. EN, Point 11 headline. MISLEADING
- Quote: "Light returns, then the loudest moment"
- Problem: The heuristic is stated as fact. m. 63 is f, the same level as m. 5–9, 16–18, 37–41, 60–64 and 71–74. The text does hedge it.
- Evidence: `LOUDEST/BUSIEST POINT (heuristic): measure 63 (f)`.
- Fix: "Light returns, then the estimated loudest moment"

### 2. ZH, Point 10 headline. MISLEADING
- Quote: "全乐章最响最忙的地方"
- Problem: Same as #1.
- Fix: "估计是本乐章最响、最忙的地方"

### 3. ZH, Point 11 headline. MISLEADING
- Quote: "主旋律回来了,这次在G大调"
- Problem: An auto-estimated key is stated as fact. The text itself says the theme returns at the same pitch as the opening (C major) and that the G major label is only an estimate. The EN version hedges this.
- Evidence: `main theme: Violin 1 69-71, exact, transposed 0 semitones, key G major`. `harmony: Estimated automatically`.
- Fix: "主旋律原样回来了"

### 4. ZH, Point 8. STYLE
- Quote: "从 [m. 43] 起进入C小调([m. 47] 第六部分开始,仍是C小调和轻声),整体变得更暗、更内省,保持轻声。"
- Problem: The parenthesis is inserted in the middle of the sentence, and "轻声" is said twice. This is an editing artifact.
- Fix: "从 [m. 43] 起进入C小调,整体变得更暗、更内省,一直保持弱(p)。[m. 47] 第六部分开始,仍在C小调。"

### 5. ZH, terminology. STYLE
- Quotes:
  - Point 1: "乐章一开始就很轻"
  - Glossary: "pp是很轻,p是轻,f是响"
- Problem: "很轻" reads as pp, but the opening is p. The standard terms are 弱/很弱/强.
- Fix: "乐章一开始是弱(p)……" Glossary: "pp是很弱,p是弱,f是强。"

### 6. EN, Point 10. STYLE
- Quote: "It stays in C minor and stays soft until [m. 56]."
- Problem: This suggests the dynamic changes at m. 56. In fact the key changes at m. 57, and the music stays soft until m. 59 (f at m. 60).
- Evidence: `57|…|C major|…|p|p`, `60|…|f|f`.
- Fix: "It stays soft, and in C minor until [m. 56]."

**Checked and clean:** the EN overview and Points 1–9, 12, 13. The ZH overview and Points 2–7, 9, 12, 13 are clean apart from #5.

---

## k525_3 (III. Menuetto)

### 1. ZH, Point 8 headline. ERROR (broken text)
- Quote: "第四部分:强奏重现,第四部分:强奏重现"
- Problem: The headline is duplicated, and readers will see it.
- Fix: "第四部分:强奏重现"

### 2. EN, Point 5 CLAIMS. STYLE
- Quote: `{"type": "lead", "measure": "17", "value": "Vc"}`
- Problem: Every other claim uses full part names ("Cello"). An automatic claim checker may reject this one.
- Fix: `{"type": "lead", "measure": "17", "value": "Cello"}`

### 3. EN, Point 1. STYLE
- Quote: "Then the first violin probably leads with the main tune [m. 1-3]."
- Problem: The theme starts at m. 0, and the ZH version says [m. 0-3].
- Evidence: `main theme: Violin 1 0-3`. `main theme: Violin 2 0-3`.
- Fix: "The first violin probably leads with the main tune [m. 0-3], starting with all instruments on the same notes in octaves [m. 0]."

### 4. ZH, Point 2. STYLE
- Quote: "第一部分在G大调上结束,并会重复[m. 8]。"
- Problem: The measure reference is attached to "repeat" instead of to the ending bar.
- Fix: "第一部分在G大调上结束 [m. 8],并会重复。"

**Checked and clean:** the EN overview and Points 2–4, 6–11. The ZH overview and Points 1, 3–7, 9–12. Point 9's dim and Point 11's fp are correctly described as gradual and sudden.

---

## k525_4 (IV. Rondo)

### 1. EN, Point 1. MISLEADING
- Quote: "Later in this opening section it grows louder, reaching a strong finish at [m. 10b]."
- Problem: "grows louder" implies a crescendo, but none is marked. The level steps up from p to mf (m. 7) to f (m. 10b). The ZH version says this correctly ("逐级").
- Evidence: `7|…|mf|mf`, `10b|…|f|f`. No <cresc>.
- Fix: "Later in this opening section it steps up to medium loud [m. 7] and then to loud [m. 10b]."

### 2. EN, Point 3. STYLE
- Quote: "Three instruments play more lightly together [m. 18-21]."
- Problem: m. 19 is homophonic, not trio. The ZH version correctly gives [m. 20-21].
- Evidence: `18|…|trio`, `19|…|homophonic`, `20|…|trio`, `21|…|trio`.
- Fix: "At times only three instruments play [m. 18, 20-21]."

### 3. EN, Point 6 headline. STYLE
- Quote: "The loudest moment of this section"
- Problem: The heuristic is stated as fact. The text hedges it ("probably").
- Fix: "The estimated loudest moment"

### 4. ZH, Point 7 headline. STYLE
- Quote: "第二部分的最响处"
- Problem: Same as #3.
- Fix: "第二部分里估计最响的地方"

### 5. EN, Point 7. STYLE
- Quote: "A new part begins loud [m. 59], with the instruments in unison. In unison, they play the same notes."
- Problem: The added definition is clumsy and repeats the glossary.
- Fix: "A new part begins loud [m. 59], with the instruments playing the same notes in unison."

### 6. EN, Point 14. STYLE
- Quote: "The last part starts with the main tune in G major…"
- Problem: Point 13 says the last part begins at m. 132 with the loud unison, and the section list agrees (Part 4: 132–166).
- Fix: "Right after that unison, the main tune returns in G major, played softly by the first violin [m. 133-135]."

### 7. ZH, Point 10. STYLE
- Quote: "程序把 [m. 76-77] 标为G大调,但这里估出的和弦并不清楚,又回到小调 [m. 78]。"
- Problem: The joined clauses read as if the unclear chords went back to minor.
- Fix: "程序把 [m. 76-77] 标为G大调,但这里估出的和弦并不清楚。[m. 78] 起又回到G小调。"

### 8. ZH, Point 5 headline vs EN Point 4. STYLE
- Quote: ZH "进入A大调,气氛更轻盈" vs. EN "Some of the estimated chords here sound tense."
- Problem: The two languages give opposite mood descriptions, and the facts support neither.
- Fix: ZH headline: "进入A大调,领奏变得分散". Optionally soften the EN text to "The estimated chords here move around a lot."

**Checked and clean:** the EN overview and Points 2, 4, 5, 8–13, 15. The ZH overview and Points 1–4, 6, 8, 9, 11–16 are clean apart from #8.

---

## Counts

| Piece | ERROR | MISLEADING | STYLE |
|---|---|---|---|
| op18no5_1 | 0 | 6 | 5 |
| op18no5_2 | 0 | 3 | 6 |
| op18no5_3 | 0 | 1 | 4 |
| op18no5_4 | 1 | 0 | 5 |
| k525_1 | 0 | 2 | 2 |
| k525_2 | 0 | 3 | 3 |
| k525_3 | 1 | 0 | 3 |
| k525_4 | 0 | 1 | 7 |
| **Total** | **2** | **16** | **35** |

## Patterns across guides

1. **Gradual wording with no cresc/dim marking.** Words like "fades", "getting very quiet", "grows louder", "一路渐强" and "减弱" are used where the change is sudden. Found in op18no5_1 (EN P3 and P12, ZH P12), k525_1 EN P11 and k525_4 EN P1.
2. **Loudest-point estimate stated as fact in headlines,** even where the text is hedged. Found in op18no5_1 P8 (both languages), op18no5_2 P8, op18no5_4 (EN P10 and ZH P9), k525_2 (EN P11 and ZH P10) and k525_4 (EN P6 and ZH P7).
3. **Non-standard Chinese dynamic terms.** 轻/很轻/响/极弱/极强 appear instead of 弱/很弱/强/很强. Found in every Beethoven ZH guide and in k525_1 and k525_2. Some guides are not even consistent with their own glossary.
4. **Editing artifacts:**
   - Duplicated text: k525_3 ZH P8 headline, op18no5_3 EN glossary, op18no5_2 EN P3, op18no5_1 ZH P8, k525_2 ZH P8.
   - Misplaced or dangling references: k525_1 EN P4, op18no5_1 EN P11, k525_3 ZH P2.
