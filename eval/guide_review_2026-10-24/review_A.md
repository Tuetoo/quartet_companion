# Review A: prose audit of listening guides

Pieces: `d929_1` (Schubert, Piano Trio D. 929, mvt 1) and `passacaglia` (Handel–Halvorsen duo).
Sources checked: `*_facts.txt`, `*_guide_en.txt`, `*_guide_zh.txt` in `/tmp/claude-0/review/digest/`.
Severity: ERROR = factually wrong or invented; MISLEADING = defensible but a listener would be misled; STYLE = wording/translation.

---

## d929_1 (Schubert D. 929, I)

### D1. d929_1 · EN + ZH · Overview · MISLEADING
- EN: "Trust the big picture: sections, keys, who leads, and loud versus soft."
- ZH: "所以本指南只讲大框架:段落、调性、谁在带领、声音大小。"
- Problem: the guide tells readers to trust "who leads". The method notes call lead a heuristic and list only sections, keys and overall shape as more reliable. Many lead spans in this piece have confidence below 0.4.
- Evidence: `- lead: Lead part is a heuristic ... Treat low-confidence spans as uncertain.` / `- score: ... Rhythm and texture details may be wrong; sections, keys and the overall shape are more reliable.` / e.g. `83-98 Piano (conf 0.39)`, `115-133 Piano (conf 0.3)`.
- Fix EN: "Trust the big picture: sections, keys, and loud versus soft. Who leads is a computer guess, so treat it as a hint."
- Fix ZH: "所以本指南只讲大框架:段落、调性和声音大小。“谁在带领”是电脑推测的,只能作为参考。"

### D2. d929_1 · EN · Point 2 [m. 5-8] · MISLEADING
- Quote: "The violin still leads, but the mood is gentler. The three instruments now sound like a team of equals."
- Problem: The violin leads clearly only at m. 5. In m. 6-8 the lead is shared (Vn+Piano, Vn+Vc) and the confidence is low. Saying "the violin still leads" and then "a team of equals" contradicts itself.
- Evidence: `5|...|Vn|1.0|trio|p`, `6|...|Vn+Piano|0.43|homophonic`, `7|...|Vn+Piano|0.0|trio`, `8|...|Vn+Vc|0.0|melody + accompaniment`.
- Fix: "The music drops to soft at [m. 5]. The violin leads at first. Then the lead is shared, and the three instruments sound more like equal partners."

### D3. d929_1 · EN · Point 4 [m. 16b-21] · ERROR
- Quotes: HEADLINE "The cello sings alone"; TEXT "The cello steps out with a solo line in [m. 16b-21]. It is clearly in the lead."
- Problem: The cello is solo only in m. 16b-17b and 20b-21. At m. 18b the violin leads, all three play (trio), and it is loud. At m. 19b the texture is homophonic. "Alone" and "clearly in the lead" for the whole range are wrong. The ZH guide (point 4, "大提琴在 [m. 16b-17b] 独自演奏") gets it right, so the two languages contradict each other.
- Evidence: `16b-17b solo; 18b-18b trio; 19b-19b homophonic; 20b-21 solo`; `18b|Part 1|F major|Vn|0.99|trio|f|f,<cresc>`.
- Fix: "The cello plays alone at [m. 16b-17b], and the key moves to F major. At [m. 18b] the violin briefly takes over and the music gets loud. Then the cello plays alone again and settles into B-flat major at [m. 21]." Headline: "The cello steps forward".

### D4. d929_1 · EN · Point 10 [m. 175-181] · MISLEADING
- Quote: "It centres on A major from [m. 176], with the piano leading."
- Problem: The piano leads clearly only at m. 176. From m. 177 the confidence is low, and m. 178-180 are shared Piano+Violin. The text needs a hedge.
- Evidence: `176|...|Piano|1.0`, `177|...|Piano|0.32`, `178|...|Piano+Vn|0.13`, `179|...|Piano+Vn|0.13`, `180|...|Piano+Vn|0.18`.
- Fix: "It centres on A major from [m. 176]. The piano leads at first, then probably shares the lead with the violin."

