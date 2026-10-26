# Review C: Mozart K. 525, movements 1-4 (prose review)

Scope: k525_1, k525_2, k525_3, k525_4, EN and ZH guides, checked against `*_facts.txt` only.
Severity: ERROR = factually wrong or invented; MISLEADING = defensible but a listener would be misled; STYLE = wording or translation.

General checks that pass in all eight guides: every guide says once that keys/chords are estimated and that the score came from optical recognition. No outside knowledge (history, dates, biography, recordings, fame) appears anywhere. The out-of-range measure references flagged in `audit.tsv` for k525_1 ZH P12 ([m. 21-27]) and k525_3 ZH P10 ([m. 19-24]) say so explicitly ("第一部分的", "前面"), so they are fine. The `audit.tsv` "unhedged-lead" flags for k525_3 m. 17 (cello) are an artefact of the duplicated label 17: the Part 3 row reads `17|Part 3|D major|Vc|1.0|solo`, so "the cello plays alone" is supported. The k525_4 m. 58b flags concern the claims list. The prose only says the cello plays the tune, which the theme table supports (`main theme: Cello 58b-61, tonal`).

---

## k525_1 (I. Allegro)

### 1. k525_1 / EN / overview — MISLEADING
- Quote: "Trust the big picture: the sections, the key changes, who leads, and loud versus soft."
- Problem: the guide tells the listener to trust "who leads". The facts call the lead a heuristic and list only sections, keys and overall shape as reliable. Many bars have lead confidence 0.0.
- Evidence: "lead: Lead part is a heuristic ... Treat low-confidence spans as uncertain." / "sections, keys and the overall shape are more reliable."
- Fix: "Trust the big picture: the sections, the key changes, and loud versus soft. Who has the tune is only a rough guess in many bars."

### 2. k525_1 / EN / point 3 — MISLEADING
- Quote: "The first violin keeps the tune over a quiet background."
- Problem: two bars in this range have the lead shared with the viola at confidence 0.0, and three bars are homophonic (no separate background). The text does not hedge.
- Evidence: "11|Part 1|G major|Vn1+Va|0.0|melody + accompaniment" ; "15|Part 1|G major|Vn1+Va|0.0|..." ; "10 ... homophonic", "12 ... homophonic", "14 ... homophonic".
- Fix: "The first violin mostly keeps the tune. In a few bars the viola probably shares it [m. 11, 15]."

### 3. k525_1 / EN / point 4 — STYLE
- Quote: "The estimated loudest point of Part 1 is at [m. 25]. Here the viola and cello probably share the lead for a moment [m. 23-24]."
- Problem: "Here" follows the sentence about m. 25 but points to m. 23-24, so the reader looks at the wrong bar. Also, the facts give m. 25 as the loudest/busiest point of the whole movement, not just of Part 1. The ZH version says 全曲, so the two versions disagree.
- Evidence: "LOUDEST/BUSIEST POINT (heuristic): measure 25 (ff, Part 1)"; "23-24 Va (conf 0.0)".
- Fix: "Just before, the viola and cello probably share the lead for a moment [m. 23-24]. The software estimates [m. 25] as the loudest, busiest point of the movement."

### 4. k525_1 / EN / point 5 — MISLEADING
- Quote: "After two loud bars, the music turns soft at [m. 27]. The lines become more independent."
- Problem: (a) The A major passage has only one loud bar (m. 26). M. 25 belongs to the previous point and to D major. (b) Only m. 29-30 have independent lines; m. 27-28 and m. 31-34 are melody + accompaniment.
- Evidence: "26|Part 1|A major|...|ff" ; "27|...|p|p" ; texture "27-28 melody + accompaniment; 29-30 independent lines; 31-34 melody + accompaniment".
- Fix: "After one loud bar, the music turns soft at [m. 27]. For a moment the lines move more independently [m. 29-30]."

### 5. k525_1 / EN / point 7 — STYLE
- Quote: "Next the players move in unison or in octaves, meaning they play the same notes at different heights [m. 56-57]."
- Problem: the definition only fits octaves. Unison means the same notes at the same height. (The glossary gets this right.)
- Fix: "Next the players play the same notes, either at the same height or in different octaves [m. 56-57]."

### 6. k525_1 / EN / point 8 — MISLEADING
- Quote: "The first violin has the tune."
- Problem: every other bar in 59-68 has the lead shared with violin 2 (or viola) at very low confidence. The guide does not hedge.
- Evidence: "60|...|Vn1+Vn2|0.05|independent lines", "62|...|Vn1+Vn2|0.17", "64|...|Vn1+Vn2|0.17", "68|...|Vn1+Va|0.0".
- Fix: "The first violin probably has the tune, but in every other bar the second violin seems to share it."

