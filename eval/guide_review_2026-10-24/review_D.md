# Review D: Beethoven Op. 18 No. 5, movements I–IV (listening guides, EN + ZH)

Severity key: ERROR = factually wrong or invented; MISLEADING = defensible but a listener would be misled; STYLE = wording or translation.
"Facts" quotes come from `P_facts.txt` (measure-table rows are given as `label|section|key|lead|conf|texture|dyn|new markings|cadence|chords`).

---

## op18no5_1 (I. Allegro)

### 1-1 · EN + ZH · Point 1 · MISLEADING
- EN: "It starts softly, with sharp little accents." ZH: "乐章在 A 大调中轻声开始。"
- Problem: bar 1 also carries an **f** marking. "Starts softly" may be wrong for the very first sound. The matching return at m. 136 has no f, so the opening is not simply soft.
- Evidence: `1|Part 1|A major|Vn1|1.0|melody + accompaniment|p|f,sfp,sf||I` vs `136|...|p|sfp,sf||I`.
- Fix EN: "Bar 1 has loud and accented markings (f, sfp, sf), but the tune soon settles to soft."
- Fix ZH: "第 1 小节带有强(f)和突强(sfp、sf)记号,随后主旋律在轻声(p)中展开。"

### 1-2 · ZH · Point 1 · MISLEADING
- "第 4 小节只有第一小提琴独奏,像一个小小的停顿 [m. 4]。"
- Problem: m. 4 is a solo line, not a pause. Calling it "a small pause" tells the listener to expect silence.
- Evidence: `4|Part 1|A major|Vn1|1.0|solo|p|||`
- Fix: "第 4 小节其他乐器停下,只剩第一小提琴独自演奏 [m. 4]。"

### 1-3 · ZH · Point 2 · MISLEADING
- "接着出现渐强,也就是声音一点点变大 [m. 21-22]。到第 23 小节突然变成强。"
- Problem: the forte at m. 23 comes at the end of a marked crescendo, which starts at m. 17. It is not sudden. The EN version ("grows louder ... reaches forte") is correct.
- Evidence: `17|...|<cresc>`, `21|...|<cresc>`, `22|...|<cresc>`, `23|...|f|f||V`
- Fix: "经过渐强(声音一点点变大)[m. 21-22],到第 23 小节达到强(f)。"

### 1-4 · ZH · Point 2 · STYLE
- "从这里开始,乐器更多地一起走,织体变得整齐 [m. 17-18]。"
- Problem: "织体变得整齐" is vague and not a standard term.
- Evidence: `17-18 homophonic`
- Fix: "第 17-18 小节,各声部以相同节奏一起移动,形成和弦式(主调)织体。"

### 1-5 · EN · Points 3 and 7 · MISLEADING
- P3: "It opens with all instruments in octaves, playing the same notes [m. 25]." P7: "Part 2 starts with everyone playing the same notes in octaves [m. 81]."
- Problem: the texture label is `unison/octaves`. It does not say that all four instruments take part. The ZH text correctly says "几件乐器".
- Evidence: `25-25 unison/octaves`, `81-81 unison/octaves` (no part count given).
- Fix P3: "It opens with the instruments playing the same line in unison or octaves [m. 25]." Fix P7: "Part 2 starts with the instruments playing one line together in octaves [m. 81]."

### 1-6 · EN · Points 4 and 13 · MISLEADING (hedging rule)
- P4: "Then the second violin takes the lead, and the texture becomes a trio, meaning three parts [m. 43-47]." P13: "The second violin takes the lead, and a trio of three parts plays [m. 183-187]."
- Problem: the lead confidence for both spans is below 0.4, so the text must hedge. The ZH text hedges ("大概……把握不大"). Also, m. 43 is not yet a trio.
- Evidence: `43-47 Vn2 (conf 0.28)`, `183-187 Vn2 (conf 0.28)`; `44 ... Vn2+Va|0.0|trio`; `43-43 melody + accompaniment`, `44-47 trio`.
- Fix P4: "At m. 43 the second violin steps forward. Then only three parts play (a trio), and the lead is probably shared between the second violin and viola [m. 44-47]." Use the same wording for P13 with m. 183 / 184-187.

### 1-7 · EN · Point 7 · MISLEADING
- Headline: "Part 2 begins in octaves, then loud steps downward"
- Problem: the facts contain no melodic direction. "Steps downward" is invented.
- Evidence: m. 82-87 give only chords (`#viio7/ii ii ...`, `viio43 I6 viio6`) and `f`; no contour data.
- Fix: "Part 2 begins in octaves, then turns loud and chordal"

