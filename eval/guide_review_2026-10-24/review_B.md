# Review B: Haydn Op. 76 No. 3 "Emperor", movements I-IV (prose review)

Reviewer scope: prose of headline/text/overview/glossary in `haydn76_3_{1,2,3,4}_guide_{en,zh}.txt`, checked against the matching `_facts.txt`. Claims were already code-verified and are not re-checked except where the prose goes beyond them.

Severity: ERROR = factually wrong or invented; MISLEADING = defensible but a listener would be misled; STYLE = wording/translation.

All eight guides say at least once (in the overview) that keys/chords are estimated, so rule 3 (keys) is met everywhere. No outside history, biography, hymn history or performer information was found in any guide (rule 4 met).

---

## haydn76_3_1 (I. Allegro)

### 1-1 · EN point 4 + ZH point 4 · MISLEADING
- EN: "Accents (fz) stand out, then the music softens at [m. 22]."
- ZH: "[m. 22] 起音量转弱。"
- Problem: m. 22 has a very loud **ff** marking before the p. Both versions describe only the drop to soft, so a listener does not expect the loud burst.
- Evidence: `22|Part 1|D major|Vn1|1.0|melody + accompaniment|p|ff,p||...`
- Fix EN: "The key moves briefly to D major at [m. 20], with sharp accents (fz). At [m. 22] there is a very loud ff, and then the music drops at once to soft."
- Fix ZH: "[m. 20] 进入 D 大调,有 fz 重音。[m. 22] 先出现一个很强的 ff,随后立刻转弱(p)。"

### 1-2 · EN point 5 + ZH point 5 · MISLEADING
- EN: "The loudest point of the piece is at [m. 30], marked ff."
- ZH: "[m. 30-31] 是第一部分最响的地方,标记为 ff(很强)。"
- Problem: "loudest point" comes from a heuristic and is stated as fact. Also, m. 30 is not the only ff: m. 22 is marked ff too. The text should say that this is the computer's estimate.
- Evidence: `## LOUDEST/BUSIEST POINT (heuristic): measure 30 (ff, Part 1)`; `22|...|ff,p|`
- Fix EN: "At [m. 30] the music is marked ff (very loud). The computer estimates this as the loudest and busiest point of the movement."
- Fix ZH: "[m. 30-31] 标记为 ff(很强),软件估计这里是全乐章最响、最忙的地方。"

### 1-3 · EN point 10 + ZH point 11 · MISLEADING
- EN: "Then Violin 1 plays the main theme again, loud, in E minor [m. 78-80]. It has the same shape as the opening tune, but in a darker key."
- ZH: "[m. 78-80] 第一小提琴奏出开头的主旋律,只是现在在 E 小调里,听起来更暗。"
- Problem: the theme return is listed as **transposed 0 semitones**, so the notes are at exactly the same pitch as the opening, which was in C major. The "E minor" is only the auto-estimated label for m. 75-79. From m. 79 the measure table repeats m. 1-11 almost exactly (same chords, the same Violin 2 lead in the 5th bar, the same dynamics). A listener told to expect "a darker key" will hear the opening tune unchanged. The ZH guide also contradicts itself: point 12 says "[m. 80] 回到 C 大调,音乐很像开头的样子".
- Evidence: `main theme: Violin 1 78-80, exact, transposed 0 semitones, key E minor`; `79|...|C major C major` = `1|...|C major C major`; `80|...|D dominant seventh G major` = `2|...`; `83|...|Vn2|0.69` = `5|...|Vn2|0.69`; key plan `C major: 80-89`
- Fix EN: "Then Violin 1 plays the main theme again, at exactly the same pitch as the opening [m. 78-80]. The computer labels the key just before it as E minor. But from [m. 80] the music follows the opening closely, back in C major."
- Fix ZH: "[m. 78-80] 第一小提琴再次奏出开头的主旋律,音高和开头完全相同。软件把前面几小节的调性估计为 E 小调,但从 [m. 80] 起,音乐几乎和开头一样,回到 C 大调。"