### 7. k525_1 / EN / point 9 — MISLEADING
- Quote (headline): "A loud burst, then a pause for breath"
- Problem: "pause" suggests silence or a rest. The facts show m. 71-72 still playing (soft, independent lines/homophonic). No bar is empty.
- Evidence: "71|Part 2|D major|Vn1|0.32|independent lines|p|p" ; "0 measure(s) have no notes".
- Fix: "A loud burst, then a soft moment"

### 8. k525_1 / EN / point 11 — MISLEADING
- Quote: "From [m. 85] the music is soft again, in G major. The first violin leads."
- Problem: (a) The music is already soft from m. 83 (point 10 says so), so "soft again" at 85 is wrong about where the change happens. (b) The lead is unhedged, but m. 86 and m. 90 are shared with the viola at 0.0, and m. 92 is at 0.32.
- Evidence: "83|...|p|p" ; "86|...|Vn1+Va|0.0" ; "90|...|Vn1+Va|0.0" ; "92|...|Vn1|0.32".
- Fix: "The music stays soft in G major. The first violin mostly leads, though the viola probably shares the tune in a few bars [m. 86, 90]."

### 9. k525_1 / EN / point 12 — MISLEADING
- Quote: "It is a sharp contrast after the very soft music before it."
- Problem: the bar just before (m. 95) is soft (p), not very soft. Only m. 94 is pp.
- Evidence: "94|...|pp|p,pp" ; "95|...|p|p".
- Fix: "It is a sharp contrast after the soft music before it."

### 10. k525_1 / EN / point 13 — MISLEADING
- Quote (headline): "Home key, with a loud swell"
- Problem: "swell" means a gradual crescendo. The facts show a sudden f marking at m. 111 and no crescendo.
- Evidence: "110|...|p" ; "111|...|f|f".
- Fix: "Home key, then a sudden loud passage"

### 11. k525_1 / ZH / point 1 — MISLEADING
- Quote (headline): "开场主题:三件乐器同时亮相"
- Problem: the texture is homophonic (everyone plays together), so violin 2 is playing too. The headline suggests only three instruments play. The theme match covers three parts, but the passage is not a three-instrument passage.
- Evidence: "0|Part 1|G major|Vn1|0.48|homophonic|f" ; theme returns list Vn1, Va, Vc at 0-1.
- Fix: "开场主题:四件乐器一起强奏,三个声部奏同一旋律"

### 12. k525_1 / ZH / point 1 — MISLEADING
- Quote: "这是全曲最重要的旋律,请先记住它。"
- Problem: the facts give only one theme and do not rank its importance. Also, "全曲" means the whole work, but this guide covers one movement.
- Evidence: "THEMES - 'main theme': first played by Violin 1 at 0" (only theme listed).
- Fix: "这是本乐章的主要主题,第二部分开头还会再出现,请先记住它。"

### 13. k525_1 / ZH / point 2 — MISLEADING
- Quote: "程序对这一段主奏的判断相当有把握,大多是第一小提琴。"
- Problem: confidence is high only in m. 4-7. M. 2 = 0.29, m. 3 = 0.0 (shared with violin 2), and m. 8 = 0.36. "相当有把握" overstates it for the whole stretch. The texture also alternates with independent lines (m. 3, 6, 8).
- Evidence: "2|...|0.29", "3|...|Vn1+Vn2|0.0|independent lines", "8|...|0.36|independent lines".
- Fix: "中间几小节 [m. 4-7] 主奏很清楚是第一小提琴;两头几小节判断把握不大,可能与第二小提琴分担。"

### 14. k525_1 / ZH / point 3 — MISLEADING
- Quote: "第一小提琴仍然带着旋律,其他三件乐器轻轻伴奏 [m. 9-16]。"
- Problem: same as EN point 3. The viola probably shares the lead in m. 11 and m. 15 (confidence 0.0). M. 10, 12 and 14 are homophonic, not a tune with accompaniment.
- Evidence: "11|...|Vn1+Va|0.0" ; "15|...|Vn1+Va|0.0".
- Fix: "第一小提琴大多带着旋律,其他乐器轻声衬托;[m. 11] 和 [m. 15] 中提琴可能与它分担旋律。"

### 15. k525_1 / ZH / point 4 — MISLEADING
- Quote: "然后音量降到更弱的 pp [m. 19]。" / headline "强弱对比加大,逐渐安静下来"
- Problem: at m. 19 the pp marking is followed at once by p, and the dynamic in force is p. The pp is momentary. "逐渐" (gradual) is not supported because there is no diminuendo marking.
- Evidence: "19|Part 1|G major|Vn1|0.65|melody + accompaniment|p|pp,p".
- Fix: "然后在 [m. 19] 有一瞬间极弱(pp),随即回到弱(p)。" Headline: "重音之后,一瞬间变得极轻"