### 1-8 · EN + ZH · Point 8 · MISLEADING
- EN: "The parts weave quietly with their own separate lines [m. 89-98]." ZH: "各声部的线条互相交错 [m. 89-98]。"
- Problem: only every other bar has independent lines. The other bars are melody + accompaniment.
- Evidence: `89-90 melody + accompaniment; 91 independent lines; 92 melody + accompaniment; 93 independent lines; 94 m+a; 95 independent; 96 m+a; 97 independent; 98 m+a`
- Fix EN: "Quietly, bars of tune-and-accompaniment alternate with bars where the parts move on their own lines [m. 89-98]." Fix ZH: "轻声中,“旋律加伴奏”的小节和各声部独立进行的小节交替出现 [m. 89-98]。"

### 1-9 · EN + ZH · Point 8 · MISLEADING
- EN: "The loudest and busiest point is [m. 101]." ZH: "第 101 小节是这个乐章最响最忙的地方。"
- Problem: the facts mark this as a heuristic. m. 101 is only `f`, the same level as many other passages (23, 48, 51-65, 82-87). A listener will expect a clear peak.
- Evidence: `LOUDEST/BUSIEST POINT (heuristic): measure 101 (f, Part 2)`; `101|...|f|f||I`
- Fix EN: "The analysis marks [m. 101] as the busiest loud moment." Fix ZH: "按分析,第 101 小节是本乐章最密集的强奏点之一。"

### 1-10 · ZH · Point 5 · ERROR
- "这里有强弱交替,也有带重音的突出音符 [m. 49-51]。"
- Problem: m. 49-51 have no accent marks. The sf accents start at m. 52.
- Evidence: `49|...|p|p||`, `50|...|p|||`, `51|...|f|f||I`; first sf at `52|...|f|sf||V V6`
- Fix: "第 49-51 小节轻(p)和强(f)交替出现。"

### 1-11 · EN · Point 11 · STYLE
- "The first violin keeps the tune going [m. 140-150]."
- Problem: the point's range is 151-163, and Point 10 ends at 139. The reference falls just outside every point.
- Evidence: `POINT 11 [m. 151-163]`
- Fix: change the point range to [m. 140-163], or keep the sentence and add "(just before this point)".

### 1-12 · ZH · Point 12 · ERROR
- Headline: "第一部分的材料重现,调性更暗". Text: "这里和第一部分对应的段落相比,调性整体降到了更暗的色彩。"
- Problem: invented comparison. Both passages are minor key areas with a short major flash (E minor/G major/E minor vs A minor/C major/A minor). Nothing in the facts says one is darker. It also contradicts the EN version: "with the same dark mood as before".
- Evidence: KEY PLAN `E minor: 25-30; G major: 31-32; E minor: 32-36` vs `A minor: 164-170; C major: 170-172; A minor: 173-176`
- Fix headline: "第一部分的小调材料重现". Fix text: "这段和第一部分第 25-36 小节相对应,同样是小调,只是换成了 A 小调。"

### 1-13 · ZH · Point 12 · MISLEADING
- "第 165 小节几件乐器再次齐奏。之后再次出现短暂的暗色 A 小调 [m. 173-176]。"
- Problem: A minor already starts at m. 164/165, not after it. The C major flash (170-172), which EN mentions, is left out. The listener gets the wrong timeline.
- Evidence: `A minor: 164-170`, `C major: 170-172`, `A minor: 173-176`
- Fix: "第 165 小节起转入 A 小调,几件乐器再次齐奏。第 171-172 小节短暂转亮到 C 大调,随后回到 A 小调并减弱到 pp [m. 173-176]。"

### 1-14 · EN · Point 14 · MISLEADING
- Headline: "Viola solo, octaves, and a calm slide to the end"
- Problem: the second ending of Part 2 is loud, so the close of this section is not a calm slide.
- Evidence: `220a|...|p|<cresc>`, `219b|...|f|f||I`
- Fix: "Viola solo, octaves, and soft phrases before a loud second ending"

### 1-15 · EN · Point 15 · MISLEADING
- Headline: "A soft goodbye, then two loud closing chords"
- Problem: the facts give one chord label per bar (V7, I). They do not say how many chords are actually played. "Two chords" is invented detail.
- Evidence: `224|...|f|f||V7`, `225|...|f|||I`
- Fix: "A soft start, then a loud close on the home chord"