### D5. d929_1 · EN · Point 12 [m. 249-255] · MISLEADING
- Quote: "It reaches the loudest and busiest point of the movement at [m. 254]."
- Problem: m. 254 is only the computer's best guess. The facts show a louder marking (fff) at m. 305. Stated as plain fact, this is too strong.
- Evidence: `## LOUDEST/BUSIEST POINT (heuristic): measure 254 (ff, ...)`; `305|Section 7 ...|F# minor|Piano|1.0|...|ff|fff,ff,sf,<dim>`.
- Fix: "It reaches one of the loudest and busiest moments of the movement at [m. 254]."

### D6. d929_1 · EN · Point 15 [m. 616-644] · ERROR
- Quote: HEADLINE "Final return to E-flat and a loud ending"
- Problem: The movement does not end loud. The last bars are soft (p from m. 642), and the point's own text says so. The ZH headline ("降E大调中安静收束") says the opposite, so the two languages contradict each other.
- Evidence: `642|...|Eb major|Piano|1.0|...|p|p`, `643|...|p`, `644|...|tacet|p`.
- Fix: "Final return to E-flat: a loud build-up, then a soft close"

### D7. d929_1 · EN · Point 9 [m. 152-161] · STYLE
- Quote: HEADLINE "Cello and piano share a gentle tune"
- Problem: The facts show the lead passing between cello and piano. Nothing shows that they play the same tune.
- Evidence: `152-153 Vc (conf 0.73); 154-155 Piano (conf 1.0); 156-156 Vc ...; 157-158 Piano ...; 159-161 Vc`; THEMES lists no return in this range.
- Fix: "Cello and piano take turns, very softly"

### D8. d929_1 · EN · Glossary · STYLE
- Quote: glossary entries "Tacet" and "Crescendo (cresc)".
- Problem: Neither word appears in the EN prose. The text says "a short silence" (P8) and "swells" (P9), so readers cannot link the glossary to the text.
- Evidence: EN P8 TEXT "After a short silence, ..."; EN P9 TEXT "The music swells and fades in small waves."
- Fix (P9): "The music swells and fades in small waves (crescendo and diminuendo)." Fix (P8): "After a short silence (all parts are tacet), the violin plays alone ..."

### D9. d929_1 · ZH · Overview · STYLE
- Quote: "文中的调和和弦都是自动估计的。"
- Problem: "调和和弦" reads as "调和 + 和弦" (the word "调和" means "harmonise"). The meaning is unclear.
- Fix: "文中的调性与和弦都是电脑自动估计的。"

### D10. d929_1 · ZH · Points 1 and 15 · STYLE
- Quotes: P1 "三件乐器的织体像一起和声,比较整齐。请记住这个开头,它是全曲的起点。"; P15 "这里织体比较整齐,像一起和声。"
- Problem: "织体像一起和声" is not natural Chinese and does not explain homophonic texture. "全曲" should be "本乐章", because this is one movement.
- Evidence: `1-4 homophonic`; `395-398 homophonic`.
- Fix P1: "三件乐器节奏一致,一起奏出和弦,托着小提琴的旋律(主调织体)。请记住这个开头,它是本乐章的起点。"
- Fix P15: "这里三件乐器又一起奏和弦,节奏整齐,和开头很像。"

### D11. d929_1 · ZH · Point 4 [m. 16b-21] · MISLEADING
- Quote: HEADLINE "大提琴独唱,转向明亮的调"
- Problem: The music goes from E-flat major to F major and B-flat major. All three are major keys, so it does not "turn bright" from something dark. The glossary says major keys sound bright, so a reader would wrongly assume the earlier music was minor or dark.
- Evidence: `- Eb major: 1-16b`, `- F major: 17b-20b`, `- Bb major: 21-25`.
- Fix: "大提琴独奏,调性转到F大调和降B大调"

### D12. d929_1 · ZH · Point 8 [m. 152-174] · STYLE
- Quote: "大约在 [m. 160] 起音乐稳定在降B大调。"
- Problem: The point covers up to m. 174, but the text describes only up to m. 161. The key changes to D minor at m. 173, so "稳定在降B大调" is not true for the whole range. It also leaves out that the piano leads from m. 162.
- Evidence: `- Bb major: 160-172`, `- D minor: 173-175`; `162-190 Piano (conf 0.46)`.
- Fix: "大约从 [m. 160] 起转到降B大调,之后主要由钢琴带领;到 [m. 173] 转入D小调。" (or shorten the range to 152-161)

