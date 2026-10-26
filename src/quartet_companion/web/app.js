/* Quartet Companion web player.
 * Reads pieces/index.json and pieces/<id>/data.json (built by `qc site`).
 * Everything shown comes from the fact sheet or the verified guide.
 */
(function () {
  "use strict";

  const T = {
    en: {
      doubts_title: "Bars to compare by ear ({n}) — marked with a dotted frame",
      doubts_body: "The program read this score from a scan. In these bars the notes it read fit the sound clearly worse than in the bars around them, so the scan may have been misread there (or the players do something special). This is a hint, not a verdict. Click a bar number to hear it.",
      doubt_length: "notes don't fill the bar",
      library: "Library", lib_search: "Search: composer, title, nickname, key…", lib_all_composers: "All composers",
      lib_any_mode: "Major and minor", major: "major", minor: "minor", lib_any_len: "Any length",
      len_short: "Under 5 min", len_mid: "5–10 min", len_long: "Over 10 min", lib_any_ens: "All ensembles",
      ens_quartet: "String quartet", ens_trio: "Trio", ens_quintet: "Quintet", ens_other: "Other",
      lib_guide: "Has a guide in this language", lib_count: "{m} movements in {w} works",
      lib_none: "Nothing matches. Try fewer words or clear a filter.", lib_no_audio: "no recording",
      lib_mvts: "movements",
      tagline: "Listen with the score's eyes", measure: "Measure", section: "Section", key: "Key",
      dynamic: "Dynamic", texture: "Texture", sections: "Sections", keys: "Keys",
      leg_lead: "has the tune", leg_active: "playing", leg_theme: "opening theme returns",
      leg_flag: "uncertain timing", leg_click: "Click anywhere on the timeline to jump there.",
      uncertain_title: "ⓘ A few spots where the timing may be slightly off (nothing to do)",
      uncertain_body: "The program is less sure about these measures. The highlight may run a little early or late there. You do not need to check anything; if something looks clearly wrong, just tell Claude which piece and roughly where.",
      autonext: "Play the next movement automatically", score: "Score", follow: "Follow the music",
      score_hint: "The highlighted bar is playing now. Click any bar to jump there.", page: "page",
      printed_note: "This is the original printed score (scanned page).",
      recording: "Recording", compare: "Compare recordings",
      compare_hint: "Each line is how fast one recording plays each bar (higher = faster). Click the chart to jump there; switch recordings above to hear the same bar in another performance.",
      cmp_total: "Length", cmp_faster: "{sec}: {a} is {p}% faster than {b}", cmp_slower: "{sec}: {a} is {p}% slower than {b}",
      cmp_repeats: "Repeats: {a} – {x}; {b} – {y}", cmp_bpm: "beats/min", cmp_bar: "bar",
      cmp_overall: "Overall", cmp_vs_overall: "(differs most from the overall difference)",
      practice: "Practice", speed: "Speed", loop_pick: "Choose bars to loop", loop_clear: "Stop looping",
      countin: "Count-in before each start", pick_first: "Click the first bar in the score…",
      pick_last: "…now click the last bar", looping: "Looping bars {a}–{b}",
      drawn_note: "This score is redrawn from the notes the program read.",
      no_audio: "No recording is aligned with this piece yet.", guide: "Listening guide", glossary: "Words used",
      no_guide: "No guide yet in this language. Run: qc guide <piece> --lang en zh",
      at_a_glance: "At a glance", variations: "Variations", method: "How this was made",
      credits_link: "Credits and licences",
      footer: "Facts come from the score analysis. The guide is written by Claude and every claim is checked against those facts.",
      verified: (v, u) => `${v} claims checked ✓` + (u ? ` · ${u} unchecked` : ""),
      home_key: "Home key", meter: "Time signature", length: "Length", measures: "measures",
      tempo: "Tempo marking", harmony: "Harmony", expert: "expert analysis (DCML ABC)", auto: "estimated by the program",
      opening_theme: "Opening theme", returns: "returns", tune_in: "tune heard mostly in",
      same_harmony: "same chords as the theme", busier: "notes vs theme", m: "m.", performed: "Recording plays",
      score_quality: "Score quality (OMR)",
      textures: {"melody + accompaniment": "melody + accompaniment", "homophonic": "chordal (all move together)",
                 "independent lines": "independent lines", "duet": "duet", "trio": "trio", "solo": "solo",
                 "unison/octaves": "unison / octaves", "tacet": "silence", "held": "held notes"},
    },
    zh: {
      doubts_title: "建议对照着听的小节（{n} 处，乐谱上用虚线框标出）",
      doubts_body: "这份乐谱是程序从扫描页识别出来的。在这些小节里，程序读到的音符和录音的声音明显比前后小节对得差，可能是识别错了（也可能是演奏者的特殊处理）。这只是提示，不是结论。点小节号可以跳过去听。",
      doubt_length: "音符时值不满一小节",
      library: "曲库", lib_search: "搜索：作曲家、曲名、别名、调性……", lib_all_composers: "全部作曲家",
      lib_any_mode: "大调和小调", major: "大调", minor: "小调", lib_any_len: "任意时长",
      len_short: "5 分钟以内", len_mid: "5–10 分钟", len_long: "10 分钟以上", lib_any_ens: "全部编制",
      ens_quartet: "弦乐四重奏", ens_trio: "三重奏", ens_quintet: "五重奏", ens_other: "其他",
      lib_guide: "有当前语言的导读", lib_count: "共 {w} 部作品，{m} 个乐章",
      lib_none: "没有符合的曲目。试试少输几个字，或取消一个筛选。", lib_no_audio: "无录音",
      lib_mvts: "个乐章",
      tagline: "用乐谱的眼睛去听", measure: "小节", section: "段落", key: "调性", dynamic: "力度", texture: "织体",
      sections: "段落", keys: "调性", leg_lead: "主旋律", leg_active: "在演奏", leg_theme: "开头主题再现",
      leg_flag: "时间不确定", leg_click: "点击时间轴任意位置即可跳转。",
      uncertain_title: "ⓘ 有几处时间可能略有偏差（无需处理）",
      uncertain_body: "程序对这些小节的时间把握不大，高亮可能会稍早或稍晚一点。你不需要做任何检查。如果看到明显不对的地方，告诉 Claude 是哪首曲子、大概在哪里就行。",
      autonext: "自动接着播放下一乐章", score: "乐谱", follow: "跟随音乐翻页",
      score_hint: "高亮的小节就是正在演奏的地方。点任意一个小节即可跳转到那里。", page: "页",
      printed_note: "这是原版印刷乐谱（扫描页）。",
      recording: "录音", compare: "录音比较",
      compare_hint: "每条线表示一个录音在每个小节演奏得多快（越高越快）。点图表可以跳到那里；在上面切换录音，就能听另一个版本的同一小节。",
      cmp_total: "时长", cmp_faster: "{sec}：{a} 比 {b} 快 {p}%", cmp_slower: "{sec}：{a} 比 {b} 慢 {p}%",
      cmp_repeats: "反复：{a} —— {x}；{b} —— {y}", cmp_bpm: "拍/分钟", cmp_bar: "小节",
      cmp_overall: "整体", cmp_vs_overall: "（和整体差别相比，这里最不一样）",
      practice: "练习", speed: "速度", loop_pick: "选择循环段", loop_clear: "停止循环",
      countin: "每次开始前给预备拍", pick_first: "在乐谱上点第一个小节……",
      pick_last: "……再点最后一个小节", looping: "正在循环：第 {a}–{b} 小节",
      drawn_note: "这份乐谱是根据程序读到的音符重新绘制的。",
      no_audio: "这首曲子还没有对齐的录音。", guide: "听赏指南", glossary: "术语解释",
      no_guide: "这个语言还没有指南。运行：qc guide <piece> --lang en zh",
      at_a_glance: "概览", variations: "变奏", method: "这些信息怎么来的",
      credits_link: "来源与授权",
      footer: "事实来自乐谱分析。指南由 Claude 撰写，每一条说法都已对照这些事实检查过。",
      verified: (v, u) => `${v} 条说法已核对 ✓` + (u ? ` · ${u} 条未核对` : ""),
      home_key: "主调", meter: "拍号", length: "长度", measures: "小节", tempo: "速度标记", harmony: "和声",
      expert: "专家标注（DCML ABC）", auto: "程序自动估计", opening_theme: "开头主题", returns: "再现",
      tune_in: "主题主要在", same_harmony: "与主题和声相同", busier: "音符密度（相对主题）", m: "第", performed: "录音演奏方式",
      score_quality: "乐谱质量（光学识别）",
      textures: {"melody + accompaniment": "旋律＋伴奏", "homophonic": "和弦式（齐动）", "independent lines": "各声部独立",
                 "duet": "二重奏", "trio": "三重奏", "solo": "独奏", "unison/octaves": "齐奏 / 八度", "tacet": "休止", "held": "延续音"},
    },
  };
  const PART_COLORS = ["--vn1", "--vn2", "--va", "--vc", "--extra", "--extra"];
  const PART_ZH = {"Violin 1": "第一小提琴", "Violin 2": "第二小提琴", "Viola": "中提琴", "Cello": "大提琴",
                   "Violin": "小提琴", "Double bass": "低音提琴"};

  let lang = (navigator.language || "en").toLowerCase().startsWith("zh") ? "zh" : "en";
  try { lang = localStorage.getItem("qc-lang") || lang; } catch (e) { /* storage may be blocked */ }
  let data = null, played = [], total = 0, t0 = 0, byMc = {}, labelOcc = {}, index = [], autoplayNext = false;
  const $ = (id) => document.getElementById(id);
  const audio = $("audio");
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const t = (k) => (T[lang][k] !== undefined ? T[lang][k] : T.en[k]);
  const partName = (p) => (lang === "zh" && PART_ZH[p]) ? PART_ZH[p] : p;
  const fmt = (s) => { s = Math.max(0, s || 0); const m = Math.floor(s / 60); return `${m}:${String(Math.floor(s % 60)).padStart(2, "0")}`; };
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));

  // ------------------------------------------------------------ loading
  async function init() {
    document.querySelectorAll(".lang button").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.lang)));
    $("play").addEventListener("click", () => {
      if (!audio.paused || counting) { stopCount(); audio.pause(); return; }
      if (loop && (audio.currentTime < loop.s - 0.05 || audio.currentTime >= loop.e - 0.05)) { startLoop(); return; }
      if (loop && $("countin").checked) { startLoop(audio.currentTime); return; }
      audio.play();
    });
    initPractice();
    $("rec-select").addEventListener("change", (e) => switchRecording(+e.target.value));
    $("compare-chart").addEventListener("click", (e) => {
      const i = compareIndexAt(e);
      if (i < 0) return;
      const keys = occKeys(played);
      let j = keys.indexOf(cmp.baseKeys[i]);
      if (j < 0) j = played.findIndex((p) => `${p.mc}` === cmp.baseKeys[i].split("#")[0]);
      if (j >= 0) seekTo(played[j].start_sec);
    });
    $("compare-chart").addEventListener("mousemove", (e) => {
      const i = compareIndexAt(e), tip = $("compare-tip");
      if (i < 0 || !cmp) { tip.hidden = true; return; }
      const recs = data.recordings, bm = recs[0].measures[i];
      tip.innerHTML = `<b>${esc(t("measure"))} ${esc(bm.label)}</b><br>` + recs.map((r, k) =>
        `${esc(r.name)}: ${cmp.series[k][i] ? Math.round(cmp.series[k][i]) : "–"}`).join("<br>");
      const card = $("compare-card").getBoundingClientRect();
      tip.style.left = `${Math.min(e.clientX - card.left + 12, card.width - 180)}px`;
      tip.style.top = `${e.clientY - card.top + 12}px`;
      tip.hidden = false;
    });
    $("compare-chart").addEventListener("mouseleave", () => { $("compare-tip").hidden = true; });
    audio.addEventListener("play", () => $("play-icon").setAttribute("d", "M7 5h4v14H7zM13 5h4v14h-4z"));
    audio.addEventListener("pause", () => $("play-icon").setAttribute("d", "M8 5v14l11-7z"));
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", () => { $("dur").textContent = fmt(total - t0); });
    $("timeline").addEventListener("click", onTimelineClick);
    $("prev-page").addEventListener("click", () => { $("follow").checked = false; showPage(scorePage - 1); });
    $("next-page").addEventListener("click", () => { $("follow").checked = false; showPage(scorePage + 1); });
    $("score").addEventListener("click", (e) => {
      if (!data.score) return;
      let mc;
      if (data.score.kind === "image") {         // which measure box was clicked?
        const page = e.target.closest(".qc-page");
        if (!page) return;
        const r = page.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        const hit = Object.entries(data.score.measures).find(([, v]) =>
          v.boxes.some((b) => b.page === scorePage && x >= b.x0 && x <= b.x1 && y >= b.y0 && y <= b.y1));
        mc = hit ? +hit[0] : undefined;
      } else {
        const g = e.target.closest("g.measure");
        if (!g) return;
        mc = idToMc()[g.getAttribute("data-id") || g.id];
      }
      if (mc === undefined) return;
      if (picking) { pickBar(mc); return; }
      $("follow").checked = true;
      const occ = played.findIndex((p) => p.mc === mc);
      if (occ >= 0) seekTo(played[occ].start_sec);
    });
    document.addEventListener("keydown", (e) => {
      if (e.code === "Space" && e.target === document.body) { e.preventDefault(); $("play").click(); }
    });
    try { index = await (await fetch("pieces/index.json")).json(); } catch (e) { /* none yet */ }
    const sel = $("piece-select");
    // group the movements of one work together
    const works = [];
    index.forEach((p) => { const w = works.find((x) => x.work === p.work); if (w) w.items.push(p); else works.push({work: p.work, items: [p]}); });
    sel.innerHTML = works.map((w) => w.items.length > 1
      ? `<optgroup label="${esc(w.items[0].title.split(" – ")[0])}">${w.items.map((p) => `<option value="${esc(p.id)}">${esc(p.title.split(" – ").slice(1).join(" – ") || p.title)}</option>`).join("")}</optgroup>`
      : `<option value="${esc(w.items[0].id)}">${esc(w.items[0].title)}</option>`).join("");
    audio.addEventListener("ended", playNextMovement);
    sel.addEventListener("change", () => { location.hash = sel.value; load(sel.value); });
    initLibrary();
    $("doubts-list").addEventListener("click", (e) => {
      const b = e.target.closest(".doubt-chip");
      if (!b) return;
      const occ = played.findIndex((p) => p.mc === +b.dataset.mc);
      $("follow").checked = true;
      if (occ >= 0) seekTo(played[occ].start_sec);
      else highlightMeasure(+b.dataset.mc);
    });
    const start = decodeURIComponent(location.hash.slice(1)) || (index[0] && index[0].id);
    if (start) { sel.value = start; load(start); } else { $("title").textContent = "No pieces built yet — run `qc site`."; }
    setLang(lang, true);
  }

  function nextMovementId() {
    const i = index.findIndex((p) => p.id === data.id);
    const next = index[i + 1];
    return next && next.work === index[i].work && next.has_audio ? next.id : null;
  }

  async function playNextMovement() {
    const next = nextMovementId();
    if (!next || !$("autonext").checked) return;
    $("piece-select").value = next;
    location.hash = next;
    autoplayNext = true;
    await load(next);
  }

  async function load(id) {
    audio.pause();
    stopCount();
    clearLoop(true);
    data = await (await fetch(`pieces/${encodeURIComponent(id)}/data.json`)).json();
    byMc = {};
    data.measures.forEach((m) => { byMc[m.mc] = m; });
    const al = data.alignment;
    const recs = data.recordings || [];
    $("rec-wrap").hidden = recs.length < 2;
    $("rec-select").innerHTML = recs.map((r, k) => `<option value="${k}">${esc(r.name)}</option>`).join("");
    if (al && al.audio) {
      useAlignment(al);
      audio.addEventListener("loadedmetadata", () => {
        audio.currentTime = played.length ? played[0].start_sec : 0;   // start at measure 1 of this movement
        if (autoplayNext) { autoplayNext = false; audio.play().catch(() => {}); }
      }, {once: true});
      $("no-audio").hidden = true; $("play").disabled = false; $("practice").hidden = false;
    } else {
      // no recording: draw the timeline in score order, one unit per measure
      let x = 0;
      played = data.measures.map((m, i) => ({occurrence: i, mc: m.mc, label: m.label, start_sec: x, end_sec: (x += 1), f: m}));
      audio.removeAttribute("src"); $("no-audio").hidden = false; $("play").disabled = true; $("practice").hidden = true;
    }
    total = played.length ? played[played.length - 1].end_sec : 1;
    t0 = played.length ? played[0].start_sec : 0;
    const nxt = nextMovementId();
    $("autonext-wrap").hidden = !nxt;
    labelOcc = {};
    played.forEach((p, i) => { (labelOcc[p.label] = labelOcc[p.label] || []).push(i); });
    scorePage = 0; scoreNowId = null;
    $("score-card").hidden = !data.score;
    $("score-source").hidden = !data.score;
    if (data.score) $("score-source").textContent = t(data.score.kind === "image" ? "printed_note" : "drawn_note");
    if (data.score) showPage(1);
    render();
  }

  function useAlignment(al) {
    // make one recording the one that plays (its clip and its measure times)
    data.alignment = al;
    played = al.measures.map((m) => ({...m, f: byMc[m.mc]}));
    audio.src = `pieces/${encodeURIComponent(data.id)}/${al.audio}`;
    total = played.length ? played[played.length - 1].end_sec : 1;
    t0 = played.length ? played[0].start_sec : 0;
    labelOcc = {};
    played.forEach((p, i) => { (labelOcc[p.label] = labelOcc[p.label] || []).push(i); });
  }

  // key of a played bar that is the same in every recording: bar id + which time it is played
  function occKeys(list) {
    const seen = {};
    return list.map((p) => { seen[p.mc] = (seen[p.mc] || 0) + 1; return `${p.mc}#${seen[p.mc]}`; });
  }

  function switchRecording(k) {
    const recs = data.recordings || [];
    if (!recs[k] || recs[k] === data.alignment) return;
    const wasPlaying = !audio.paused;
    const i = currentIndex(audio.currentTime || 0);
    const p = played[i];
    const frac = p ? Math.max(0, Math.min(1, (audio.currentTime - p.start_sec) / Math.max(0.01, p.end_sec - p.start_sec))) : 0;
    const key = occKeys(played)[i];
    const oldKeys = occKeys(played);
    const loopKeys = loop ? [oldKeys[loop.ia], oldKeys[loop.ib]] : null;
    audio.pause(); stopCount();
    const rate = audio.playbackRate;
    useAlignment(recs[k]);
    const keys = occKeys(played);
    let j = keys.indexOf(key);
    if (j < 0) j = played.findIndex((q) => p && q.mc === p.mc);
    if (loopKeys) {
      const ia = keys.indexOf(loopKeys[0]), ib = keys.indexOf(loopKeys[1]);
      if (ia >= 0 && ib >= ia) loop = {...loop, ia, ib, s: played[ia].start_sec, e: played[ib].end_sec};
      else clearLoop(true);
    }
    audio.addEventListener("loadedmetadata", () => {
      audio.playbackRate = rate;
      const q = played[Math.max(0, j)];
      audio.currentTime = q ? q.start_sec + frac * (q.end_sec - q.start_sec) : t0;
      onTime();
      if (wasPlaying) audio.play().catch(() => {});
    }, {once: true});
    $("dur").textContent = fmt(total - t0);
    render();
  }

  // ------------------------------------------------------------ compare recordings
  const REC_COLORS = ["--accent", "--va", "--vn2", "--vc"];
  let cmp = null;

  function smooth(vals, k) {
    return vals.map((_, i) => {
      const w = vals.slice(Math.max(0, i - k), i + k + 1).filter((v) => v != null && isFinite(v));
      if (!w.length) return null;
      const s = [...w].sort((x, y) => x - y);
      return s[Math.floor(s.length / 2)];
    });
  }

  function drawCompare() {
    const recs = data.recordings || [];
    $("compare-card").hidden = recs.length < 2;
    cmp = null;
    if (recs.length < 2) return;
    const base = recs[0].measures;
    const baseKeys = occKeys(base);
    const series = recs.map((r) => {
      const keys = occKeys(r.measures), at = {};
      keys.forEach((kk, i) => { at[kk] = r.measures[i]; });
      const raw = baseKeys.map((kk) => {
        const m = at[kk];
        return m && m.tempo_qpm > 0 && m.end_sec - m.start_sec > 0.05 ? m.tempo_qpm : null;
      });
      return smooth(raw, 2);
    });
    const all = series.flat().filter((v) => v != null).sort((x, y) => x - y);
    if (!all.length) return;
    let lo = all[Math.floor(all.length * 0.03)], hi = all[Math.floor(all.length * 0.97)];
    const pad = (hi - lo) * 0.15 + 2; lo = Math.max(0, lo - pad); hi += pad;
    const W = 1000, H = 260, L = 44, R = 8, Tp = 22, B = 24;
    const n = base.length;
    const X = (i) => L + (W - L - R) * (n > 1 ? i / (n - 1) : 0);
    const Y = (v) => Tp + (H - Tp - B) * (1 - (v - lo) / (hi - lo));
    let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(t("compare"))}">`;
    // tempo grid
    const step = Math.max(5, Math.round((hi - lo) / 4 / 5) * 5);
    for (let v = Math.ceil(lo / step) * step; v <= hi; v += step) {
      svg += `<line class="grid" x1="${L}" x2="${W - R}" y1="${Y(v)}" y2="${Y(v)}"/><text class="axis" x="${L - 6}" y="${Y(v) + 4}" text-anchor="end">${v}</text>`;
    }
    // section boundaries (from the facts of the first recording's bars)
    let prev = null;
    base.forEach((m, i) => {
      const sec = (byMc[m.mc] || {}).section;
      if (sec && sec !== prev) {
        svg += `<line class="sec-line" x1="${X(i)}" x2="${X(i)}" y1="${Tp - 4}" y2="${H - B}"/>` +
               `<text class="sec-name" x="${X(i) + 3}" y="${Tp - 8}">${esc(sec.length > 18 ? sec.slice(0, 17) + "…" : sec)}</text>`;
        prev = sec;
      }
    });
    series.forEach((s, k) => {
      let d = "", pen = false;
      s.forEach((v, i) => { if (v == null) { pen = false; return; } d += `${pen ? "L" : "M"}${X(i).toFixed(1)},${Y(v).toFixed(1)}`; pen = true; });
      svg += `<path d="${d}" fill="none" stroke="${css(REC_COLORS[k % REC_COLORS.length])}" stroke-width="2.2" stroke-linejoin="round"/>`;
    });
    svg += `<text class="axis" x="${L}" y="${H - 6}">${esc(t("cmp_bar"))} ${esc(base[0].label)}</text>`;
    svg += `<text class="axis" x="${W - R}" y="${H - 6}" text-anchor="end">${esc(base[n - 1].label)}</text>`;
    svg += `<line class="now" id="cmp-now" x1="-10" x2="-10" y1="${Tp - 4}" y2="${H - B}"/></svg>`;
    $("compare-chart").innerHTML = svg;
    $("compare-legend").innerHTML = `<span class="muted">${esc(t("cmp_bpm"))}</span>` + recs.map((r, k) =>
      `<span><i style="background:${css(REC_COLORS[k % REC_COLORS.length])}"></i>${esc(r.name)}</span>`).join("");
    cmp = {X, n, baseKeys, series, W, L, R};
    // notes: length, repeats, biggest differences by section
    const dur = (r) => r.measures[r.measures.length - 1].end_sec - r.measures[0].start_sec;
    const notes = [`${t("cmp_total")}${lang === "zh" ? "：" : ": "}` + recs.map((r) => `${r.name} ${fmt(dur(r))}`).join(" · ")];
    if (recs[0].order !== recs[1].order) {
      notes.push(t("cmp_repeats").replace("{a}", recs[0].name).replace("{x}", recs[0].order_description)
        .replace("{b}", recs[1].name).replace("{y}", recs[1].order_description));
    }
    // Where do the two performances differ most, beyond one simply being faster overall?
    const bySec = {}, allr = [];
    base.forEach((m, i) => {
      const a = series[1][i], b = series[0][i], sec = (byMc[m.mc] || {}).section;
      if (a && b) allr.push(Math.log(a / b));
      if (a && b && sec) (bySec[sec] = bySec[sec] || []).push(Math.log(a / b));
    });
    const mean = (v) => v.reduce((x, y) => x + y, 0) / v.length;
    const pct = (r) => Math.round((Math.exp(Math.abs(r)) - 1) * 100);
    const say = (key, sec, r) => t(r > 0 ? "cmp_faster" : "cmp_slower").replace("{sec}", sec)
      .replace("{a}", recs[1].name).replace("{b}", recs[0].name).replace("{p}", pct(r));
    if (allr.length) {
      const r0 = mean(allr);
      if (Math.abs(r0) > 0.03) notes.push(say("", t("cmp_overall"), r0));
      Object.entries(bySec).filter(([, v]) => v.length >= 4)
        .map(([sec, v]) => [sec, mean(v)])
        .sort((x, y) => Math.abs(y[1] - r0) - Math.abs(x[1] - r0)).slice(0, 3)
        .filter(([, r]) => Math.abs(r - r0) > 0.035)
        .forEach(([sec, r]) => notes.push(`${say("", sec, r)} ${t("cmp_vs_overall")}`));
    }
    $("compare-notes").innerHTML = notes.map((x) => `<li>${esc(x)}</li>`).join("");
    updateCompareNow();
  }

  function compareIndexAt(e) {
    const svg = $("compare-chart").querySelector("svg");
    if (!svg || !cmp) return -1;
    const r = svg.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width * cmp.W;
    return Math.max(0, Math.min(cmp.n - 1, Math.round((x - cmp.L) / (cmp.W - cmp.L - cmp.R) * (cmp.n - 1))));
  }

  function updateCompareNow() {
    const line = document.getElementById("cmp-now");
    if (!line || !cmp || !played.length) return;
    const key = occKeys(played)[currentIndex(audio.currentTime || 0)];
    const i = cmp.baseKeys.indexOf(key);
    const x = i >= 0 ? cmp.X(i) : -10;
    line.setAttribute("x1", x); line.setAttribute("x2", x);
  }

  // ------------------------------------------------------------ score pages
  let scorePage = 0, scoreNowId = null;
  const idToMc = () => {
    const m = {};
    Object.entries(data.score.measures).forEach(([mc, v]) => { m[v.id] = +mc; });
    return m;
  };

  async function showPage(n) {
    if (!data.score || n < 1 || n > data.score.pages || n === scorePage) return;
    scorePage = n;
    const base = `pieces/${encodeURIComponent(data.id)}/score/`;
    if (data.score.kind === "image") {           // the printed page (scores read from a PDF)
      const [w, h] = data.score.page_sizes[n - 1];
      $("score").innerHTML = `<div class="qc-page" style="aspect-ratio:${w}/${h}">` +
        `<img src="${base}${data.score.page_files[n - 1]}" alt="${t("score")} ${n}"></div>`;
    } else {
      const svg = await (await fetch(`${base}page-${n}.svg`)).text();
      if (scorePage !== n) return;               // another page was requested meanwhile
      $("score").innerHTML = svg;
    }
    $("page-label").textContent = `${t("page")} ${n} / ${data.score.pages}`;
    scoreNowId = null;
    drawLoop();
    drawDoubts();
    onTime();
  }

  function highlightMeasure(mc) {
    if (!data.score) return;
    const m = data.score.measures[String(mc)];
    if (!m) return;
    if (m.page !== scorePage && $("follow").checked) { showPage(m.page); return; }
    if (scoreNowId === m.id) return;
    const root = $("score");
    if (data.score.kind === "image") {
      const page = root.querySelector(".qc-page");
      if (!page) return;
      page.querySelectorAll(".qc-hl").forEach((el) => el.remove());
      m.boxes.filter((b) => b.page === scorePage).forEach((b) => {
        const el = document.createElement("div");
        el.className = "qc-hl";
        Object.assign(el.style, {left: `${b.x0 * 100}%`, top: `${b.y0 * 100}%`,
          width: `${(b.x1 - b.x0) * 100}%`, height: `${(b.y1 - b.y0) * 100}%`});
        page.appendChild(el);
      });
      scoreNowId = m.id;
      return;
    }
    root.querySelectorAll(".qc-now").forEach((el) => el.classList.remove("qc-now"));
    root.querySelectorAll(".qc-box").forEach((el) => el.remove());
    const g = root.querySelector(`[data-id="${m.id}"]`) || root.querySelector(`#${CSS.escape(m.id)}`);
    if (!g) return;
    g.classList.add("qc-now");
    try {                                         // soft background box behind the bar
      const b = g.getBBox();
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("class", "qc-box");
      ["x", "y", "width", "height"].forEach((k, i) => rect.setAttribute(k, [b.x - 4, b.y - 4, b.width + 8, b.height + 8][i]));
      g.insertBefore(rect, g.firstChild);
    } catch (e) { /* not rendered yet */ }
    scoreNowId = m.id;
  }

  function setLang(l, quiet) {
    lang = l;
    try { localStorage.setItem("qc-lang", l); } catch (e) { /* ignore */ }
    document.documentElement.lang = l === "zh" ? "zh-CN" : "en";
    document.querySelectorAll(".lang button").forEach((b) => b.classList.toggle("on", b.dataset.lang === l));
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const v = t(el.dataset.i18n);
      if (typeof v === "string") el.textContent = v;
    });
    if (typeof updateLoopInfo === "function") updateLoopInfo();
    if (data && data.score && scorePage) $("page-label").textContent = `${t("page")} ${scorePage} / ${data.score.pages}`;
    if (data && data.score) $("score-source").textContent = t(data.score.kind === "image" ? "printed_note" : "drawn_note");
    if ($("library").open) { fillLibraryFilters(); renderLibrary(); }
    if (!quiet && data) render();
  }

  // ------------------------------------------------------------ rendering
  // the timeline spans this movement only: from its first to its last measure
  const span = () => Math.max(1e-6, total - t0);
  const xpct = (sec) => `${(100 * (sec - t0) / span()).toFixed(3)}%`;
  const wpct = (a, b) => `${(100 * Math.max(0, b - a) / span()).toFixed(3)}%`;
  const hue = (s) => { let h = 0; for (const c of s) h = (h * 31 + c.charCodeAt(0)) % 360; return h; };
  // Keys on the circle of fifths get well-separated hues; minor keys are darker.
  const FIFTHS = {"C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6, "C#": 7, "G#": 8, "D#": 9, "A#": 10,
                  "F": -1, "Bb": -2, "Eb": -3, "Ab": -4, "Db": -5, "Gb": -6, "Cb": -7, "Fb": -8, "E#": 11, "B#": 12};
  const keyColor = (k) => {
    const [tonic, mode] = k.split(" ");
    const f = FIFTHS[tonic];
    const h = f === undefined ? hue(k) : ((f * 137.5) % 360 + 360) % 360;
    return mode === "minor" ? `hsl(${h} 32% 36%)` : `hsl(${h} 45% 47%)`;
  };

  function runs(getter) {
    const out = [];
    played.forEach((p) => {
      const v = getter(p);
      const last = out[out.length - 1];
      if (last && last.v === v && Math.abs(last.end - p.start_sec) < 1e-6) last.end = p.end_sec;
      else out.push({v, start: p.start_sec, end: p.end_sec, first: p});
    });
    return out;
  }

  function render() {
    const pc = data.piece;
    $("title").textContent = pc.title;
    $("subtitle").textContent = [pc.composer, pc.tempo_marking, pc.home_key].filter(Boolean).join(" · ");
    // Uncertain spots are shown as a calm note, not as a task for the listener.
    const warns = (data.alignment && data.alignment.warnings) || [];
    $("warnings").innerHTML = warns.length
      ? `<details class="notice soft"><summary>${esc(t("uncertain_title"))}</summary>
           <p>${esc(t("uncertain_body"))}</p><ul>${warns.map((w) => `<li>${esc(w)}</li>`).join("")}</ul></details>`
      : "";
    renderDoubts();

    // sections and keys
    $("lane-sections").innerHTML = runs((p) => p.f.section).map((r, i) =>
      `<div class="seg section" style="left:${xpct(r.start)};width:${wpct(r.start, r.end)};background:hsl(${(i * 47) % 360} 30% 82% / .75)" title="${esc(r.v)}">${esc(r.v)}</div>`).join("");
    $("lane-keys").innerHTML = runs((p) => p.f.key).map((r) =>
      `<div class="seg key" style="left:${xpct(r.start)};width:${wpct(r.start, r.end)};background:${keyColor(r.v)}" title="${esc(r.v)}">${esc(r.v)}</div>`).join("");

    // part lanes
    const lanes = $("part-lanes");
    lanes.innerHTML = "";
    pc.parts.forEach((part, pi) => {
      const color = css(PART_COLORS[pi] || "--extra");
      const lab = document.createElement("div");
      lab.className = "row-label"; lab.dataset.part = part; lab.textContent = partName(part);
      const lane = document.createElement("div");
      lane.className = "lane part";
      let html = "";
      runs((p) => p.f.active_parts.includes(part)).forEach((r) => {
        if (r.v) html += `<div class="seg active" style="left:${xpct(r.start)};width:${wpct(r.start, r.end)};background:${color}"></div>`;
      });
      runs((p) => p.f.lead === part || p.f.co_lead === part).forEach((r) => {
        if (r.v) html += `<div class="seg lead" style="left:${xpct(r.start)};width:${wpct(r.start, r.end)};background:${color}"></div>`;
      });
      played.forEach((p) => {
        if (p.flagged && pi === pc.parts.length - 1) html += `<div class="seg flag" style="left:${xpct(p.start_sec)};width:${wpct(p.start_sec, p.end_sec)}"></div>`;
      });
      (data.theme_occurrences || []).filter((o) => o.part === part && o.kind !== "original").forEach((o) => {
        (labelOcc[o.start_label] || []).forEach((i) => { html += `<span class="star" style="left:${xpct(played[i].start_sec)}" title="${esc(o.theme)}">★</span>`; });
      });
      lane.innerHTML = html;
      lanes.appendChild(lab); lanes.appendChild(lane);
    });
    renderGuide(); renderFacts(); onTime();
  }

  function mrefs(text) {
    return esc(text).replace(/\[m\.?\s*([0-9]+[a-h]?)(?:\s*[-–]\s*([0-9]+[a-h]?))?\]/g, (all, a, b) =>
      `<span class="mref" data-label="${a}">${lang === "zh" ? `第 ${a}${b ? "–" + b : ""} 小节` : `m. ${a}${b ? "–" + b : ""}`}</span>`);
  }

  function renderGuide() {
    const g = data.guides[lang];
    const v = data.verification[lang];
    $("no-guide").hidden = !!g;
    $("overview").innerHTML = g ? mrefs(g.overview) : "";
    $("verified").textContent = v ? t("verified")(v.verified, v.unchecked) : "";
    $("verified").hidden = !v;
    const ol = $("points");
    ol.innerHTML = "";
    if (!g) { $("glossary-box").hidden = true; return; }
    g.listening_points.forEach((p, i) => {
      const li = document.createElement("li");
      li.className = "point"; li.dataset.start = p.start_measure; li.dataset.end = p.end_measure; li.dataset.i = i;
      const pi = data.piece.parts.indexOf(p.focus_part);
      const pill = pi >= 0 ? `<span class="pill" style="background:${css(PART_COLORS[pi])}">${esc(partName(p.focus_part))}</span>` : "";
      li.innerHTML = `<div class="meta"><span>${lang === "zh" ? `第 ${esc(p.start_measure)}–${esc(p.end_measure)} 小节` : `m. ${esc(p.start_measure)}–${esc(p.end_measure)}`}</span>${pill}</div>
        <div class="head">${esc(p.headline)}</div><p class="txt">${mrefs(p.text)}</p>`;
      li.addEventListener("click", (e) => {
        const ref = e.target.closest(".mref");
        seekLabel(ref ? ref.dataset.label : p.start_measure);
      });
      ol.appendChild(li);
    });
    $("overview").querySelectorAll(".mref").forEach((el) => el.addEventListener("click", () => seekLabel(el.dataset.label)));
    $("glossary-box").hidden = !(g.glossary && g.glossary.length);
    $("glossary").innerHTML = (g.glossary || []).map((x) => `<dt>${esc(x.term)}</dt><dd>${esc(x.explanation)}</dd>`).join("");
  }

  function renderFacts() {
    const pc = data.piece;
    const rows = [
      [t("home_key"), pc.home_key], [t("meter"), pc.time_signature],
      [t("length"), `${pc.n_measures} ${t("measures")}`], [t("tempo"), pc.tempo_marking],
      [t("harmony"), pc.harmony_source === "expert" ? t("expert") : t("auto")],
    ];
    if (data.themes && data.themes[0]) {
      const th = data.themes[0];
      const n = (data.theme_occurrences || []).filter((o) => o.kind !== "original").length;
      rows.push([t("opening_theme"), `${partName(th.part)}, ${t("m")} ${th.start_label}${lang === "zh" ? " 小节" : ""} · ${n} × ${t("returns")}`]);
    }
    if (data.alignment) rows.push([t("performed"), data.alignment.order_description]);
    if (data.score_quality && pc.harmony_source === "auto") rows.push([t("score_quality"), data.score_quality.verdict]);
    $("glance").innerHTML = `<dl class="glance">${rows.filter((r) => r[1]).map((r) => `<dt>${esc(r[0])}</dt><dd>${esc(r[1])}</dd>`).join("")}</dl>`;

    const vars = data.variations || [];
    $("var-title").hidden = !vars.length;
    $("variations").innerHTML = vars.map((v) => {
      const hs = v.harmonic_similarity_to_theme;
      const bits = [];
      if (v.theme_tune_best_part) bits.push(`${t("tune_in")} <b>${esc(partName(v.theme_tune_best_part))}</b>`);
      if (hs != null) bits.push(`${t("same_harmony")}: ${Math.round(hs * 100)}%`);
      bits.push(`${t("busier")}: ${v.note_density_vs_theme}×`);
      return `<div class="var" data-label="${esc(v.start_label)}"><b>${esc(v.name)}</b> <span class="muted small">${t("m")} ${esc(v.start_label)}–${esc(v.end_label)}</span>
        <div class="small">${bits.join(" · ")}</div>
        ${hs != null ? `<div class="bar"><i style="width:${Math.round(hs * 100)}%"></i></div>` : ""}</div>`;
    }).join("");
    $("variations").querySelectorAll(".var").forEach((el) => el.addEventListener("click", () => seekLabel(el.dataset.label)));
    $("method").innerHTML = Object.values(data.method_notes || {}).map((m) => `<li>${esc(m)}</li>`).join("");
    const c = data.credits || {};
    const audioCredit = (data.alignment && data.alignment.credit) || c.audio;
    $("credits").textContent = [c.score && `Score: ${c.score}`, audioCredit && `Recording: ${audioCredit}`].filter(Boolean).join(" · ");
    drawCompare();
  }

  // ------------------------------------------------------------ playback
  function currentIndex(sec) {
    let lo = 0, hi = played.length - 1, ans = 0;
    while (lo <= hi) { const mid = (lo + hi) >> 1; if (played[mid].start_sec <= sec) { ans = mid; lo = mid + 1; } else hi = mid - 1; }
    return ans;
  }

  function onTime() {
    if (!played.length) return;
    const sec = data.alignment ? audio.currentTime : 0;
    if (data.alignment && !audio.paused && !loop && sec > total + 2.5) { audio.pause(); playNextMovement(); }
    $("cur").textContent = fmt(Math.max(0, sec - t0));
    const i = currentIndex(sec);
    const p = played[i], f = p.f;
    $("now-measure").textContent = p.label;
    highlightMeasure(p.mc);
    $("now-section").textContent = f.section || "–";
    $("now-key").textContent = f.key || "–";
    $("now-dyn").textContent = f.dynamic === "unmarked" ? "–" : f.dynamic;
    $("now-tex").textContent = (t("textures")[f.texture] || f.texture);
    document.querySelectorAll(".row-label[data-part]").forEach((el) =>
      el.classList.toggle("is-lead", el.dataset.part === f.lead || el.dataset.part === f.co_lead));
    // playhead: lanes start after the label column
    const tl = $("timeline"), lane = $("lane-sections");
    const x = lane.offsetLeft + lane.offsetWidth * Math.max(0, Math.min(1, (sec - t0) / span()));
    $("playhead").style.left = `${x}px`;
    updateCompareNow();
    // highlight the guide point that contains this measure
    const pos = (lab) => (labelOcc[lab] || [])[0] ?? -1;
    document.querySelectorAll(".point").forEach((el) => {
      const occS = labelOcc[el.dataset.start] || [], occE = labelOcc[el.dataset.end] || [];
      let on = false;
      occS.forEach((s) => occE.forEach((e) => { if (e >= s && i >= s && i <= e) on = true; }));
      if (!occS.length && pos(el.dataset.start) === i) on = true;
      el.classList.toggle("current", on);
    });
    void tl;
  }

  function seekLabel(label) {
    const occ = labelOcc[String(label)];
    if (!occ || !occ.length) return;
    // prefer the next occurrence after the current position, else the first
    const now = currentIndex(audio.currentTime || 0);
    const target = occ.find((o) => o > now) ?? occ[0];
    seekTo(played[target].start_sec);
  }

  function seekTo(sec) {
    if (!data.alignment) return;
    audio.currentTime = sec;
    if (audio.paused) audio.play().catch(() => {});
    onTime();
  }

  function onTimelineClick(e) {
    const lane = $("lane-sections");
    const r = lane.getBoundingClientRect();
    if (e.clientX < r.left) return;
    seekTo(t0 + Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * span());
  }

  // ------------------------------------------------------------ practice
  // Loop a passage, slow down without changing pitch, optional count-in clicks.
  let loop = null, picking = 0, pickA = null, counting = null, actx = null;

  function initPractice() {
    const sp = $("speed");
    const setSpeed = () => {
      audio.playbackRate = (+sp.value) / 100;
      audio.preservesPitch = true; audio.mozPreservesPitch = true; audio.webkitPreservesPitch = true;
      $("speed-val").textContent = `${sp.value}%`;
    };
    sp.addEventListener("input", setSpeed);
    setSpeed();
    $("loop-pick").addEventListener("click", () => {
      if (picking) { picking = 0; updateLoopInfo(); return; }
      picking = 1; pickA = null; updateLoopInfo();
      if (data.score) $("score-card").scrollIntoView({behavior: "smooth", block: "start"});
    });
    $("loop-clear").addEventListener("click", () => clearLoop());
    requestAnimationFrame(loopWatch);
  }

  function occurrenceNear(mc, fromIndex) {
    // the occurrence of this bar at or before the current position, else the first one
    const occ = played.map((p, i) => (p.mc === mc ? i : -1)).filter((i) => i >= 0);
    if (!occ.length) return -1;
    const before = occ.filter((i) => i <= fromIndex);
    return before.length ? before[before.length - 1] : occ[0];
  }

  function pickBar(mc) {
    if (picking === 1) { pickA = mc; picking = 2; updateLoopInfo(); return; }
    picking = 0;
    const now = currentIndex(audio.currentTime || 0);
    let ia = occurrenceNear(pickA, now);
    let ib = played.findIndex((p, i) => i >= ia && p.mc === mc);
    if (ib < 0) {                                  // clicked the end first: swap
      ib = occurrenceNear(mc, now);
      ia = played.findIndex((p, i) => i >= ib && p.mc === pickA);
      if (ia < 0) { updateLoopInfo(); return; }
      [ia, ib] = [ib, ia];
    }
    loop = {ia, ib, s: played[ia].start_sec, e: played[ib].end_sec, a: played[ia].label, b: played[ib].label};
    updateLoopInfo();
    drawLoop();
    startLoop();
  }

  function clearLoop(quiet) {
    loop = null; picking = 0; pickA = null;
    if (!quiet) { stopCount(); }
    updateLoopInfo();
    drawLoop();
  }

  function updateLoopInfo() {
    const info = $("loop-info");
    $("score").classList.toggle("picking", !!picking);
    $("loop-pick").classList.toggle("on", !!picking);
    if (picking === 1) info.textContent = t("pick_first");
    else if (picking === 2) info.textContent = t("pick_last");
    else info.textContent = loop ? t("looping").replace("{a}", loop.a).replace("{b}", loop.b) : "";
    $("loop-clear").hidden = !loop;
  }

  function drawLoop() {
    const root = $("score");
    root.querySelectorAll(".qc-loopbox").forEach((el) => el.remove());
    root.querySelectorAll(".qc-inloop").forEach((el) => el.classList.remove("qc-inloop"));
    if (!loop || !data || !data.score) return;
    const mcs = new Set(played.slice(loop.ia, loop.ib + 1).map((p) => String(p.mc)));
    mcs.forEach((mc) => {
      const m = data.score.measures[mc];
      if (!m) return;
      if (data.score.kind === "image") {
        const page = root.querySelector(".qc-page");
        if (!page) return;
        m.boxes.filter((b) => b.page === scorePage).forEach((b) => {
          const el = document.createElement("div");
          el.className = "qc-loopbox";
          Object.assign(el.style, {left: `${b.x0 * 100}%`, top: `${b.y0 * 100}%`,
            width: `${(b.x1 - b.x0) * 100}%`, height: `${(b.y1 - b.y0) * 100}%`});
          page.appendChild(el);
        });
      } else {
        const g = root.querySelector(`[data-id="${m.id}"]`) || root.querySelector(`#${CSS.escape(m.id)}`);
        if (g) g.classList.add("qc-inloop");
      }
    });
  }

  // ------------------------------------------------------------ bars to compare by ear (OMR scores)
  function renderDoubts() {
    const list = (data && data.score_doubts) || [];
    const box = $("doubts");
    box.hidden = !list.length || !data.score;
    if (box.hidden) return;
    $("doubts-title").textContent = t("doubts_title").replace("{n}", list.length);
    $("doubts-body").textContent = t("doubts_body");
    $("doubts-list").innerHTML = list.map((d) =>
      `<button type="button" class="doubt-chip" data-mc="${d.mc}" title="${d.reasons.includes("length") ? esc(t("doubt_length")) : ""}">` +
      `${esc(t("m"))} ${esc(d.label)}${d.reasons.includes("length") ? " *" : ""}</button>`).join("");
  }

  function drawDoubts() {
    const root = $("score");
    root.querySelectorAll(".qc-doubtbox").forEach((el) => el.remove());
    root.querySelectorAll(".qc-doubt").forEach((el) => el.classList.remove("qc-doubt"));
    const list = (data && data.score_doubts) || [];
    if (!list.length || !data.score) return;
    list.forEach((d) => {
      const m = data.score.measures[String(d.mc)];
      if (!m) return;
      if (data.score.kind === "image") {
        const page = root.querySelector(".qc-page");
        if (!page) return;
        m.boxes.filter((b) => b.page === scorePage).forEach((b) => {
          const el = document.createElement("div");
          el.className = "qc-doubtbox";
          Object.assign(el.style, {left: `${b.x0 * 100}%`, top: `${b.y0 * 100}%`,
            width: `${(b.x1 - b.x0) * 100}%`, height: `${(b.y1 - b.y0) * 100}%`});
          page.appendChild(el);
        });
      } else {
        const g = root.querySelector(`[data-id="${m.id}"]`) || root.querySelector(`#${CSS.escape(m.id)}`);
        if (g) g.classList.add("qc-doubt");
      }
    });
  }

  function beatsOf(i) {
    // count-in beats for this bar: 6/8 -> 2, 9/8 -> 3, 2/2 -> 2, 3/4 -> 3 ...
    const ts = (data.timesig || {})[String(played[i].mc)] || "4/4";
    const [n, d] = ts.split("/").map(Number);
    if (!n || !d) return 4;
    if (d === 8 && n % 3 === 0 && n > 3) return n / 3;
    return Math.min(n, 6);
  }

  function click(time, accent) {
    const o = actx.createOscillator(), g = actx.createGain();
    o.frequency.value = accent ? 1568 : 1046;
    g.gain.setValueAtTime(0.0001, time);
    g.gain.exponentialRampToValueAtTime(0.5, time + 0.005);
    g.gain.exponentialRampToValueAtTime(0.0001, time + 0.08);
    o.connect(g).connect(actx.destination);
    o.start(time); o.stop(time + 0.1);
  }

  function startLoop(fromSec) {
    // jump to the loop start (or fromSec), with a count-in if asked
    if (!loop) return;
    stopCount();
    const at = fromSec ?? loop.s;
    audio.pause();
    audio.currentTime = at;
    onTime();
    if (!$("countin").checked) { audio.play().catch(() => {}); return; }
    try { actx = actx || new (window.AudioContext || window.webkitAudioContext)(); actx.resume(); } catch (e) { actx = null; }
    if (!actx) { audio.play().catch(() => {}); return; }
    const i = currentIndex(at);
    const n = beatsOf(i);
    const barSec = Math.max(0.6, played[i].end_sec - played[i].start_sec);
    const beat = Math.min(1.5, Math.max(0.25, barSec / n)) / audio.playbackRate;
    const t0a = actx.currentTime + 0.1;
    for (let k = 0; k < n; k++) click(t0a + k * beat, k === 0);
    counting = setTimeout(() => { counting = null; audio.play().catch(() => {}); }, (0.1 + n * beat) * 1000);
  }

  function stopCount() { if (counting) { clearTimeout(counting); counting = null; } }

  function loopWatch() {
    // checked every frame (timeupdate fires only ~4 times a second)
    if (loop && !audio.paused && !counting && audio.currentTime >= loop.e - 0.03) startLoop();
    requestAnimationFrame(loopWatch);
  }

  // ------------------------------------------------------------ library
  // Search and filter every movement in pieces/index.json. Chinese composer
  // names, nicknames and key names are searchable too.
  const COMPOSER_ZH = {haydn: "海顿", mozart: "莫扎特", beethoven: "贝多芬", schubert: "舒伯特", dvorak: "德沃夏克",
    borodin: "鲍罗丁", debussy: "德彪西", mendelssohn: "门德尔松", ravel: "拉威尔", smetana: "斯美塔那",
    tchaikovsky: "柴可夫斯基", brahms: "勃拉姆斯", grieg: "格里格", schumann: "舒曼", janacek: "雅纳切克",
    handel: "亨德尔", halvorsen: "哈尔沃森", boccherini: "博凯里尼", verdi: "威尔第", puccini: "普契尼"};
  const NICK_ZH = {"emperor": "皇帝", "kaiser": "皇帝", "death and the maiden": "死神与少女", "american": "美国",
    "lark": "云雀", "dissonance": "不协和音", "eine kleine nachtmusik": "小夜曲", "sunrise": "日出", "hunt": "狩猎",
    "rider": "骑士", "fifths": "五度", "razumovsky": "拉祖莫夫斯基", "passacaglia": "帕萨卡利亚", "rosamunde": "罗莎蒙德",
    "notturno": "夜曲", "trio": "三重奏"};
  const fold = (x) => String(x || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  function keyZh(key) {
    const m = /^([A-G])(?:[- ]?(flat|sharp|♭|♯|b|#))?\s+(major|minor)$/i.exec(String(key || "").trim());
    if (!m) return "";
    const acc = m[2] ? (/flat|♭|^b$/i.test(m[2]) ? "降" : "升") : "";
    const minor = m[3].toLowerCase() === "minor";
    return `${acc}${minor ? m[1].toLowerCase() : m[1].toUpperCase()}${minor ? "小调" : "大调"}`;
  }
  const keyText = (k) => (lang === "zh" && keyZh(k)) || k || "";
  // "G. F. Handel / J. Halvorsen": filter by the first name, show both
  const lastName = (c) => { const parts = fold(c).replace(/[^a-z ]/g, " ").trim().split(/\s+/); return parts[parts.length - 1] || ""; };
  const composerKey = (c) => lastName(String(c || "").split("/")[0]);
  const composerLabel = (c) => lang !== "zh" ? c :
    String(c || "").split("/").map((x) => COMPOSER_ZH[lastName(x)] || x.trim()).join(" / ");
  function haystack(p) {
    const extra = [String(p.composer || "").split("/").map((x) => COMPOSER_ZH[lastName(x)] || "").join(" "),
      keyZh(p.key), p.key, p.tempo, p.id];
    for (const [k, v] of Object.entries(NICK_ZH)) if (fold(p.title).includes(k)) extra.push(v);
    return fold([p.title, p.composer, ...extra].join(" "));
  }
  function lenClass(sec) { return sec == null ? "" : sec < 300 ? "short" : sec <= 600 ? "mid" : "long"; }

  function fillLibraryFilters() {
    const comp = $("lib-composer"), keep = comp.value;
    const names = [...new Map(index.map((p) => [composerKey(p.composer), p.composer])).entries()]
      .sort((a, b) => a[0].localeCompare(b[0]));
    comp.innerHTML = `<option value="">${esc(t("lib_all_composers"))}</option>` +
      names.map(([k, c]) => `<option value="${esc(k)}">${esc(composerLabel(c))}</option>`).join("");
    comp.value = keep;
    const opts = (id, list) => { const el = $(id), v = el.value; el.innerHTML = list.map(([val, lab]) => `<option value="${val}">${esc(lab)}</option>`).join(""); el.value = v || ""; };
    opts("lib-mode", [["", t("lib_any_mode")], ["major", t("major")], ["minor", t("minor")]]);
    opts("lib-len", [["", t("lib_any_len")], ["short", t("len_short")], ["mid", t("len_mid")], ["long", t("len_long")]]);
    const ens = [...new Set(index.map((p) => p.ensemble).filter(Boolean))];
    $("lib-ens").hidden = ens.length < 2;
    opts("lib-ens", [["", t("lib_any_ens")], ...ens.map((e) => [e, t("ens_" + e)])]);
    $("lib-q").placeholder = t("lib_search");
  }

  function renderLibrary() {
    const words = fold($("lib-q").value).split(/\s+/).filter(Boolean);
    const comp = $("lib-composer").value, mode = $("lib-mode").value, len = $("lib-len").value, ens = $("lib-ens").value;
    const needGuide = $("lib-guide").checked;
    const hits = index.filter((p) => {
      if (comp && composerKey(p.composer) !== comp) return false;
      if (mode && p.mode !== mode) return false;
      if (len && lenClass(p.duration_sec) !== len) return false;
      if (ens && p.ensemble !== ens) return false;
      if (needGuide && !(p.languages || []).includes(lang)) return false;
      const h = haystack(p);
      return words.every((w) => h.includes(w));
    });
    const works = [];
    hits.forEach((p) => { const w = works.find((x) => x.work === p.work); if (w) w.items.push(p); else works.push({work: p.work, items: [p]}); });
    $("lib-count").textContent = t("lib_count").replace("{m}", hits.length).replace("{w}", works.length);
    if (!hits.length) { $("lib-list").innerHTML = `<p class="muted">${esc(t("lib_none"))}</p>`; return; }
    const current = data && data.id;
    $("lib-list").innerHTML = works.map((w) => {
      const first = w.items[0], workTitle = first.title.split(" – ")[0];
      const all = index.filter((p) => p.work === w.work);
      const tot = all.reduce((s, p) => s + (p.duration_sec || 0), 0);
      return `<section class="lib-work"><div class="lib-work-head"><span class="lib-work-title">${esc(workTitle)}</span>` +
        `<span class="muted small">${esc(composerLabel(first.composer))} · ${all.length} ${esc(t("lib_mvts"))}${tot ? " · " + fmt(tot) : ""}</span></div>` +
        w.items.map((p) => {
          const mv = p.title.split(" – ").slice(1).join(" – ") || p.title;
          const badges = (p.languages || []).map((l) => `<span class="lib-badge">${l === "zh" ? "中" : "EN"}</span>`).join("") +
            (p.has_audio ? "" : `<span class="lib-badge off">${esc(t("lib_no_audio"))}</span>`);
          return `<button type="button" class="lib-item${p.id === current ? " on" : ""}" data-id="${esc(p.id)}">` +
            `<span class="lib-mv">${esc(mv)}</span><span class="lib-meta">${esc(keyText(p.key))}` +
            `${p.duration_sec ? " · " + fmt(p.duration_sec) : ""}</span><span class="lib-badges">${badges}</span></button>`;
        }).join("") + `</section>`;
    }).join("");
  }

  function initLibrary() {
    const dlg = $("library");
    const open = () => { fillLibraryFilters(); renderLibrary(); if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", ""); $("lib-q").focus(); };
    const close = () => { if (dlg.close) dlg.close(); else dlg.removeAttribute("open"); };
    $("lib-open").addEventListener("click", open);
    $("lib-close").addEventListener("click", close);
    dlg.addEventListener("click", (e) => { if (e.target === dlg) close(); });   // click outside the panel
    ["lib-q", "lib-composer", "lib-mode", "lib-len", "lib-ens", "lib-guide"].forEach((id) =>
      $(id).addEventListener(id === "lib-q" ? "input" : "change", renderLibrary));
    $("lib-list").addEventListener("click", (e) => {
      const b = e.target.closest(".lib-item");
      if (!b) return;
      close();
      $("piece-select").value = b.dataset.id;
      location.hash = b.dataset.id;
      load(b.dataset.id);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "/" && e.target === document.body) { e.preventDefault(); open(); }
    });
  }

  window.addEventListener("resize", onTime);
  window.qcDebug = { keyZh, highlightMeasure, showPage, audio, pickBar: (mc) => pickBar(mc), startPick: () => $("loop-pick").click(), getLoop: () => loop };       // for automated screenshots
  init();
})();