### 1-16 · ZH · Point 10 · STYLE
- "第 136 小节开头的主旋律在第一小提琴中原样回来"
- Problem: this can be read as "the theme at the start of bar 136".
- Fix: "从第 136 小节起,乐章开头的主旋律由第一小提琴原样奏出。"

### 1-17 · ZH · Point 15 · STYLE
- "第 208 小节起声音渐强"
- Problem: the crescendo is marked at m. 207 (the claim also says 207), and m. 208 carries sfp.
- Evidence: `207|...|p|<cresc>||I`, `208|...|p|sfp||...`
- Fix: "第 207 小节起标有渐强"

### 1-18 · ZH · Overview · STYLE
- "全曲分三大块"
- Problem: this is one movement, not the whole work.
- Fix: "本乐章分三大块"

### 1-19 · ZH · Glossary · STYLE
- "转调 … 听起来像是气氛突然变亮或变暗。" and "f 是响"
- Problem: a key change is not always sudden. The standard term for f is 强.
- Fix: "转调:音乐从一个调换到另一个调,色彩常随之变亮或变暗。" "pp 是很弱,p 是弱,f 是强,sf 是突强。"

### 1-20 · EN · Glossary · STYLE
- "Trio / duet: Only three parts (trio) or two parts (duet) play the main material."
- Problem: "main material" is vague. The texture label means that only three (or two) instruments are sounding.
- Fix: "Only three (trio) or two (duet) of the four instruments are playing."

**Summary op18no5_1.** Keys, sections, repeats and the theme return at m. 136 are reported correctly in both languages. The main problems are in the ZH text. It invents accents at m. 49-51. It also claims the A minor return is "darker" than the Part 1 E minor passage, which contradicts the EN text, and it blurs the order of keys around m. 164-176. The EN text drops the hedge for the second violin twice (conf 0.28), adds a melodic direction and a chord count that are not in the facts, and twice says "all/everyone" for octave passages. The opening is called "soft", although bar 1 also carries an f marking.

---

## op18no5_2 (II. Menuetto)

### Machine flag check: EN Point 7 "A minor"
- The sentence is: "A minor key sounds more serious and shadowed than a major one." Here "A" is the article ("a minor key"). It does not name the key of A minor, so it is **not a key error**. It is ambiguous on first reading, though, especially beside "C# minor". Logged as 2-6 (STYLE).

### 2-1 · EN · Point 1 · ERROR
- "The first violin plays the main theme by itself, quietly [m. 0-3]. Then the other players join as accompaniment."
- Problem: the first violin is alone only in m. 0. The accompaniment is already there from m. 1. The ZH version is correct ("只有第一小提琴独奏 [m. 0]").
- Evidence: `0-0 solo; 1-10 melody + accompaniment`
- Fix: "The first violin starts the main theme alone and quietly [m. 0]. From [m. 1] the others join as accompaniment."

### 2-2 · EN · Point 9 · ERROR
- "Then the first violin brings back the main theme, soft and alone [m. 46-49]."
- Problem: the first violin is alone only in m. 46. The ZH version is correct.
- Evidence: `46-46 solo; 47-57 melody + accompaniment`
- Fix: "Then the first violin brings back the main theme, alone and soft at first [m. 46]. The others join from [m. 47]."

### 2-3 · EN + ZH · Overview (and ZH Glossary) · MISLEADING
- EN: "Listen for the opening tune as it moves between instruments and keys." ZH: "开头那段轻柔的主旋律如何在不同乐器和不同调里出现". ZH glossary: "会在不同乐器和不同调里重现。"
- Problem: every return is at the same pitches (0 semitones) or exactly an octave lower (-12), so the tune never actually changes key. The key names on the returns are just the local key at their first bar. The return at 46 is labelled C# minor, but m. 47-49 are A major.
- Evidence: `main theme: Viola 12-15, exact, transposed -12 semitones, key E major`; `main theme: Violin 1 46-49, exact, transposed 0 semitones, key C# minor`; `13|Menuetto|A major`, `47|Menuetto|A major`
- Fix EN: "Listen for the opening tune as it passes from the violin to the viola (an octave lower) and back." Fix ZH: "请留意开头的主旋律如何从第一小提琴传到中提琴(低一个八度),之后又回到第一小提琴。" Glossary ZH: "主旋律:全乐章最容易记住的那段曲调,会由不同乐器再次奏出。"