### D13. d929_1 · ZH · Point 9 [m. 175-195] · STYLE
- Quote: "[m. 175] 起声音突然变得很响(ff),调性为A大调。"
- Problem: The key at m. 175 is D minor. A major starts at m. 176.
- Evidence: `175|...|D minor|...|ff|ff`, `176|...|A major`.
- Fix: "[m. 175] 起声音突然变得很响(ff),随后在 [m. 176] 转到A大调。"

### D14. d929_1 · ZH · Point 10 [m. 209-232] · STYLE
- Quote: "调性在升F大调、B小调、D大调、C大调之间变换,色彩不断改变。这些快速的转换,像在远方漫步。"
- Problem: "之间变换" suggests the music goes back and forth, but the keys come one after another. Each key lasts 4-11 bars, so "快速" overstates it. D minor (m. 226) is missing, unlike in the EN version. "遥远的" in the headline is a theory judgement that is not in the facts.
- Evidence: `- F# major: 206-216`, `- B minor: 217-220`, `- D major: 221-225`, `- D minor: 226-229`, `- C major: 230-232`.
- Fix: "调性依次经过升F大调、B小调、D大调、D小调和C大调,色彩不断变化,听起来飘忽不定。" Headline: "极轻的声音中不断转调"

### D15. d929_1 · ZH · Point 11 [m. 249-254] · MISLEADING
- Quote: "钢琴在这里主导。"
- Problem: There is no hedge, but the lead confidence is low in most of these bars, including m. 254, the bar the claim is about.
- Evidence: `249|...|Piano|0.28`, `251|...|Piano|0.22`, `253|...|Piano|0.38`, `254|...|Piano|0.29`.
- Fix: "这里可能主要是钢琴在带领,但判断不太确定。"

### D16. d929_1 · ZH · Points 11 and 12 · MISLEADING (internal contradiction)
- Quotes: P11 "到 [m. 254] 达到全乐章最响、最忙的地方(ff)"; P12 headline "从降B小调慢慢走远,再来一次高潮", text "到 [m. 305] 又变得很响".
- Problem: P11 says m. 254 is the loudest point of the whole movement. P12 then calls m. 305 another climax ("高潮"), and m. 305 has a louder marking (fff). The facts only name a heuristic loudest point. They do not label m. 305 a climax.
- Evidence: `## LOUDEST/BUSIEST POINT (heuristic): measure 254 (ff, ...)`; `305|...|ff|fff,ff,sf,<dim>`.
- Fix P11: "到 [m. 254] 达到本乐章最响、最忙的时刻之一(ff),调性为B小调。" Fix P12 headline: "从降B小调慢慢走远,再次变得很响"

### D17. d929_1 · ZH · Point 12 [m. 257-308] · MISLEADING
- Quote: "到 [m. 305] 又变得很响,然后在 [m. 308] 戛然而止。"
- Problem: "戛然而止" means a sudden stop. The facts show a diminuendo at m. 307 before the silent bar at m. 308.
- Evidence: `307|...|Ab major|Vn|0.69|homophonic|ff|sf,<dim>`, `308|...|none|0.0|tacet`.
- Fix: "到 [m. 305] 又变得很响,随后渐弱,在 [m. 308] 停下来。"

### D18. d929_1 · ZH · Point 16 [m. 612-644] · MISLEADING
- Quotes: HEADLINE "尾声:降E大调中安静收束"; TEXT "尾声从 [m. 612] 开始。先在G小调中轻声进行"
- Problem: "尾声" (coda) is a formal label that is not in the facts. The facts only name "Section 12 (new key signature)" and "Section 13". Also, m. 612-613 are in B minor, and G minor starts at m. 614. The EN version starts the last section at m. 616.
- Evidence: `- Section 12 (new key signature): 612-615`, `- Section 13 (new key signature): 616-644`; `- B minor: 606-613`, `- G minor: 614-622`.
- Fix: "最后一段从 [m. 616] 开始,在G小调中轻声进行(前面 [m. 612-615] 是一小段过渡)。" Headline: "最后一段:回到降E大调,轻声结束"

### D19. d929_1 · ZH · Points 6, 10, 13 and glossary · STYLE
- Quotes: P6 "声音降到极轻(pp)"; P10 "声音极轻(pp)"; P13 "声音又变得很轻(pp)"; glossary "pp 是很弱".
- Problem: The same marking (pp) has three different names, so readers may think these are three different levels.
- Fix: use one term everywhere, e.g. "很弱(pp)", and match the glossary: "f 是强,p 是弱,pp 是很弱,ff 是很强".