### 16. k525_1 / ZH / point 5 — MISLEADING
- Quote (headline): "转入D大调,音量达到全曲最高点"
- Problem: the loudest point is a heuristic estimate (the text hedges with 估计, but the headline does not). The same ff level also appears at m. 96-97. "全曲" should be "本乐章".
- Evidence: "LOUDEST/BUSIEST POINT (heuristic): measure 25" ; "96|...|ff|ff,sf".
- Fix: "转入D大调,本乐章估计最响的地方"

### 17. k525_1 / ZH / point 9 — MISLEADING
- Quote: "这一段像是在“探索”不同的调,第一小提琴在高处领唱。"
- Problem: the lead is unhedged even though m. 60, 62 and 64 are shared with violin 2 at confidence ≤ 0.17. "在高处" (register) is not given in the facts.
- Evidence: "60|...|Vn1+Vn2|0.05", "62|...|Vn1+Vn2|0.17", "64|...|Vn1+Vn2|0.17".
- Fix: "这一段像是在“探索”不同的调;旋律大概在第一小提琴,但每隔一小节第二小提琴似乎也在分担。"

### 18. k525_1 / ZH / point 11 — ERROR
- Quote: "到 [m. 85] 起音乐变弱"
- Problem: the music turns soft at m. 83, not m. 85 (m. 83-84 are already p). "到……起" is also ungrammatical.
- Evidence: "82|...|f" ; "83|Part 2|G major|Vn1|0.39|independent lines|p|p".
- Fix: "从 [m. 83] 起音乐变弱。"

### 19. k525_1 / ZH / point 11 — MISLEADING
- Quote: "很像第一部分开头后那段轻柔的旋律。"
- Problem: the facts list no theme return here. The likeness is in the chords and dynamics (m. 85-94 match m. 10-19, including sf at 92-93 vs 17-18 and pp at 94 vs 19), not in a detected melody. Calling it the same 旋律 claims more than the facts show.
- Evidence: theme returns list only 0-1 and 55-56. Chords: "85|...|B minor C major" = "10|...|B minor C major"; "94|...|pp|p,pp||G major C major" vs "19|...|pp,p||G major C major".
- Fix: "这里的和声与强弱走向,和第一部分 [m. 10-19] 那段轻声音乐很相似(和声为程序估计)。"

### 20. k525_1 / ZH / point 11 — MISLEADING
- Quote: "从 [m. 79] 起第一小提琴清楚地领唱。"
- Problem: "从……起" suggests the clear lead continues onward. It is clear only in m. 79-82. Later bars drop (m. 83 = 0.39, m. 86 = 0.0 shared, m. 90 = 0.0 shared).
- Evidence: "79-82 ... 1.0" ; "83|...|0.39" ; "86|...|Vn1+Va|0.0".
- Fix: "[m. 79-82] 第一小提琴清楚地领奏。"

### 21. k525_1 / ZH / point 13 — MISLEADING
- Quote: "音乐一再交替:弱 [m. 104]、强 [m. 111]……"
- Problem: nothing changes at m. 104. The music has been soft since m. 98, and m. 104 has no new marking. Listing it in an alternation suggests a drop there.
- Evidence: "98|...|p|p" ; "104|Part 2|G major|Vn2|0.61|melody + accompaniment|p|||".
- Fix: "音乐一再交替:先是弱 [m. 102],然后强 [m. 111]、弱 [m. 115]、强 [m. 119]。"

### 22. k525_1 / ZH / glossary — ERROR
- Quote: "齐奏(homophonic):几件乐器节奏大致一样,像一起“合唱”。"
- Problem: 齐奏 means unison (everyone plays the same notes). It is not homophonic texture. Point 8 uses 齐奏 correctly for unison/octaves, so the glossary contradicts the text.
- Evidence: "56-57 unison/octaves" (point 8 齐奏) vs "0-1 homophonic".
- Fix: term "主调织体(各声部同节奏,homophonic)", explanation "几件乐器按同样的节奏一起走,像一起唱一首赞美诗,上面的声部最突出。"

### 23. k525_1 / ZH / glossary — STYLE
- Quote: "sf:突然加重的一个音,像一次轻轻的“重击”。"
- Problem: "轻轻的重击" contradicts itself.
- Fix: "sf:突然加重的一个音,像一次短促的重击。"

### 24. k525_1 / ZH / overview, point 5, point 10 — STYLE
- Quote: "全曲分为两大部分" / "全曲的估计高点" / "是全曲较暗、较紧张的地方"
- Problem: 全曲 means the whole work, but the guide covers one movement.
- Fix: replace 全曲 with 本乐章, e.g. "本乐章分为两大部分".