### 2-4 · EN · Point 3 · MISLEADING
- "The viola plays the main theme in E major [m. 12-15]. ... Then the music turns back to A major [m. 13-21]."
- Problem: only m. 12 is E major, and m. 13-15 are A major. The text contradicts itself ("in E major" for 12-15, then A major "then" from 13). The tune is the same notes one octave lower, so it is in effect in the home key.
- Evidence: `12|Menuetto|E major|Va|0.89`, `13|Menuetto|A major|Va|0.77`; transposition -12.
- Fix: "The viola plays the main theme, one octave lower [m. 12-15]. As it enters, the music slips back from E major to A major [m. 13]."

### 2-5 · EN · Point 2 · MISLEADING
- "The music moves to a new home key, E major [m. 10-12]."
- Problem: the home key stays A major. E major is a brief local key.
- Evidence: `"home_key": "A major"`; `E major: 10-12`
- Fix: "The music moves briefly to a new key, E major [m. 10-12]."

### 2-6 · EN · Point 7 · STYLE
- "A minor key sounds more serious and shadowed than a major one."
- Problem: this reads at first as the key of A minor, which does not occur here (see the flag check above).
- Fix: "Minor keys sound more serious and shadowed than major ones."

### 2-7 · EN · Overview · MISLEADING
- "The Trio then gives a calmer, more accented contrast."
- Problem: "calmer" is not supported. The Menuetto is also p almost throughout, and the Trio has an sf in nearly every bar from m. 82 to 87 and m. 98 to 103.
- Evidence: Trio rows 82-87 and 98-103 all `sf`; Menuetto dynamics `p` except m. 44-45 (ff) and m. 72 (f).
- Fix: "The Trio stays soft but has a sharp accent in almost every bar."

### 2-8 · EN + ZH · Glossary / ZH Overview · MISLEADING
- EN glossary: "Trio: The middle section of a minuet. It contrasts with the main part and is usually calmer." ZH glossary: "小步舞曲中间的对比段落". ZH overview: "后面是较短的中段(Trio)".
- Problem: "middle" and "usually calmer" are general outside knowledge. In the facts the Trio is the last section (81-105), with no return of the Menuetto. A listener using the player will not hear a "middle" section.
- Evidence: `SECTIONS: Menuetto: 0-81b ...; Trio: 81-105`
- Fix EN: "Trio: the contrasting second section of this movement." Fix ZH glossary: "Trio(三声中部):与小步舞曲主体形成对比的段落,这里在主体之后出现。" ZH overview: "后面是较短的对比段落 Trio(三声中部)".

### 2-9 · EN · Point 10 · MISLEADING
- "The lead passes around. The viola has it first [m. 59-61]."
- Problem: in the D major passage the first violin leads first (m. 55-57), before the viola.
- Evidence: `55|...|D major|Vn1|0.34`, `56|...|Vn1|1.0`, `57|...|Vn1|0.9`; span `46-58 Vn1 (conf 0.6)`
- Fix: "The first violin leads at first [m. 55-57]. Then the viola takes over [m. 59-61]."

### 2-10 · ZH · Point 10 · MISLEADING
- "接下来旋律像接力一样换手:中提琴 [m. 59]、第二小提琴 [m. 62]、再到大提琴 [m. 67]。"
- Problem: this skips the first violin's return (64-66), so the hand-over looks as if it goes straight from the second violin to the cello. It also states the cello lead without a hedge, although its span confidence is below 0.4. EN hedges this.
- Evidence: `64-66 Vn1 (conf 0.6)`; `67-70 Vc (conf 0.36)`
- Fix: "旋律像接力一样换手:中提琴 [m. 59]、第二小提琴 [m. 62]、第一小提琴 [m. 64],之后可能交给大提琴 [m. 67],但不太确定。"

### 2-11 · EN · Point 11 · MISLEADING (minor)
- "A short loud chord at [m. 72] drops quickly back to soft."
- Problem: the whole bar is marked f and holds three chords. It is not one short chord.
- Evidence: `72|...|f|f||IV ii V7`
- Fix: "One loud bar [m. 72] drops straight back to soft [m. 73]."

### 2-12 · EN · Point 12 · MISLEADING
- "Then come punchy accented chords [m. 82-87]."
- Problem: the dynamic stays p throughout, and the bars alternate between chords and melody + accompaniment. "Punchy chords" suggests loud block chords.
- Evidence: `82-87 ... dynamic p ... sf`; textures `82-83 homophonic; 84 m+a; 85 homophonic; 86-88 m+a`
- Fix: "Then each bar gets a sharp accent, while the overall level stays soft [m. 82-87]."