### Summary: d929_1
The ZH guide is generally more careful with ranges (P4 correctly limits the cello solo to m. 16b-17b; P16 correctly calls the ending quiet). The EN guide has two factual errors: it calls m. 16b-21 a continuous cello solo when the violin leads at m. 18b, and its last headline promises "a loud ending" when the final bars are p. These errors also make the two languages contradict each other. Hedging is handled well in the overview, which states both the optical-recognition and the estimated-keys caveats, and in P3 and P14 (EN) / P3 and P15 (ZH). However, several unhedged lead claims rest on low-confidence bars (EN P2, P10; ZH P11), and both overviews wrongly tell readers to "trust" who leads. The "loudest point" at m. 254 is a heuristic, and the fff marking at m. 305 contradicts it. This creates an internal contradiction in ZH (P11 vs P12). The ZH prose needs some idiom fixes: "调和和弦", "织体像一起和声", inconsistent names for pp, and the invented "尾声" label.

---

## passacaglia (Handel–Halvorsen)

### P1. passacaglia · EN · Overview · MISLEADING
- Quote: "A short four-measure pattern is played again and again, and the music above it keeps changing."
- Problem: This is a textbook definition, not what the facts show. The facts measure how much of the theme's harmony each variation keeps, and from Variation 9 on it is usually close to 0. The theme is detected again only at m. 1-2. There are only two instruments, so there is no separate bass "below" for music to sit "above". The ZH overview ("被不断改写") is closer to the facts.
- Evidence: `Theme returns ...: main theme: Violin 1-2, original`; `Variation 9 (37-40): ... same harmony as theme: 0.0`; `Variation 11 ...: 0.0`; `Variation 18-22 ... same harmony as theme: 0.0 / 0.0 / 0.08 / 0.0 / 0.0`.
- Fix: "This is a passacaglia: a short four-measure theme followed by 22 variations, each also four measures long. Early variations stay close to the theme; later ones move far from it."

### P2. passacaglia · EN + ZH · Glossary "Passacaglia" / "帕萨卡利亚" · MISLEADING
- Quotes: EN "A piece built on a short pattern that repeats many times while the music above it changes."; ZH "一小段音乐不断重复,上方的音乐每次都改写。"
- Problem: Same issue as P1. The facts do not show a repeating pattern underneath. The ZH glossary also contradicts the ZH overview and ZH P1 ("有时离它很远").
- Evidence: as in P1.
- Fix EN: "A set of variations on a short theme; each variation keeps the theme's length but changes the music."
- Fix ZH: "一种变奏曲:一段短主题之后跟着许多变奏,每段长度相同,但内容不断改写。"

### P3. passacaglia · EN · Point 1 [m. 1-4] · STYLE
- Quote: "The violin plays the theme alone on top, loud, with the viola accompanying [m. 1-4]."
- Problem: "alone" and "with the viola accompanying" contradict each other. In m. 4 the texture is a duet.
- Evidence: `1-3 melody + accompaniment; 4-36 duet`.
- Fix: "The violin plays the theme loudly on top, and the viola accompanies below [m. 1-4]."

### P4. passacaglia · EN · Point 1 [m. 1-4] · MISLEADING
- Quote: "Learn it, because everything that follows is built on its four-measure shape."
- Problem: Only the length (4 bars) carries through for sure. From the middle of the piece the facts show almost none of the theme's tune or harmony, so a listener who tries to follow the tune will lose it.
- Evidence: `Variation 18 (73-76): tune presence [Vn 0.0, Va 0.0]; ... same harmony as theme: 0.0`; `Variation 19 ...: tune presence [Vn 0.0, Va 0.06]`.
- Fix: "Learn it. Every variation keeps its four-measure length, and the early ones stay close to its tune."

### P5. passacaglia · EN · Point 2 [m. 5-8] · STYLE
- Quote: "The volume stays at a strong, steady loud level."
- Problem: "Steady" ignores the diminuendo in m. 8.
- Evidence: `8|Variation 1|G minor|Vn|0.3|duet|f|<dim>`.
- Fix: "The volume stays loud, then eases off at the end [m. 8]."