### 1-4 · EN point 13 (headline) · MISLEADING
- EN: "Faster and soft, with a turn to C minor"
- Problem: the section is faster only on the **second** time through. The headline says it is faster now, but the text correctly says "marked to go faster on the repeat".
- Evidence: `Section 3 (la seconda volta più presto): 105-121b (17 measures, repeated)`
- Fix EN: "Soft, with a turn to C minor (faster the second time)"

### 1-5 · ZH point 3 · MISLEADING
- ZH: "之后第一小提琴大概率带着旋律往前走 [m. 13-19]。"
- Problem: 大概率 means "with high probability", but the confidence here is only 0.23-0.48. The hedge must be weaker (可能).
- Evidence: `13|...|Vn1|0.23`, `16|...|Vn1+Vc|0.0`, `12-32 Vn1 (conf 0.45)`
- Fix ZH: "之后第一小提琴可能带着旋律往前走 [m. 13-19],但这个判断把握不大。"

### 1-6 · ZH point 15 · STYLE
- ZH: "第一小提琴大概率领奏,不过领奏不太确定。"
- Problem: the sentence contradicts itself (大概率 = high probability, then 不太确定). The confidence is 0.26.
- Evidence: `115|...|Vn1|0.26`; `84-121b Vn1 (conf 0.39)`
- Fix ZH: "[m. 115] 起转强,第一小提琴可能在领奏,但不太确定。"

### 1-7 · ZH glossary · ERROR
- ZH: "齐奏式织体(homophonic)": "几件乐器节奏大致一致,像一起唱同一首歌。"
- Problem: 齐奏 means unison (everyone plays the same notes). Homophonic texture means the parts play **different** notes in the same rhythm, as chords. The Chinese guide for movement III uses "齐奏" for unison/octaves, so across the four movements the same word means two different things. The text of point 1 ("步调一致……同一个和声") is also inconsistent with "齐奏".
- Evidence: `0-2 homophonic` with chords listed (`0|...|G major`, `1|...|C major C major`); movement III ZH glossary: "齐奏/八度: 几件乐器同奏同一条旋律"
- Fix ZH: "主调织体(homophonic)": "几件乐器节奏大致一致,一起奏出和弦,旋律通常在最上面。"

### 1-8 · ZH glossary · STYLE
- ZH: "fz": "某个音突然加重,像轻轻一击。"
- Problem: "轻轻一击" (a light tap) contradicts "突然加重" (a sudden strong accent).
- Evidence: EN glossary: "fz: A sudden sharp accent on a note."
- Fix ZH: "某个音突然加重,像猛地一击。"

### 1-9 · ZH point 1 · STYLE
- ZH: "四件乐器步调一致,像在合唱同一个和声。"
- Problem: "合唱同一个和声" is unnatural Chinese and vague.
- Evidence: `0-2 homophonic`
- Fix ZH: "四件乐器节奏一致,一起奏出和弦,旋律在最上面。"

### 1-10 · EN points 7 and 14 · STYLE
- EN P7: "It swells to loud at [m. 38]."
- EN P14: "The music grows loud at [m. 115]..."
- Problem: "swells" and "grows" suggest a gradual crescendo. The facts show only a sudden new **f** marking and no crescendo.
- Evidence: `38|...|f|f|`; `115|...|f|f|`
- Fix EN P7: "It turns loud at [m. 38]."
- Fix EN P14: "The music turns loud at [m. 115], with Violin 1 probably on the melody."

### 1-11 · EN point 3 + ZH point 3 (headline) · STYLE
- EN: "This is a brighter, higher-feeling place to be."
- ZH headline: "转到 G 大调,气氛更明亮"
- Problem: the facts say nothing about G major being brighter or higher than C major (both are major keys). This is an unsupported impression.
- Evidence: key plan `C major: 0-10`, `G major: 11-19` (no other description)
- Fix EN: "At [m. 11] the key is estimated to change to G major."
- Fix ZH headline: "转到 G 大调"