### 2-13 · EN · Point 14 · MISLEADING
- Headline: "The Trio repeats with violin on top, then ends"
- Problem: at m. 94 a phrase is restated, but the Trio itself does not start again there. The listener may think the section repeat begins at m. 94.
- Evidence: chords `90: I6 V6 I; 91: V43 vi7 V6` = `94: I6 V6 I; 95: V43 vi7 V6`
- Fix: "The first violin restates the phrase, then the Trio ends"

### 2-14 · ZH · Points 1 and 9 · STYLE
- "只有第一小提琴独奏,音量很轻 [m. 0]" / "音量回到很轻 [m. 46]"
- Problem: the marking is p (弱/轻). "很轻" suggests pp.
- Fix: "音量轻(p)"

### 2-15 · ZH · Point 5 · STYLE
- "这叫“和声式”"
- Problem: this is not the usual term for homophonic texture.
- Fix: "这叫主调织体(和弦式织体):各声部节奏一致,一起移动。" (Also update the glossary entry.)

### 2-16 · ZH · Point 6 · STYLE
- Headline: "回到A大调,小提琴留出独奏的空隙"
- Problem: the logic is reversed. It is the accompaniment that stops, not the violin that "leaves gaps".
- Fix: "回到A大调,伴奏两次停下,只剩第一小提琴"

### 2-17 · ZH · Point 8 · STYLE
- "出现一小格空白"
- Problem: awkward wording.
- Fix: "出现一整小节的静默"

### 2-18 · ZH · Point 15 · STYLE
- Headline: "小提琴重复前面的想法,收束全曲"
- Problem: m. 105 ends this movement (the Trio), not the whole work.
- Fix: "第一小提琴再现前面的乐句,Trio 结束"

**Summary op18no5_2.** Sections, dynamics, the ff peak at m. 44 and the silent m. 45 are reported correctly. Two EN "alone" statements are wrong: m. 0-3 and m. 46-49 are solo only in their first bar, and ZH gets both right. The biggest conceptual problem is in both languages: the guide treats the theme as moving "between keys", but every return is at the same pitch or an octave lower. EN P3 also contradicts itself on E major vs A major. The flagged "A minor" is the article "a", so it is not a key error, but it should be reworded. Calling the Trio "calmer" and a "middle section" comes from outside knowledge and is not in the facts. ZH P10 drops a needed hedge on the cello lead.

---

## op18no5_3 (III. Andante cantabile, theme and variations)

### Machine flag check: ZH Point 8 variation name
- ZH P8 says "第五变奏突然变响 / 第五变奏一开始就是强(f)" for [m. 80-88a]. Facts: `Var. 5: 80-128` and `80|Var. 5|D major|Vn2|0.38|unison/octaves|f|f||`. **The name is correct.** All other ZH variation names (第一 at m. 16, 第二 at m. 32, 第三 at m. 48, 第四 at m. 64) also match the facts. No finding.

### 3-1 · EN + ZH · Point 1 · ERROR
- EN: "Violin 1 plays the tune alone at the start, softly [m. 0-3]." ZH: "第一小提琴独自轻声奏出主题 [m. 0-3]。"
- Problem: Violin 1 is alone only in m. 0.
- Evidence: `0-0 solo; 1-1 melody + accompaniment; 2-6 independent lines`
- Fix EN: "Violin 1 starts the tune alone and softly [m. 0]. The others join from [m. 1]." Fix ZH: "第一小提琴先独自轻声奏出主题的开头 [m. 0],从第 1 小节起其他乐器加入。"

### 3-2 · EN + ZH · Point 1 · MISLEADING
- EN: "It begins high and steps gently downward." ZH: "旋律从高处一步步往下走"
- Problem: the tune starts on A4 and leaps up to F#5. Only after that does it step down.
- Evidence: `notes A4 F#5 E5 D5 C#5 B4 A4 A4 B4`
- Fix EN: "It opens with a leap upward, then steps gently down." Fix ZH: "旋律先向上一跳,然后一步步往下走。"

### 3-3 · EN + ZH · Point 1 · MISLEADING
- EN: "The other players mostly accompany." ZH: "其他乐器在下面伴奏"
- Problem: most of m. 2-8 is labelled independent lines, not accompaniment.
- Evidence: `2-6 independent lines; 7-7 melody + accompaniment; 8-8 independent lines`
- Fix EN: "Soon the other parts move with lines of their own under the tune [m. 2-6]." Fix ZH: "从第 2 小节起,其他声部也有各自的线条 [m. 2-6]。"

