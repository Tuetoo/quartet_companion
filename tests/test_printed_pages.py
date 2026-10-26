"""Printed-page view: measure boxes from an Audiveris book (.omr)."""
import json
import zipfile

from PIL import Image

from conftest import make_score
from quartet_companion.io.omr_geometry import book_measure_boxes, printed_measure_map, save_printed_pages

SHEET = """<?xml version="1.0"?>
<sheet><picture width="1000" height="1400"/><scale><interline main="20"/></scale>
<page id="1">
 <system id="1">
  <stack id="1" left="100" right="500"/><stack id="2" left="500" right="900"/>
  <part id="1"><staff id="1"><lines>
   <line><point x="100" y="200"/><point x="900" y="200"/></line>
   <line><point x="100" y="280.5"/><point x="900" y="280.5"/></line></lines></staff></part>
 </system>
 <system id="2">
  <stack id="3" left="100" right="900"/>
  <part id="1"><staff id="1"><lines>
   <line><point x="100" y="600"/><point x="900" y="600"/></line>
   <line><point x="100" y="680"/><point x="900" y="680"/></line></lines></staff></part>
 </system>
</page></sheet>"""
BOOK = '<book><sheet number="1"><page id="1" movement-start="true"/></sheet></book>'
MXL = ('<score-partwise><part-list/><part id="P1"><measure number="0"/><measure number="1"/>'
       '<measure number="2"/></part></score-partwise>')


def _book(tmp_path):
    png = tmp_path / "b.png"
    Image.new("L", (1000, 1400), 255).save(png)
    omr = tmp_path / "x.omr"
    with zipfile.ZipFile(omr, "w") as z:
        z.writestr("book.xml", BOOK)
        z.writestr("sheet#1/sheet#1.xml", SHEET)
        z.write(png, "sheet#1/BINARY.png")
    xml = tmp_path / "x.musicxml"
    xml.write_text(MXL)
    return omr, xml


def test_boxes_follow_systems(tmp_path):
    omr, _ = _book(tmp_path)
    boxes = book_measure_boxes(omr, pad=0)
    assert len(boxes) == 3
    assert boxes[0]["movement_start"] and not boxes[1]["movement_start"]
    assert (boxes[0]["x0"], boxes[0]["x1"]) == (100, 500)
    assert boxes[0]["y0"] == 200 - 60 and boxes[2]["y0"] == 600 - 60        # 3 staff spaces above


def test_save_and_map(tmp_path):
    omr, xml = _book(tmp_path)
    assert save_printed_pages(omr, [xml], [tmp_path / "piece"], page_width=500) == [True]
    geo = json.loads((tmp_path / "piece" / "printed" / "geometry.json").read_text())
    assert [m["number"] for m in geo["measures"]] == ["0", "1", "2"]
    assert geo["pages"][0]["h"] == 700
    b = geo["measures"][1]["boxes"][0]
    assert b["page"] == 1 and 0.49 < b["x0"] < 0.52
    score = make_score([(1, 0, 1, 0, 60)], n_measures=3)
    m = printed_measure_map(score, geo)
    assert sorted(m) == list(score.measures["mc"].astype(int))
    assert m[int(score.measures["mc"].iloc[2])]["boxes"][0]["y0"] > 0.3     # third bar is on the second system


def test_count_mismatch_is_skipped(tmp_path):
    omr, xml = _book(tmp_path)
    xml.write_text(MXL.replace('<measure number="2"/>', '<measure number="2"/><measure number="3"/>'))
    assert save_printed_pages(omr, [xml], [tmp_path / "piece"]) == [False]


def test_set_repeats_by_hand():
    from quartet_companion.pieces import set_repeats
    from quartet_companion.unfold import _follow
    score = make_score([(1, 0, 1, 0, 60)], n_measures=6)
    set_repeats(score, [["2", "3"], ["5", "6"]])
    assert _follow(score.measures, True) == [1, 2, 3, 2, 3, 4, 5, 6, 5, 6]
    assert _follow(score.measures, False) == [1, 2, 3, 4, 5, 6]
    set_repeats(score, [])
    assert _follow(score.measures, True) == [1, 2, 3, 4, 5, 6]


def test_ocr_tempo_marks():
    from quartet_companion.align.tempo import is_metronome, parse_tempo
    assert parse_tempo("Largamente (Jz66)") == 66 and is_metronome("Largamente (Jz66)")
    assert parse_tempo("Conagilité(J:112)") == 112
    assert parse_tempo("=72") == 72
    assert not is_metronome("Andante") and parse_tempo("Andante") is not None
    assert parse_tempo("cresc. 1") is None and parse_tempo("Var. 2") is None


def test_consolidate_and_concat():
    from quartet_companion.io.omr import concat_scores, consolidate_parts
    from quartet_companion.unfold import _follow
    # OMR pieces: violin found as "Voice" in bars 1-2 and as "Violin" in bars 3-4, piano on two staves
    rows = [(1, 0, 1, 0, 76), (2, 0, 1, 0, 77), (3, 0, 1, 1, 79), (4, 0, 1, 1, 81),
            (1, 0, 1, 2, 72), (3, 0, 1, 2, 74), (1, 0, 1, 3, 48), (4, 0, 1, 3, 50),
            (1, 0, 1, 4, 45), (2, 0, 1, 4, 47), (3, 0, 1, 4, 45), (4, 0, 1, 4, 43)]
    a = make_score(rows, n_measures=4, parts=["Voice", "Violin", "Piano 1", "Piano 2", "Cello"])
    consolidate_parts(a, ["Violin", "Cello", "Piano"])
    assert a.parts == ["Violin", "Cello", "Piano"]
    by = a.notes.groupby("part")["midi"].apply(sorted).to_dict()
    assert by[0] == [76, 77, 79, 81] and by[1] == [43, 45, 45, 47] and by[2] == [48, 50, 72, 74]
    b = make_score([(1, 0, 1, 0, 70)], n_measures=2, parts=["Violin", "Cello", "Piano"])
    j = concat_scores([a, b])
    assert list(j.measures["mc"]) == [1, 2, 3, 4, 5, 6] and list(j.measures["mn"]) == [1, 2, 3, 4, 5, 6]
    assert _follow(j.measures, True) == [1, 2, 3, 4, 5, 6]
    assert j.notes["onset_qb"].max() == 16.0 and j.validate() == []