**Summary, haydn76_3_1:** Overall accurate. Sections, keys, dynamics and hedges mostly follow the facts. The main problem is the theme return at m. 78: both languages call it "darker / in E minor". But the facts show it is at the same pitch as the opening, and the bars that follow copy the opening in C major. The ZH guide even contradicts itself on this between points 11 and 12. Two other issues: the "loudest point" heuristic is stated as fact and ignores the ff at m. 22, and both versions skip that ff when they describe m. 22. On the Chinese side, the glossary translates homophonic as 齐奏 (unison), which is wrong and clashes with movement III, and 大概率 is used for low-confidence leads.

---

## haydn76_3_2 (II. Poco adagio cantabile, variations)

### 2-1 · EN overview · MISLEADING
- EN: "The same tune is heard five times, each time in a different part. It starts in Violin 1, then moves to Violin 2, the cello, the viola, and back to Violin 1."
- Problem: this contradicts itself. Violin 1 has the tune twice (Theme and Var. IV), so it is not "each time in a different part".
- Evidence: `Theme ... tune mostly in: Violin 1`; `Var. IV ... tune mostly in: Violin 1`
- Fix EN: "The same tune is heard five times. It starts in Violin 1, then moves to Violin 2, the cello and the viola, and finally comes back to Violin 1."

### 2-2 · EN point 1 · MISLEADING
- EN: "Violin 1 plays the tune alone on top [m. 0-5]."
- Problem: "alone" suggests Violin 1 plays by itself, but the other three parts play throughout, and in m. 3-4 they all move together in chords.
- Evidence: `0-2 melody + accompaniment; 3-4 homophonic; 5-6 melody + accompaniment`
- Fix EN: "Violin 1 plays the tune on top [m. 0-5]. The other three parts accompany it softly."

### 2-3 · EN point 2 + EN glossary "D major" · STYLE
- EN P2: "This is a nearby key that feels a little brighter."
- EN glossary: "D major: A nearby key that sounds a little brighter than G major."
- Problem: the facts say nothing about D major sounding brighter than G major (both are major). This is an unsupported impression presented as a definition.
- Evidence: key plan only: `D major: 6-10`, `26-31`, `46-52`, `66-72`, `87-92`
- Fix EN P2: "The music is estimated to move to D major, a nearby key [m. 6-10]."
- Fix EN glossary: "D major: A nearby key. The music visits it in the middle of the theme and of every variation, then returns to G major."

### 2-4 · EN point 3 · STYLE
- EN: "Short sharp accents, marked fz, appear at [m. 12] and [m. 16]. After each one the music drops back to soft."
- Problem: the accents come in pairs of bars (12-13 and 16-17). They are not single accents.
- Evidence: `12|...|fz`, `13|...|fz`, `14|...|p`, `16|...|fz`, `17|...|fz`, `18|...|p`
- Fix EN: "Short sharp accents, marked fz, appear in [m. 12-13] and again in [m. 16-17]. After each pair the music is marked soft again."

### 2-5 · EN point 4 · MISLEADING
- EN: "The lead is uncertain, because the two lines are so close."
- Problem: the reason is invented. Also, the tune itself is not uncertain: tune presence in Violin 2 is 1.0. Only the lead detector's confidence is low.
- Evidence: `Var. I ... tune presence [Vn1 0.21, Vn2 1.0, ...]`; `20-39 Vn2 (conf 0.44)`
- Fix EN: "The tune itself is clearly in Violin 2. The computer is less sure which violin stands out more."

### 2-6a · ZH point 10 · ERROR
- ZH: "这只是个小细节,而且中提琴声音很淡。第一小提琴仍是主要旋律。"
- Problem: "中提琴声音很淡" (the viola is faint) is invented. The facts make the viola **co-lead** at m. 90. "第一小提琴仍是主要旋律" is stated without a hedge, but the confidence is 0.0 and 0.14.
- Evidence: `90|Var. IV|D major|Vn1+Va|0.0|...`; `91|...|Vn1|0.14`; `main theme: Viola 90-91, inverted, transposed 5 semitones`
- Fix ZH: "在 [m. 90-91],中提琴奏出主题“倒过来”的样子:原来向上的地方变成向下。这里第一小提琴和中提琴可能共同领奏,判断把握不大。"