### 3-4 · EN · Point 1 · MISLEADING
- "Each section is repeated, so you hear every one twice."
- Problem: the coda is not repeated.
- Evidence: `Coda (Poco Adagio): 129-139 (11 measures)` (no "repeated")
- Fix: "The theme and each of the five variations are repeated. The coda is heard once."

### 3-5 · EN · Point 3 · MISLEADING
- "The violins now sound busier around it."
- Problem: the density figure is for the whole texture. Nothing in the facts says the extra notes are in the violins.
- Evidence: `Var. 1 ... note density vs theme: 1.52x` (no per-part data)
- Fix: "Overall there are about one and a half times as many notes as in the theme."

### 3-6 · EN + ZH · Points 6/9 (EN), 5/8 (ZH) · MISLEADING (internal tension)
- EN P6 headline: "Variation 3: the busiest" vs EN P9: "The loudest and busiest point is at [m. 84]." ZH P5: "这一段音符最密" vs ZH P8: "[m. 84] 是全乐章最响、最忙的地方。"
- Problem: the two claims use different measures (average density per variation vs a single-bar heuristic), and the listener is told twice that something is "the busiest".
- Evidence: `Var. 3 ... note density vs theme: 2.55x` (highest); `LOUDEST/BUSIEST POINT (heuristic): measure 84 (f, Var. 5)`
- Fix EN P9: "The analysis marks [m. 84] as the loudest point." Fix ZH P8: "按分析,[m. 84] 是全乐章最响的地方。" (Keep "most notes" for Var. 3.)

### 3-7 · EN · Point 9 and Glossary · MISLEADING
- P9: "starting with all parts in unison or octaves [m. 80]". Glossary: "Unison/octaves: All instruments play the same notes".
- Problem: the label does not say that all four instruments take part. The ZH text correctly says "几件乐器".
- Evidence: `80-80 unison/octaves`
- Fix P9: "starting with the instruments playing one line together in octaves [m. 80]". Glossary: "Two or more instruments play the same notes, or the same notes at different heights."

### 3-8 · EN · Point 12 · MISLEADING
- "Violin 1 then takes up a similar phrase [m. 111-115]."
- Problem: no theme return or similarity is listed for m. 111-115. Only the lead is known.
- Evidence: theme returns list only `Cello 107-110`; `111-115 Vn1 (conf 0.58)`
- Fix: "Violin 1 then takes the lead [m. 111-115]."

### 3-9 · EN · Point 13 · STYLE
- "Crescendos and accents push the music upward [m. 124-127]."
- Problem: "upward" sounds like rising pitch, which is not in the facts.
- Fix: "Crescendos and accents build the tension [m. 124-127]."

### 3-10 · ZH · Overview · MISLEADING
- "请留意……音符如何变得更密。"
- Problem: density does not rise steadily. Var. 4 and the coda drop back below the theme's level.
- Evidence: densities `1.0x, 1.52x, 1.6x, 2.55x, 0.95x, 1.91x, 0.87x`
- Fix: "请留意每段变奏音符的疏密变化:第三变奏最密,第四变奏又回到和主题差不多。"

### 3-11 · ZH · Overview, Glossary "主题", Point 13 headline · STYLE
- "全曲以D大调为主" / "全曲最先出现" / "轻柔的和弦收束全曲"
- Problem: these refer to one movement, not the whole quartet.
- Fix: replace "全曲" with "本乐章".

### 3-12 · ZH · Point 1 · STYLE
- "力度很弱(p)"
- Problem: p is 弱. "很弱" means pp (and the glossary itself says "p是轻").
- Fix: "力度弱(p)"

### 3-13 · ZH · Point 5 · MISLEADING
- Headline: "第三变奏:音符最密,声部互相追逐"
- Problem: "互相追逐" suggests imitation (canon). The facts only show the lead moving between parts.
- Evidence: `48-49 Va; 50-53 Vn2; 54-55 Vn1; 56 Vn2; 57 Va; 58-80 Vn1`
- Fix: "第三变奏:音符最密,旋律在声部间轮流出现"

### 3-14 · ZH · Point 6 · STYLE
- "这是全乐章里少见的小调。"
- Problem: F# minor is the only minor key in the key plan, so "少见" understates it.
- Evidence: KEY PLAN: only `F# minor: 69-72` is minor.
- Fix: "这是全乐章唯一的小调段落。"