---

## k525_2 (II. Romanze)

### 25. k525_2 / EN / overview — STYLE
- Quote: "the lead is only a rough guess here (confidence under 0.5)"
- Problem: "confidence under 0.5" is jargon for lay readers.
- Fix: "Violin 1 probably carries the main tune, but the software's guess about who leads is rough here."

### 26. k525_2 / EN / point 3 — MISLEADING
- Quote: "The music stays soft, with Violin 1 clearly on top."
- Problem: (a) m. 14 has new f / fp accents, so the music is not plainly soft throughout. (b) The m. 15 lead is 0.38, below 0.4, and is shown as "clearly".
- Evidence: "14|Part 2|G major|Vn1|0.65|melody + accompaniment|p|f,p,fp" ; "15|...|Vn1|0.38|trio".
- Fix: "The music stays mostly soft, with a short accent at [m. 14]. Violin 1 is clearly on top at first [m. 11-13]."

### 27. k525_2 / EN / point 6 — MISLEADING
- Quote: "The music stays soft, and Violin 1 clearly has the tune."
- Problem: this is true only for m. 24-26. M. 23 and m. 27 are shared with violin 2 (0.0 and 0.2).
- Evidence: "23|...|Vn1+Vn2|0.0" ; "27|...|Vn1+Vn2|0.2".
- Fix: "The music stays soft. Violin 1 clearly has the tune in the middle [m. 24-26]."

### 28. k525_2 / EN / point 8 — MISLEADING
- Quote (headline): "Back in C major, building to loud"
- Problem: "building" suggests a gradual crescendo. The facts show a sudden f at m. 37 after p, with no crescendo marking. The text itself says "it becomes f".
- Evidence: "36|...|p|||" ; "37|...|f|f".
- Fix: "Back in C major, then suddenly loud"

### 29. k525_2 / EN / point 10 — MISLEADING
- Quote: "Violin 1 probably carries the tune over a gentle accompaniment."
- Problem: m. 48-50 are independent lines, not a tune with accompaniment.
- Evidence: texture "48-50 independent lines; 51-59 melody + accompaniment".
- Fix: "Violin 1 probably carries the tune. At first the lines move more independently [m. 48-50], then the others accompany [m. 51-56]."

### 30. k525_2 / EN / point 11 — MISLEADING
- Quote: "The loudest and busiest point is around [m. 63]."
- Problem: the facts give this as a heuristic estimate, and m. 60-64 all have the same dynamic (f). The EN states it as fact. ZH point 10 hedges correctly ("被估算为").
- Evidence: "LOUDEST/BUSIEST POINT (heuristic): measure 63 (f, Part 6)" ; "60 ... 64 |f".
- Fix: "The software estimates the loudest, busiest point around [m. 63]."

### 31. k525_2 / EN / point 12 — MISLEADING
- Quote: "Then Violin 1 plays the main theme again, now in G major [m. 69-71]." (headline: "The main tune returns in G major")
- Problem: the theme comes back at exactly the same pitch as the opening (transposed 0 semitones). "Now in G major" makes the listener expect a transposed tune. The G major label is only the key estimate.
- Evidence: "main theme: Violin 1 69-71, exact, transposed 0 semitones, key G major" ; "main theme: Violin 1 1-3, original, transposed 0 semitones, key C major".
- Fix: "Then Violin 1 plays the main theme again, at the same pitch as the opening [m. 69-71]. The software labels the key here as G major, but that is only an estimate." Headline: "The main tune returns"

### 32. k525_2 / EN / point 13 — MISLEADING
- Quote: "The last bars sit in G major [m. 77-80]."
- Problem: the home key is C major, and the overview says the music "keeps coming back to it". Ending "in G major" leaves the listener confused. The facts also show the very last chord estimated as C major, which the guide omits.
- Evidence: '"home_key": "C major"' ; "80|Part 6|G major|...|G dominant seventh C major".
- Fix: "The software estimates the last bars as G major [m. 77-80], but the very last chord is estimated as C major, so the movement probably ends at home. Treat these keys as a guide."

### 33. k525_2 / EN / point 13 — STYLE
- Quote: "Then the music grows soft again [m. 75]."
- Problem: "grows" suggests a gradual change, but m. 75 has a sudden p. ZH says "突然变轻", so the two versions differ.
- Evidence: "74|...|f" ; "75|...|p|p".
- Fix: "Then the music turns suddenly soft again [m. 75]."

### 34. k525_2 / ZH / overview — STYLE
- Quote: "第一小提琴大多数时候(大概)带着歌唱性的旋律,其余三件乐器伴奏。"
- Problem: the bracketed "(大概)" reads awkwardly.
- Fix: "第一小提琴大概在大多数时候唱着旋律,其余三件乐器伴奏,不过程序对主奏的判断把握不大。"