### 2-6b · EN point 11 · MISLEADING
- EN: "Violin 1 keeps the tune above steady accompaniment."
- Problem: this is stated for all of m. 87-92, but at m. 90-91 the lead is shared with the viola, which plays the tune upside down, and the confidence there is very low.
- Evidence: same lines as 2-6a.
- Fix EN: "Violin 1 mostly keeps the tune. Around [m. 90-91] the viola also comes forward with the tune turned upside down, so the lead is shared there."

### 2-7 · ZH point 8 · MISLEADING
- ZH: "中提琴一直是最突出的声音。"
- Problem: the point covers m. 66-79, and in m. 66-68 the lead is uncertain (m. 67 is shared with Violin 1 at 0.03). "一直" (all the time) overstates it.
- Evidence: `66|...|Va|0.4`, `67|...|Va+Vn1|0.03`, `68|...|Va|0.41`; `73-79` Va 0.79-0.99
- Fix ZH: "[m. 73-79] 中提琴是最突出的声音;[m. 66-68] 一带领奏不太确定。"

### 2-8 · EN point 9 · STYLE
- EN: "The viola line stands out clearly above the accompaniment."
- Problem: "above" can be read as higher in pitch. The viola is an inner voice, and nothing in the facts says it is on top.
- Evidence: `73-74 independent lines; 75-76 melody + accompaniment`; lead Va 0.79-0.99
- Fix EN: "The viola line stands out clearly from the accompaniment."

### 2-9 · EN point 8 · STYLE
- EN: "The music dips briefly to D major from [m. 66]."
- Problem: "dips" suggests going down or darker, but this is the same D major region as in every other section. The word choice is odd.
- Evidence: `D major: 66-72`
- Fix EN: "The music moves briefly to D major from [m. 66]."

**Summary, haydn76_3_2:** The structure is described well: theme plus four variations, the tune moving Vn1 → Vn2 → Vc → Va → Vn1, the octave shifts (ZH), the soft dynamics and the pp ending. Hedging is generally good. The real error is in ZH point 10, which invents that the viola is "faint" at m. 90-91, where the facts make it co-lead. EN point 11 has the milder version of the same problem. The EN overview contradicts itself ("each time a different part"), and EN point 1's "alone" misleads. The rest is small: "brighter D major" in the text and glossary, an invented reason for the uncertain lead, and accents placed in single bars instead of pairs.

---

## haydn76_3_3 (III. Menuetto)

### 3-1 · ZH glossary "主调" · MISLEADING
- ZH: "一首乐曲的“家”,开头和结尾最有归属感的调。这里是 C 大调。"
- Problem: this score ends with the Trio at m. 100, and the last bars are estimated in A minor. So "the key at the beginning and the end … here C major" is contradicted by the facts. The ZH point 13 itself says "乐章在 [m. 100] … 结束", in A minor.
- Evidence: `home_key: C major`; key plan `A minor: 94-100`; `last_label: 100`
- Fix ZH: "一首乐曲的“家”,最有归属感的调。这个乐章的主调是 C 大调;不过乐谱最后是中段 Trio,结尾几小节估计在 A 小调。"

### 3-2 · EN point 3 + ZH point 3 (headline) · MISLEADING
- EN: "The loudest and busiest moment is here, still in G major [m. 13]."
- ZH headline: "全曲最响最忙的地方"
- Problem: this heuristic is stated as fact (the ZH text hedges, but its headline does not). The listener will not hear m. 13 as louder: m. 0-25 are all marked f, and no ff appears anywhere in the movement. Also, "全曲" should be "全乐章".
- Evidence: `## LOUDEST/BUSIEST POINT (heuristic): measure 13 (f, Part 1)`; `0-25` dynamic in force `f`
- Fix EN: "The computer estimates this as the busiest moment, still in G major [m. 13]. It is marked f, like the bars around it."
- Fix ZH headline: "软件估计的全乐章最忙之处"