### 3-15 · ZH · Point 7 · MISLEADING
- Headline: "回到D大调,渐弱到极轻"
- Problem: no diminuendo is marked. The passage has a crescendo at m. 77, then a new pp at m. 79. The body text is right, but the headline contradicts it.
- Evidence: `77|...|<cresc>`, `79|...|pp|pp`
- Fix: "回到D大调,渐强之后转为极弱"

### 3-16 · ZH · Point 9 · STYLE
- "大提琴先出声 [m. 97]"
- Problem: "先出声" means "sounds first". In fact m. 97 is a cello solo, and the cello already leads at 96b.
- Fix: "[m. 97] 只有大提琴独奏。"

### 3-17 · ZH · Point 11 · MISLEADING
- Headline: "逐步积累,走向高潮前的渐强"
- Problem: this implies m. 128 is the climax, but the facts' peak is m. 84. EN says only "a loud arrival".
- Evidence: `LOUDEST/BUSIEST POINT (heuristic): measure 84`
- Fix: "逐步积累,在第 128 小节变强"

### 3-18 · ZH · Point 11 · STYLE
- "然后第二小提琴出现 [m. 116-118]"
- Problem: the second violin has been playing all along. Here it takes the lead.
- Fix: "然后由第二小提琴接过旋律 [m. 116-118]"

### 3-19 · ZH · Point 12 · MISLEADING
- "声部以合奏式的和弦为主,第一小提琴单独唱出几句 [m. 130-131]。"
- Problem: only m. 129 is chordal. The rest of 130-134 is solo, then duet, then trio. "合奏式" is also not a standard term.
- Evidence: `127-129 homophonic; 130-131 solo; 132-133 duet; 134-134 trio`
- Fix: "[m. 129] 各声部以和弦一起进行,随后第一小提琴独奏 [m. 130-131],再变成二重、三重的薄织体 [m. 132-134]。"