### 35. k525_2 / ZH / point 5 — STYLE
- Quote: "听起来像是在为后面的发展做准备。"
- Problem: 发展 can be read as 发展部 (development section), a form label the facts do not give.
- Fix: "听起来像是在为后面的变化做准备。"

### 36. k525_2 / ZH / point 8 — MISLEADING
- Quote: "这段小调持续到 [m. 56],是全乐章最阴沉的一段。"
- Problem: "最阴沉" is a superlative judgement not in the facts. What the facts do support is that this is the longest minor-key stretch (43-56, versus 24-27 and 31-32).
- Evidence: KEY PLAN "A minor: 24-27", "E minor: 31-32", "C minor: 43-56".
- Fix: "这段小调持续到 [m. 56],是全乐章最长的一段小调。"

### 37. k525_2 / ZH / point 8 — STYLE
- Quote: "[m. 45] 有一个重音标记(fp,先响后立刻轻)。"
- Problem: fp is a dynamic marking (loud then at once soft), not exactly an accent mark.
- Fix: "[m. 45] 有一个 fp 记号(先强,随即变弱)。"

### 38. k525_2 / ZH / points 8-9 — MISLEADING
- Quote: point 8 text "从 [m. 43] 起进入C小调……" (no mention of Part 5 or Part 6). Point 9 claims "Part 6" at m. 47, outside its range [57-62].
- Problem: the ZH text never tells the listener that Part 5 starts at m. 42 (with a sudden drop to p) or that Part 6 starts at m. 47. EN points 9 and 10 do. The section claim in point 9 also points outside its range (also in audit.tsv).
- Evidence: "Part 5: 42-46 (5 measures, repeated)" ; "Part 6: 47-80" ; "41|...|f" / "42|...|p|p".
- Fix (point 8): "[m. 42] 第五部分开始,音量突然变弱;从 [m. 43] 起进入C小调。[m. 47] 第六部分开始,仍是C小调和轻声。"

### 39. k525_2 / ZH / point 11 — MISLEADING
- Quote: "主旋律在 [m. 69-71] 以相同音型再次出现,由第一小提琴演奏,这次是G大调。"
- Problem: same as EN point 12. The pitch is identical to the opening (0 semitones), so "这次是G大调" makes the listener expect a transposed tune.
- Evidence: "main theme: Violin 1 69-71, exact, transposed 0 semitones".
- Fix: "主旋律在 [m. 69-71] 由第一小提琴以和开头完全相同的音高再次出现;程序把这里的调估计为G大调,仅供参考。"

### 40. k525_2 / ZH / point 12 — MISLEADING
- Quote (headline): "回到C大调,响亮的收尾"
- Problem: this is not the ending. The music turns soft at m. 75 and goes on to m. 80 (point 13 is "轻轻地结束"). The two headlines contradict each other.
- Evidence: "75|...|p|p" ; last label 80.
- Fix: "回到C大调,一段响亮的乐句"

### 41. k525_2 / ZH / point 13 — MISLEADING
- Quote: "最后四小节在轻声中进行,和声估算为G大调 [m. 77-80]。"
- Problem: same as EN point 13. The glossary says the home is C major ("听到它会有安定、回家的感觉"), and the last chord is estimated as C major.
- Evidence: "80|...|G dominant seventh C major".
- Fix: "最后四小节在轻声中进行,程序估计为G大调 [m. 77-80],但最后一个和弦估计是C大调,乐章大概还是回到了主调。"

---

## k525_3 (III. Menuetto)

### 42. k525_3 / EN / overview — MISLEADING
- Quote: "The big picture is more reliable: loud and soft, who leads, and the key changes."
- Problem: the lead is a heuristic, and its mean confidence for m. 0-17 is only 0.36.
- Evidence: "0-17 Vn1 (conf 0.36)" ; "lead: ... heuristic".
- Fix: "The big picture is more reliable: the sections, loud and soft, and the key changes. Who has the tune is only a guess in many bars."

### 43. k525_3 / EN / point 1 — MISLEADING
- Quote: "Then the first violin probably leads with the tune over the others [m. 1-3]. The others move with it in block chords."
- Problem: the facts show violin 2 playing the same main theme an octave lower in m. 0-3. Saying "the others" play block chords hides this. The EN never mentions the main theme at all. ZH point 1 does.
- Evidence: "main theme: Violin 2 0-3, exact, transposed -12 semitones".
- Fix: "Then the first violin probably leads with the main tune [m. 1-3]. The second violin plays the same tune an octave lower, and all move together in block chords."