### 3-3 · ZH point 6 · MISLEADING
- ZH: "力度重新回到 f,调性也回到 C 大调 [m. 32-36]。第一小提琴再次领奏。从安静突然回到响亮,请留意这个对比。"
- Problem: the main landmark is missing. The facts list an exact return of the main theme at m. 32-36, and the EN guide makes this the key moment ("The opening tune comes back"). The ZH overview and points never say the theme returns, so Chinese readers miss it.
- Evidence: `main theme: Violin 1 32-36, exact, transposed 0 semitones, key C major`
- Fix ZH: "第一小提琴再次奏出开头的主旋律,音符和开头完全一样;力度回到 f,调性回到 C 大调 [m. 32-36]。这是第一部分最容易辨认的时刻。"

### 3-4 · EN point 6 · STYLE
- EN: "It matches the opening exactly."
- Problem: the tune's notes match exactly, but the setting does not. At the opening Violin 1 starts alone (m. 0-1 solo). At m. 32 the others play at once. A listener waiting for a solo start may miss the return.
- Evidence: `0-1 solo; 2-4 melody + accompaniment` vs `32-32 melody + accompaniment; 33-33 solo; 34-36 melody + accompaniment`
- Fix EN: "The notes of the tune match the opening exactly. This time the other parts join in at once [m. 32], instead of Violin 1 starting alone."

### 3-5 · EN glossary "Menuetto" · MISLEADING
- EN: "A stately dance in three beats per bar."
- Problem: "stately" is outside knowledge and clashes with the movement's own marking, Allegro (fast).
- Evidence: `title: ... III. Menuetto (Allegro)`; `time_signature: 3/4`
- Fix EN: "A dance with three beats per bar. This one is marked Allegro, which means fast."

### 3-6 · ZH point 11 · MISLEADING
- ZH: "这里织体变化很多:有二重奏、三重奏,还有各声部同奏一个音的齐奏 [m. 69-75]。"
- Problem: (a) unison/octaves does not mean "all play **one note**" (同奏一个音). It means they play the same line, possibly octaves apart; the ZH glossary itself says so. (b) This happens only at m. 75, not across m. 69-75. (c) Calling a texture "三重奏" inside the section called Trio is confusing.
- Evidence: `69-69 duet; 70-70 trio; 71-71 independent lines; 72-73 melody + accompaniment; 74-74 solo; 75-75 unison/octaves`
- Fix ZH: "这里织体变化很多:[m. 69] 只有两件乐器,[m. 70] 是三件乐器一起奏,到 [m. 75] 各声部以齐奏或八度奏同样的音。"

### 3-7 · ZH point 4 · STYLE
- ZH: "这几小节里各件乐器的线条比较独立,各唱各的。"
- Problem: this is said for m. 22-25, but only m. 24-25 are independent lines. m. 22 is three instruments and m. 23 is melody + accompaniment.
- Evidence: `22-22 trio; 23-23 melody + accompaniment; 24-25 independent lines`
- Fix ZH: "[m. 24-25] 各件乐器的线条比较独立,各唱各的。"

### 3-8 · ZH point 9 · STYLE
- ZH: "第一小提琴常常几乎独奏。"
- Problem: "常常几乎" is clumsy and vague. The facts plainly say solo for m. 56-58.
- Evidence: `56-58 solo`
- Fix ZH: "第一小提琴独自演奏了几小节 [m. 56-58]。"

### 3-9 · EN point 11 · STYLE
- EN: "At m. 75 the instruments play the same notes together in octaves."
- Problem: the measure reference is not in the bracket format `[m. 75]` used everywhere else, so the player may not link it.
- Evidence: format of every other reference.
- Fix EN: "At [m. 75] the instruments play the same notes together, in unison or octaves."