### P6. passacaglia · EN · Point 5 [m. 25-36] · MISLEADING
- Quote: "The violin leads."
- Problem: There is no hedge, but half the bars in this range have lead confidence below 0.4. In Variation 8 the mean is about 0.40.
- Evidence: `27 ... 0.34`, `31 ... 0.39`, `32 ... 0.21`, `33 ... 0.34`, `34 ... 0.34`, `36 ... 0.29`.
- Fix: "The violin mostly seems to lead, though this is less certain in Variation 8."

### P7. passacaglia · EN · Point 5 [m. 25-36] · STYLE
- Quote: "The notes get faster and more crowded"
- Problem: The facts measure note density, not tempo. "Faster" may suggest the tempo speeds up.
- Evidence: `note density vs theme: 1.33x` / `1.41x` / `1.69x`.
- Fix: "Each bar holds more and more notes, but the volume mostly stays soft."

### P8. passacaglia · EN · Point 8 [m. 53-56] · MISLEADING
- Quote: "The players again move together in chords."
- Problem: Only m. 53 and 55 are homophonic. m. 54 and 56 are duet. The ZH version ("时而同步,时而各唱各的") is correct.
- Evidence: `53-53 homophonic; 54-54 duet; 55-55 homophonic; 56-65 duet`.
- Fix: "The players sometimes move together in chords and sometimes play separate lines."

### P9. passacaglia · EN · Point 9 [m. 57-64] · MISLEADING
- Quote: HEADLINE "Variations 14–15: viola in the spotlight, fading to pianissimo"
- Problem: The headline states the viola lead as fact, but the text admits it is uncertain (conf 0.36). The headline needs the same hedge.
- Evidence: `57-62 Va (conf 0.36)`.
- Fix: "Variations 14–15: the viola probably leads, then a sudden hush"

### P10. passacaglia · EN · Point 9 [m. 57-64] · MISLEADING
- Quote: "The sound fades from medium loud to very soft [m. 60-64]."
- Problem: The facts show a sudden new pp marking at m. 60, not a gradual fade (no diminuendo). Also m. 64 is p, not pp.
- Evidence: `59|...|mf|||`, `60|...|pp|pp||` (no `<dim>`), `64|...|p|p`.
- Fix: "The sound drops suddenly from medium loud to very soft at [m. 60] and stays very soft until [m. 64]."

### P11. passacaglia · EN + ZH · Overview (ZH), Points 11 and 13 · MISLEADING
- Quotes: EN P11 "Both players rest for two measures [m. 73-74]. ... This pause is a held breath before the final stretch."; EN P13 "[m. 88] is a silent bar that builds tension."; ZH overview "在第73至74小节出现两小节的停奏"; ZH P13 "[m. 88] 是短暂的停奏,为终曲做准备。"
- Problem: The facts report exactly 3 measures with no notes, and the only silent (tacet) measures are 73, 74 and 88. Variation 18 has only 0.11x the theme's note density. These silences may be optical-recognition losses, not real rests. The guide presents them as deliberate musical effects ("held breath", "builds tension") and as a main landmark in the ZH overview, with no warning.
- Evidence: `- score: ... 3 measure(s) have no notes.`; `73-74 tacet`, `88-88 tacet`; `Variation 18 (73-76): ... note density vs theme: 0.11x; ... main texture: tacet`.
- Fix EN P11: "The score shows two silent measures here [m. 73-74], though this may be a recognition error. The viola then enters alone [m. 75]."
- Fix EN P13: "The score shows [m. 88] as silent, which may be a recognition error."
- Fix ZH overview: "乐谱在第73至74小节显示两小节无声,但这可能是识别错误。"
- Fix ZH P13: "乐谱显示 [m. 88] 为空小节,可能是识别错误。"

### P12. passacaglia · EN · Points 12-14 vs glossary · STYLE
- Quotes: P12 "the volume leaps to very loud [m. 79-80]" (ff); P13 "The music stays very loud" (ff); P14 "The very loud playing continues" (fff); glossary "from very soft (pp) up to very loud (fff)".
- Problem: "Very loud" is used for both ff and fff. The glossary reserves it for fff, so the build to the loudest point at m. 90 cannot be heard in the wording.
- Evidence: `79|...|ff|ff`, `81-88 ... ff`, `90|...|fff|ff,fff`.
- Fix: glossary "...from very soft (pp) through very loud (ff) to extremely loud (fff)"; P14 "The extremely loud playing continues through the last bars [m. 91-93]."