### 44. k525_3 / EN / point 6 — MISLEADING
- Quote: "The key changes to D major, a move to a new home."
- Problem: the home key stays G major. Calling D major "a new home" misuses the glossary idea of the home key.
- Evidence: '"home_key": "G major"'.
- Fix: "The key changes to D major, a new key for this part."

### 45. k525_3 / EN / point 8 — MISLEADING
- Quote (headline): "The loudest stretch"
- Problem: m. 27-31 are marked f, the same level as the opening (m. 0-8) and m. 14-16. Only the heuristic "loudest/busiest" point picks m. 28. The headline suggests this passage is louder than anything before it.
- Evidence: "LOUDEST/BUSIEST POINT (heuristic): measure 28" ; "0|...|f|f" ; "27|...|f|f".
- Fix: "Loud again: the estimated peak"

### 46. k525_3 / EN / point 9 — MISLEADING
- Quote: "It reaches very soft at [m. 32]."
- Problem: the pp at m. 32 is followed at once by p, and the dynamic in force is p. ZH says "回到小声", so the versions differ.
- Evidence: "32|Part 4|D major|Vn1|0.8|independent lines|p|pp,p".
- Fix: "It touches very soft for a moment at [m. 32], then stays soft."

### 47. k525_3 / EN / point 11 — STYLE
- Quote (headline): "A final cadence and a last single line"
- Problem: "cadence" is jargon. It is not in the glossary, and the facts' cadence column is empty.
- Fix: "A closing phrase and a last single line"

### 48. k525_3 / ZH / overview — MISLEADING
- Quote: "所以请多关注大的轮廓(段落、调性、谁在领奏、强弱)"
- Problem: same as EN overview. 谁在领奏 is the least reliable item (mean confidence 0.36 for m. 0-17).
- Evidence: "0-17 Vn1 (conf 0.36)".
- Fix: "所以请多关注大的轮廓(段落、调性、强弱);谁在领奏只是程序的粗略判断。"

### 49. k525_3 / ZH / point 2 — MISLEADING
- Quote: "接下来仍是强奏,旋律在上,其他声部伴奏[m. 4]。"
- Problem: at m. 4 the lead is shared by violin 1 and viola at confidence 0.0, so "旋律在上" is unhedged.
- Evidence: "4|Part 1|G major|Vn1+Va|0.0|melody + accompaniment|f".
- Fix: "接下来仍是强奏,[m. 4] 旋律可能由第一小提琴和中提琴分担。"

### 50. k525_3 / ZH / point 4 — MISLEADING
- Quote (headline): "强奏回归,回到G大调"
- Problem: the music never left G major, so "回到G大调" is wrong. The key plan stays in G major for m. 0-17.
- Evidence: "G major: 0-17".
- Fix: "强奏回归,第二部分在G大调上结束"

### 51. k525_3 / ZH / point 8 — MISLEADING
- Quote: "在[m. 28]达到全曲最响、最忙的地方。" (headline "力度最高点")
- Problem: this is a heuristic estimate but is stated as fact. The dynamic level (f) is the same as at the opening, so "力度最高点" is wrong as a dynamic claim. 全曲 should be 本乐章.
- Evidence: "LOUDEST/BUSIEST POINT (heuristic): measure 28 (f, Part 4)" ; "0|...|f|f".
- Fix: "程序估计 [m. 28] 是本乐章最响、最忙的地方(力度记号与开头一样是 f)。" Headline: "第四部分:强奏重现"

### 52. k525_3 / ZH / title (also k525_2 title, k525_4 title) — STYLE
- Quote: "莫扎特《小夜曲》K. 525 第三乐章:小步舞曲(Allegretto)" ; k525_4 "回旋曲(Allegro)"
- Problem: the work is named 《弦乐小夜曲》 in k525_1 and k525_4 but 《小夜曲》 in k525_2 and k525_3. The tempo words are left in Italian, while k525_2 translates its tempo (行板).
- Fix: "莫扎特《弦乐小夜曲》K. 525 第三乐章:小步舞曲(小快板)" and "第四乐章:回旋曲(快板)".

---

## k525_4 (IV. Rondo)

### 53. k525_4 / EN / point 2 — MISLEADING
- Quote (headline): "Louder, with the lower strings joining in"
- Problem: m. 11 is no louder than m. 10b (both f). "Joining in" suggests the lower strings were silent before, but the earlier texture is melody + accompaniment with all parts playing.
- Evidence: "10b|...|f|f" ; "11|...|f|f" ; "7-13 melody + accompaniment".
- Fix: "Still loud, with the lower strings stepping forward"

### 54. k525_4 / EN / point 3 — STYLE
- Quote: "Another sharp accent appears at [m. 22]."
- Problem: no earlier accent has been mentioned, so "Another" has nothing to refer to.
- Fix: "A sharp accent appears at [m. 22]."