**Summary op18no5_3.** The variation structure, keys (A major touches, F# minor, the Bb major turn at 96b) and the cello's two-octaves-lower return of the theme are all correct. The flagged ZH P8 variation name is correct, so that flag is a false positive. Both languages get Point 1 wrong: "alone m. 0-3" (ERROR), "begins high" (it leaps up first) and "mostly accompany" (mostly independent lines). The two "busiest" claims (Var. 3 and m. 84) confuse the listener. ZH has several headline-vs-facts slips: "渐弱" where no diminuendo is marked, "高潮" at m. 128, "互相追逐", and "以和弦为主" in the coda. It also repeatedly uses "全曲" for the movement.

---

## op18no5_4 (IV. Allegro)

### 4-1 · EN · Point 7 · ERROR
- "Then the whole quartet plays loudly [m. 95-98]."
- Problem: m. 95 is a trio, so only three instruments play, and the following bars are independent lines or melody + accompaniment. "Whole quartet" is invented.
- Evidence: `95|Part 2|F# minor|Vn1|0.3|trio|f|f||i64 i`; `96 independent lines; 97-98 melody + accompaniment`
- Fix: "Then the music stays loud [m. 95-98], first with three parts and then with the tune over accompaniment."

### 4-2 · EN · Points 1 and 13 · MISLEADING
- P1: "The viola starts alone with one quiet note [m. 0]." P13: "A viola note introduces it, as before."
- Problem: the facts say viola solo, but they do not say how many notes it plays. "One note" is invented.
- Evidence: `0|Part 1|A major|Va|1.0|solo|p|p||V`; `167|...|Va|1.0|solo|p|p||`
- Fix P1: "The viola starts alone, quietly [m. 0]." P13: "A short viola solo introduces it, as before [m. 167]."

### 4-3 · EN · Points 4 and 14 · MISLEADING
- P4 headline: "Sudden loud, then sudden whisper". P4: "A crescendo ... leads to a loud chord at [m. 34]." P14: "A crescendo leads to a loud chord at [m. 205]."
- Problem: m. 34 and m. 205 are loud bars with several chords and tune + accompaniment, not single chords. The loud arrival also comes after a crescendo, so "Sudden loud" contradicts the text.
- Evidence: `34|...|melody + accompaniment|f|f||V i V i`; `205|...|melody + accompaniment|f|f||V i V i`; `32|...|<cresc>`; `203|...|<cresc>`
- Fix P4 headline: "Loud, then a sudden whisper". P4 text: "A crescendo leads to two loud bars [m. 34-35]." P14: "A crescendo leads to two loud bars [m. 205-206]."

### 4-4 · ZH · Point 4 · MISLEADING
- "在 [m. 34] 声音忽然变成强(f)。"
- Problem: a crescendo starts at m. 32, so the forte is not sudden. Only the drop to pp is sudden.
- Evidence: `32|...|<cresc>`, `34|...|f|f`
- Fix: "经过第 32 小节开始的渐强,[m. 34] 达到强(f)。"

### 4-5 · EN · Point 6 · MISLEADING
- "Violin 1 repeats a pattern in short steps [m. 71-78]."
- Problem: the repetition is supported by the chords, but "in short steps" (melodic motion) is not in the facts.
- Evidence: chords `71-74: I, #viio65/ii, ii6, V7(+9) V7` = `75-78` (same); no contour data.
- Fix: "Violin 1 plays a four-bar pattern twice [m. 71-78]."

### 4-6 · EN · Point 16 · MISLEADING
- Headline: "A playful rush to the final chord"
- Problem: "rush" suggests the music speeds up, but the facts have no tempo change. The end also has soft stretches and a soft last chord.
- Evidence: no tempo marking beyond `Allegro`; `285-296 p`, `299 p`
- Fix: "Loud accents, a soft stretch, and a quiet final chord"

### 4-7 · ZH · Overview · MISLEADING
- "它会在不同调上多次回来。"
- Problem: of the three returns, only one is in another key (D major). The other two are in A major, the opening key.
- Evidence: `Violin 1 103-104 ... key D major`; `168-170 ... A major`; `264-266 ... A major`
- Fix: "它会多次回来:一次在 D 大调,两次回到原来的 A 大调。"

### 4-8 · ZH · Point 9 · MISLEADING
- Headline: "一路加强,在m. 128达到最响"
- Problem: there is no crescendo marking from m. 114 to m. 131. The music is ff all the way through. The "m. 128" format also does not match the rest of the ZH text.
- Evidence: `114-131 dynamic in force ff`; no `<cresc>` in 114-131.
- Fix: "持续极强(ff),第 128 小节最密集"

### 4-9 · ZH · Point 9 · MISLEADING (minor)
- "最响最忙的地方在 [m. 128],四件乐器各唱各的线条,有很多重音。"
- Problem: the label is independent lines, which does not show that all four parts are independent. The lead is a 0.0-confidence Vn1+Vn2 pair. "最响" is a heuristic, since the whole span is ff.
- Evidence: `128|Part 2|C major|Vn1+Vn2|0.0|independent lines|ff|sf||...`
- Fix: "按分析,[m. 128] 是最密集的一处:各声部各走各的线条,并带有重音(sf)。"

### 4-10 · EN · Point 11 · STYLE
- Headline: "Sudden calm, then almost silence"
- Problem: pp is very soft, not near-silence.
- Fix: "Sudden calm, then very soft"

### 4-11 · EN · Point 5 · STYLE
- Headline: "Sharp accents, then a loud drop to hush"
- Problem: "loud drop" is self-contradictory.
- Fix: "Sharp accents, a loud burst, then a hush"

### 4-12 · ZH · Overview · STYLE
- "全曲分两大部分。"
- Problem: this refers to the movement.
- Fix: "本乐章分两大部分。"

### 4-13 · ZH · Points 3, 8, 14 · STYLE
- "这里仍然很轻" (p), "而且声音很响" (f), "这次声音很响(f)"
- Problem: "很轻" and "很响" suggest pp and ff. The glossary itself gives p = 弱 and f = 强.
- Fix: "这里仍然是弱(p)" / "而且是强(f)" / "这次是强(f)"

**Summary op18no5_4.** The key plan, the two-part form, the three returns of the theme (D major +5 semitones, then A major twice), the ff passage with its heuristic peak at m. 128, and the ending (cello f, then a soft last chord) are reported correctly. The only ERROR is EN P7's "whole quartet" over a trio bar. Several EN details are invented (the viola's "one note", "loud chord", "short steps", "rush"). In ZH, the overview overstates key changes in the theme returns, and m. 34 and the m. 114-131 headline describe dynamics the facts do not show ("忽然", "一路加强"). ZH translations are otherwise natural. The main remaining issues are "全曲" for the movement and "很轻/很响" for p/f.

---

### Counts
| Piece | ERROR | MISLEADING | STYLE | Total |
|---|---|---|---|---|
| op18no5_1 | 2 | 11 | 7 | 20 |
| op18no5_2 | 2 | 10 | 6 | 18 |
| op18no5_3 | 1 | 12 | 6 | 19 |
| op18no5_4 | 1 | 8 | 4 | 13 |