### P13. passacaglia · ZH · Point 4 [m. 17-24] · MISLEADING
- Quotes: HEADLINE "轻与响交替,中提琴常带头"; TEXT "这一段中提琴可能常常领头"
- Problem: The violin clearly leads in m. 17-18 (conf 1.0) and again in m. 23-24. The viola leads only around m. 19-22 (conf 0.44). "常带头" in the headline has no hedge and overstates the viola's role. EN P4 is more accurate.
- Evidence: `17-18 Vn (conf 1.0); 19-22 Va (conf 0.44); 23-56 Vn (conf 0.49)`.
- Fix headline: "轻与响交替,中提琴一度接过主导"; text: "大约在 [m. 19-22] 中提琴可能接过主导,之后小提琴又回到前面。"

### P14. passacaglia · ZH · Point 6 and glossary · STYLE
- Quotes: "这种写法叫“同步和声式”"; glossary "同步和声式(homophonic)"
- Problem: "同步和声式" is not a standard Chinese term. The usual terms are "主调织体" or "和声式织体".
- Fix: "这种写法叫“主调织体”(homophonic):两件乐器节奏一致,听起来像一起奏和弦。" Glossary: "主调织体(homophonic):各声部节奏大体一致,听起来像一串和弦。"

### P15. passacaglia · ZH · Point 8 [m. 53-56] · STYLE
- Quote: HEADLINE "再次转强,变得宽广"
- Problem: "宽广" (broad) has no support in the facts: note density is 0.9x and there is no tempo information.
- Evidence: `Variation 13 (53-56): ... note density vs theme: 0.9x; ... dynamics: f, mf`.
- Fix: "再次转强"

### P16. passacaglia · ZH · Point 9 [m. 57-64] · MISLEADING
- Quotes: HEADLINE "中提琴可能领头,声音渐弱到极轻"; TEXT "力度从中强降到极弱 [m. 60]。第十五变奏保持很轻 [m. 61-64]。"
- Problem: "渐弱" means a gradual fade, but m. 60 is a sudden pp with no diminuendo. The same pp is called "极轻", "极弱" and "很轻" within one point. m. 64 is p.
- Evidence: `60|...|pp|pp||` (no `<dim>`), `61-63 ... pp`, `64|...|p|p`.
- Fix headline: "中提琴可能领头,声音突然变得很弱"; text: "到 [m. 60] 力度从中强突然降到很弱(pp),并一直保持到 [m. 63]。"

### P17. passacaglia · ZH · Point 10 [m. 65-72] · STYLE
- Quote: "最后一小节只有小提琴独奏 [m. 72]。"
- Problem: Readers may take "最后一小节" to mean the last bar of the whole piece.
- Fix: "这一变奏的最后一小节 [m. 72] 只有小提琴独奏。"

### P18. passacaglia · ZH · Point 13 [m. 81-88] · STYLE
- Quote: "[m. 88] 是短暂的停奏,为终曲做准备。"
- Problem: "终曲" means a finale movement, but what follows is the last variation. (See also P11 for the missing OCR hedge.)
- Fix: "乐谱显示 [m. 88] 为空小节(可能是识别错误),之后进入最后一个变奏。"

### Summary: passacaglia
Neither language contains a hard factual error. Sections, keys, dynamics and the solo/silent bars all match the facts, and both overviews state that keys are estimated and that the score came from optical recognition. The main weakness is in the EN overview, EN P1 and both glossaries: they use the textbook idea of a pattern repeating "again and again". The facts show the theme's harmony and tune fading to almost nothing in the later variations, and the ZH overview ("被不断改写") describes this better. The silent bars at m. 73-74 and 88 are exactly the three empty measures that the OCR note warns about, yet both languages present them as deliberate musical effects. Some lead and texture statements are stronger than the data: EN P5 and P8, EN P9's headline, and ZH P4. The two languages differ in emphasis but do not contradict each other on facts, except ZH P4 vs EN P4 on how much the viola leads. The ZH prose needs some term fixes: "同步和声式" → "主调织体", "终曲", "宽广", and consistent names for pp.

---

## Counts
- d929_1: ERROR 2, MISLEADING 9, STYLE 8 (19 findings)
- passacaglia: ERROR 0, MISLEADING 10, STYLE 8 (18 findings)
