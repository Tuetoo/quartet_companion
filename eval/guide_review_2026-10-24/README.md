# Review of all listening guides (24 Oct 2026)

All 28 guides (14 movements × English and Chinese) were reviewed line by line
against the facts each guide was written from.

1. **Machine audit** of the prose (measure references, keys, dynamics, section
   names, instruments, hedging, outside knowledge): 32 flags.
2. **First human-style review** by four independent reviewers, one per work
   (`review_A.md` … `review_D.md`): about 250 findings, of which 13 factual errors.
3. All findings were checked against the facts and corrected (`edits_A.json` …).
4. **Second independent review** of the corrected guides (`second_review_1.md`,
   `second_review_2.md`): 97 remaining or new findings (3 errors, mostly left-over
   editing debris), all corrected (`edits_H*.json`, `edits_I.json`, `edits_J.json`).
5. Chinese loudness terms standardised: 弱 (p), 很弱 (pp), 强 (f), 很强 (ff);
   主调织体 for homophonic; 本乐章 for one movement.
6. Final state: every claim verified (0 failed), 0 prose-check issues.

What the review taught us is now built into guide generation:
`guide/prose_check.py` checks the prose of every new guide (keys named in the text,
"alone" only where a part is solo, gradual changes only with cresc/dim, the
loudest point presented as an estimate, low-confidence leads hedged, measure
references in range, standard Chinese terms). Problems are sent back to the model
once, like failed claims. On the original 28 guides this check finds 68 of the
problems; on the corrected guides it finds none. The writing rules in
`guide/generate.py` (rules 9 and 10) were extended in the same way.

The guide files before the review are kept next to the new ones as
`pieces/<id>/guide_<lang>.before_review.json`.