### 3-10 · EN point 5 · STYLE
- EN: "The parts weave more separate lines, which is called independent lines [m. 27-31]."
- Problem: the wording is clumsy and circular.
- Evidence: `27-29 independent lines; 30-30 homophonic; 31-31 independent lines`
- Fix EN: "Each part now plays more of its own line [m. 27-31]."

**Summary, haydn76_3_3:** Keys, the Part 1/Trio split, repeats, the solo openings and the pp passage all follow the facts. The EN guide correctly points out the exact theme return at m. 32, but the ZH guide leaves it out completely, which is a real gap between the two languages. The "loudest point" at m. 13 is presented as fact, although the whole passage is marked the same f. The ZH glossary says the movement ends in C major, while the score here ends in A minor. Chinese wording for unison ("同奏一个音") and a few loose measure ranges need fixing. The EN glossary's "stately" is outside knowledge and clashes with Allegro.

---

## haydn76_3_4 (IV. Finale, Presto)

### 4-1 · EN point 6 (headline vs text) · MISLEADING
- EN headline: "Tune passed around, then a soft close to Part 1"
- EN text: "The music gets soft at [m. 68]. It jumps back to loud at [m. 72b], where Part 1 ends. This part is repeated."
- Problem: the headline says Part 1 closes softly, and the text says it ends loud, so they contradict each other. The text also puts the loud m. 72b **before** the repeat. The a/b labels show two different endings: the soft one runs through 71a and the loud bar is 72b.
- Evidence: `68|...|p|p|`; `71a|...|p|`; `72b|...|f|f|`; `Part 1: 1-72b (72 measures, repeated)`
- Fix EN headline: "Tune passed around, then soft and loud endings to Part 1"
- Fix EN text: "The music gets soft at [m. 68] and stays soft through [m. 71a]. The bar labelled [m. 72b] is loud. Part 1 is repeated."

### 4-2 · ZH point 6 · STYLE
- ZH: "[m. 68-71a] 在 [m. 72b] 又转为强(f)。"
- Problem: the sentence is broken (two measure references with no verb linking them).
- Evidence: `68-71a p`, `72b f`
- Fix ZH: "[m. 68] 突然变弱(p),第一小提琴继续带着旋律,一直轻到 [m. 71a]。[m. 72b] 又转为强(f)。这一部分要反复一遍。"

### 4-3a · EN point 5 · MISLEADING
- EN headline: "Settling in E-flat major, then building to a peak"; text: "The loudest and busiest point of Part 1 is at [m. 56]."
- Problem: "building" suggests a gradual crescendo, but there is only a sudden f at m. 46. The "loudest point" is a heuristic stated as fact, and m. 46-67 are all equally marked f.
- Evidence: `46|...|f|f|`; no cresc markings in 38-57; `## LOUDEST/BUSIEST POINT (heuristic): measure 56 (f, Part 1)`
- Fix EN headline: "Settling in E-flat major, then turning loud"
- Fix EN text: "The computer estimates the busiest point of Part 1 at [m. 56]. It is marked f, like the bars around it."

### 4-3b · ZH point 5 · MISLEADING
- ZH headline: "进入 Eb 大调,力度渐强到最响处"; text: "[m. 38] 到 [m. 46] 重新变强(f)"
- Problem: 渐强 is the technical term for crescendo, and no crescendo is marked here. "[m. 38] 到 [m. 46] 重新变强" also suggests a gradual rise across those bars, but m. 38-45 are p and m. 46 is a sudden f.
- Evidence: `38-45` dynamic `p`; `46|...|f|f|`
- Fix ZH headline: "进入 Eb 大调,由弱突然转强"
- Fix ZH text: "[m. 38-45] 保持轻声,到 [m. 46] 突然变强(f),第一小提琴明显领头。软件估计第一部分最忙的地方在 [m. 56]。"