### 55. k525_4 / EN / point 4 — MISLEADING
- Quote: "The first violin probably leads over a soft accompaniment."
- Problem: in five of the eight bars the lead is shared (confidence 0.0-0.03) or very low (0.19). "Probably the first violin" does not describe this.
- Evidence: "28|...|Vn1+Vn2|0.0", "29|...|0.19", "30|...|Vn1+Vn2|0.03", "31|...|Vn1+Vn2|0.0", "32|...|Vn1+Va|0.0".
- Fix: "The first violin leads at first [m. 26]. After that the tune seems shared with the other instruments."

### 56. k525_4 / EN / point 6 — MISLEADING
- Quote: "The music swells to loud at [m. 48]."
- Problem: "swells" suggests a gradual crescendo. The facts show a sudden f at m. 48 after p, with no crescendo marking.
- Evidence: "47|...|p" ; "48|...|f|f".
- Fix: "The music turns suddenly loud at [m. 48]."

### 57. k525_4 / EN / point 9 — MISLEADING
- Quote: "There is a brief flash of G major at [m. 76-77]."
- Problem: the local key label is G major, but both estimated chords in these bars are C minor. The claim is shaky and unhedged, and a listener will not hear a bright major flash.
- Evidence: "76|Part 3|G major|...|C minor C minor" ; "77|Part 3|G major|...|C minor C minor".
- Fix: "The software marks a brief turn away from G minor at [m. 76-77], but its chord estimates there are unclear."

### 58. k525_4 / EN / point 10 — MISLEADING
- Quote (headline): "Hushed passage, building toward home"
- Problem: "building" suggests rising volume, but m. 86-100 are all p.
- Evidence: "86|...|p|f,p" through "100|...|p".
- Fix: "Hushed passage, leading toward home"

### 59. k525_4 / EN / glossary — MISLEADING
- Quote: "Trio texture: Only three of the four instruments are playing the main material."
- Problem: the texture label, used next to "solo", means three parts are sounding and one is resting. "Playing the main material" suggests the fourth plays something else.
- Evidence: texture categories "solo", "trio" ; "18-18 trio; 20-21 trio".
- Fix: "Trio texture: Only three of the four instruments are playing; one is resting."

### 60. k525_4 / ZH / overview — MISLEADING
- Quote: "所以本指南着重大轮廓:段落、调性、谁领奏、强弱。"
- Problem: 谁领奏 is presented as reliable, but m. 14-57a has a mean lead confidence of 0.33.
- Evidence: "14-57a Vn1 (conf 0.33)" ; "lead: ... heuristic".
- Fix: "所以本指南着重大轮廓:段落、调性和强弱;谁在领奏只是程序的粗略判断。"

### 61. k525_4 / ZH / point 1 — MISLEADING
- Quote: "其他乐器在下方伴奏。"
- Problem: m. 2-3 and m. 6 are independent lines, and m. 4 is shared with the cello (0.0). It is not plain accompaniment throughout.
- Evidence: "2-3 independent lines" ; "4|...|Vn1+Vc|0.0" ; "6-6 independent lines".
- Fix: "其他乐器大多在下方伴奏,有几小节各声部也各有自己的线条 [m. 2-3, 6]。"

### 62. k525_4 / ZH / point 2 — STYLE
- Quote (headline): "音量渐强,第一部分收束"
- Problem: 渐强 is the term for a crescendo marking, which the facts do not show. The change is in steps (p → mf → f). The text's "一步步变大" is right.
- Evidence: "7|...|mf|mf" ; "10b|...|f|f".
- Fix: "音量逐级加大,第一部分收束"

### 63. k525_4 / ZH / point 3 — STYLE
- Quote: "到 [m. 17] 转入D大调,音色更明亮"
- Problem: 音色 means timbre. A key change alters harmonic colour, not timbre.
- Fix: "到 [m. 17] 转入D大调,色彩更明亮"

### 64. k525_4 / ZH / point 4, point 11, glossary — MISLEADING
- Quote: "几个声部轻声交谈的“三重奏”式写法 [m. 20-21]" ; "声部像三重奏一样轻声交谈 [m. 86-89]" ; glossary "三重奏式写法(trio):大约三个声部在轻声交谈,织体比较通透。"
- Problem: the facts say only that three parts are sounding. "交谈" (dialogue or imitation) is invented. 三重奏 normally names an ensemble or genre, and "大约三个声部" is vague. The label means exactly three.
- Evidence: "20-21 trio" ; "86-89 trio".
- Fix (point 4): "随后只有三个声部在轻声演奏 [m. 20-21]。" Glossary: "三声部织体(trio):四件乐器中只有三件在演奏,一件休止,声音比较通透。"