### 4-4 · EN point 14 · MISLEADING
- EN: "The lead moves among all four players."
- Problem: the viola never leads alone in m. 159-188. It appears only once, as a co-lead with confidence 0.08 (m. 176). Many lead values here are also below 0.4, but the sentence has no hedge.
- Evidence: `145-171 Vn1 (conf 0.37); 172-175 Vn2 (conf 0.33); 176-176 Vn1 (conf 0.08); 177 Vn2; 178 Vn1; 179 Vc; 180 Vn1; 181 Vn2; 182-184 Vc (conf 0.36); 185-188 Vn1`; `176|...|Vn1+Va|0.08`
- Fix EN: "The lead seems to move between Violin 1, Violin 2 and the cello, and it is often unclear."

### 4-5 · EN point 2 · MISLEADING
- EN: "Now the first violin sings over an accompaniment."
- Problem: this is said for m. 5-17 without a hedge. In fact m. 6 and 12 are shared (confidence 0.0 and 0.06), and the cello leads at m. 13 (the ZH guide says so).
- Evidence: `6|...|Vn1+Vn2|0.0`; `12|...|Vn1+Vc|0.06`; `13-13 Vc (conf 0.73)`
- Fix EN: "The first violin mostly sings over an accompaniment, and the cello briefly takes the tune [m. 13]."

### 4-6 · EN point 11 (headline) · MISLEADING
- EN: "Soft and low, then fading to the quietest point"
- Problem: m. 123 is marked **f**, so the passage does not start soft. Nothing in the facts says "low" (register). "Fading" suggests a diminuendo, but there is only a sudden pp marking at m. 133.
- Evidence: `123|...|f|f|`; `124|...|p|p|`; `133|...|pp|pp|`; no dim markings in 123-139
- Fix EN: "The opening pattern again, then the quietest point"

### 4-7 · EN point 12 (headline) · MISLEADING
- EN: "Dark keys, then a pause on G major"
- Problem: nothing in the facts shows a pause. m. 148-150 are loud, busy independent lines.
- Evidence: `148|...|f|`, `148-148 independent lines; 149-149 melody + accompaniment; 150-150 independent lines`
- Fix EN: "Dark keys, then G major"

### 4-8 · ZH point 8 · ERROR
- ZH: "[m. 87-91] 第一、第二小提琴交替担任主角……中间短暂触及 C 小调。[m. 92-93] 之后又回到 Ab 大调。[m. 97-105]"
- Problem: (a) The alternation between the violins happens at m. 98-103, not m. 87-91. In m. 87-91 Violin 2 leads one bar, then Violin 1 leads. (b) The way the references are placed, the text reads "after m. 92-93 it returns to A-flat major", which skips E-flat major in m. 94-96. The EN guide has this right.
- Evidence: `87|...|Vn2|0.38`, `88-90 Vn1 0.64-0.72`; `99 Vn2, 100 Vn1, 101 Vn2, 102 Vn1, 103 Vn2`; key plan `C minor: 92-93`, `Eb major: 94-96`, `Ab major: 97-105`
- Fix ZH: "这一段大多在 Ab 大调上。中间 [m. 92-93] 短暂触及 C 小调,[m. 94-96] 经过 Eb 大调,[m. 97-105] 又回到 Ab 大调。[m. 98-103] 第一、第二小提琴交替担任主角,但判断并不十分确定。"

### 4-9 · ZH point 4 · MISLEADING
- ZH: "[m. 28-37] 各声部的线条相对独立,像互相对话。"
- Problem: only m. 33-36 have independent lines. m. 28-32 are melody + accompaniment or chords. The EN guide correctly says [m. 33-36].
- Evidence: `27-28 melody + accompaniment; 29-29 homophonic; 30-31 melody + accompaniment; 32-32 homophonic; 33-36 independent lines; 37-37 melody + accompaniment`
- Fix ZH: "后面 [m. 33-36] 各声部的线条相对独立,像互相对话。"

### 4-10 · ZH overview · STYLE
- ZH: "这是一首以 C 小调开始的快板终曲"
- Problem: 快板 is the standard translation of Allegro. This movement is marked Presto (急板), and the ZH title itself says "(Presto)".
- Evidence: `title: ... IV. Finale (Presto)`
- Fix ZH: "这是一首以 C 小调开始的急板(Presto)终曲"

### 4-11 · ZH points 3, 7, 10 · STYLE
- ZH P3: "[m. 18-20] 中提琴可能暂时领头……随后又短暂转到 G 小调。[m. 21-22]"
- ZH P7: "第二部分从强奏开始。[m. 73] 随后在 [m. 79]……"
- ZH P10: "这是全曲最容易辨认的回归点。[m. 120] 随后转弱。"
- Problem: measure references come after the full stop, so they attach to the wrong sentence. In P3 the viola reference also extends to m. 20, where the lead is Violin 2 + Violin 1.
- Evidence: `18|...|Va|0.99`, `19|...|Va+Vc|0.0`, `20|...|Vn2+Vn1|0.11`; `21-22 G minor`
- Fix ZH P3: "[m. 18-19] 中提琴可能暂时领头,但判断把握不大。随后 [m. 21-22] 又短暂转到 G 小调。"
- Fix ZH P7: "第二部分从强奏开始 [m. 73]。随后在 [m. 79] 转为弱奏的 Bb 大调……"
- Fix ZH P10: "这是全乐章最容易辨认的回归点。随后在 [m. 120] 转弱。"

### 4-12 · ZH glossary · STYLE
- ZH: "同步和声(homophonic)"
- Problem: this is not a standard term. The four Chinese guides translate homophonic three different ways: 齐奏式织体 (I), 和声式织体 (III), 同步和声 (IV).
- Evidence: glossaries of movements I, III and IV.
- Fix ZH: "主调织体(homophonic)": "各声部节奏大体一致,一起奏出和弦。" (use the same term in all four movements)

### 4-13 · EN point 9 · STYLE
- EN: "The tension builds before the opening tune comes back."
- Problem: nothing in the facts shows a build. The dynamic stays f with no crescendo, and the texture stays melody + accompaniment until m. 118.
- Evidence: `110-119` dynamic `f`, no new markings; `107-117 melody + accompaniment; 118-122 homophonic`
- Fix EN: "It stays loud, with the first violin mostly in front, right up to the return of the opening tune."

### 4-14 · EN point 7 · STYLE
- EN: "The second violin probably leads here, but the lead is unclear."
- Problem: "here" seems to cover all of m. 73-86, but Violin 2 leads only from m. 84. Before that the lead is Violin 1 (low confidence).
- Evidence: `65-83 Vn1 (conf 0.54); 84-87 Vn2 (conf 0.39)`
- Fix EN: "From [m. 84] the second violin probably leads, but the lead is unclear."

**Summary, haydn76_3_4:** The large shape is right in both languages: C minor to C major, Part 1 repeated, the exact theme return at m. 119, the pp low point at m. 133 and the new section at m. 151. Hedging is good in most places. The weak points are dynamics and measure placement. EN point 6's headline contradicts its own text about how Part 1 ends. Several headlines add things the facts do not show ("building", "fading", "low", "pause"). The ZH guide adds a crescendo (渐强) that is not marked. EN point 14 claims all four players lead. The worst Chinese issue is point 8: the violin exchange is placed at the wrong bars, and the E-flat major passage is skipped. The Chinese also has several dangling measure references, uses 快板 for Presto, and uses a different, nonstandard word for homophonic than the other movements.

---

## Cross-piece notes (no extra findings counted)
- The ZH guides use "全曲" (whole piece) where they mean the movement (II overview, III point 3, IV point 10, I point 11). Prefer "全乐章".
- The "loudest/busiest point" heuristic is stated as plain fact in EN for I, III and IV. Every guide should add "the computer estimates", as the ZH guide for III does in its text.
- Homophonic should get one standard Chinese term (主调织体) across all four movements. 齐奏 should be kept only for unison/octaves.