### 65. k525_4 / ZH / point 5 — MISLEADING
- Quote: "第一小提琴大多带着旋律。"
- Problem: same as EN point 4. In m. 28-32 the lead is shared or near zero. "大多" is not supported.
- Evidence: "28|...|Vn1+Vn2|0.0" … "32|...|Vn1+Va|0.0".
- Fix: "开头 [m. 26] 第一小提琴带着旋律,之后旋律似乎由几件乐器分担。"

### 66. k525_4 / ZH / point 8 — STYLE
- Quote: "[m. 60] 起第一小提琴接着奏主旋律,调性变为C小调"
- Problem: according to the key plan, C minor starts at m. 59, not m. 60.
- Evidence: "C minor: 59-61".
- Fix: "[m. 59] 调性已转为C小调;[m. 60] 起第一小提琴接着奏主旋律,色彩变暗。"

### 67. k525_4 / ZH / point 9 — MISLEADING
- Quote: "音乐由弱渐强,[m. 68] 起变强(f)。"
- Problem: there is no crescendo marking. The change from p (m. 67) to f (m. 68) is sudden.
- Evidence: "67|...|p|||" ; "68|...|f|f".
- Fix: "音乐先是轻声,[m. 68] 起突然变强(f)。"

### 68. k525_4 / ZH / point 10 — MISLEADING
- Quote: "第一小提琴整段强奏领唱 [m. 72-85]。中间 [m. 76-77] 短暂闪过G大调"
- Problem: (a) "整段" overstates the lead: m. 82 is shared at 0.0 and m. 84 is 0.32. (b) The "G大调" flash has C minor chords in the estimate (same as EN point 9). 领唱 also fits a singer better than a violin; 领奏 is the usual word.
- Evidence: "82|...|Vn1+Vn2|0.0|homophonic" ; "84|...|0.32" ; "76|...|C minor C minor".
- Fix: "第一小提琴在这段大部分时间强奏领奏 [m. 72-81]。程序把 [m. 76-77] 标为G大调,但这里估出的和弦并不清楚。"

### 69. k525_4 / ZH / glossary — STYLE
- Quote: "齐步和声(homophonic)"
- Problem: this is not a standard term.
- Fix: "主调织体(各声部同节奏,homophonic)"

---

## Summary per piece

**k525_1 (I. Allegro).** Both guides get the main facts right: two repeated parts, the key plan, the theme return at m. 55 in D major, and the dynamic changes. The main weakness is lead hedging. EN points 3, 8 and 11 and ZH points 2, 3, 9 and 11 state that the first violin leads in stretches where every other bar is shared at confidence 0.0-0.17. EN also tells the reader to "trust who leads". The ZH has one real error: the drop to soft is put at m. 85 instead of m. 83. It also has a glossary mistranslation (齐奏 for homophonic) that contradicts the ZH text, and an inferred "same melody" return at m. 85 that the facts only support as a chord and dynamic parallel. The remaining issues are small exaggerations ("two loud bars", "swell", "pause", "very soft before it", the 全曲 superlatives).

**k525_2 (II. Romanze).** The section, key and dynamic statements are accurate, and hedging is mostly good (the ZH is better here). The most important problem is in both languages: the main theme at m. 69-71 is called "now in G major" although it is at exactly the same pitch as the opening. A related problem is the "ends in G major" statement, which clashes with home key C and with the final chord, estimated as C major. Smaller issues: unhedged "clearly" leads (EN points 3 and 6), "building"/"grows" wording for sudden dynamic changes, an unhedged climax in EN point 11, a ZH "收尾" headline that is not the ending, and ZH never telling the listener where Parts 5 and 6 begin.

**k525_3 (III. Menuetto).** The guides are short and mostly accurate on sections, repeats, the D major move and the solo bars at m. 17-18 (the audit's cello flag there is a duplicate-label artefact). Problems: both overviews present "who leads" as reliable, although the whole first half has a mean confidence of 0.36. EN ignores the second violin doubling the theme. "Loudest stretch"/"力度最高点" is stated for a passage at the same f level as the opening, unhedged in ZH. The ZH headline says the music "returns" to G major when it never left. EN calls D major "a new home".

**k525_4 (IV. Rondo).** The guides follow the theme returns well (m. 5, 37, 58b/60, 64, 101, 105, 133, 137), and the keys and dynamics match the facts. The main problems: the lead is overstated in m. 25-32 (EN "probably", ZH "大多", while most bars are shared at 0.0). The "flash of G major" at m. 76-77 is unhedged in both languages although the estimated chords there are C minor. The crescendo vocabulary ("swells", "building", 渐强, 由弱渐强) describes sudden f markings. The ZH invents a "交谈" (dialogue) meaning for the three-part texture, and the EN glossary describes it ambiguously. The ZH overview again lists 谁领奏 as reliable.
