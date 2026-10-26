"""OpenScore library: search and splitting a whole work into movements (offline)."""
from quartet_companion.io.library import _movement_starts, search, split_movements

XML = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1"><part-list><score-part id="P1"><part-name>Violin 1</part-name></score-part></part-list>
<part id="P1">
 <measure number="1"><attributes><divisions>2</divisions><key><fifths>0</fifths></key>
   <time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes>
   <direction><direction-type><words>I. Allegro</words></direction-type></direction>
   <note><pitch><step>C</step><octave>5</octave></pitch><duration>8</duration></note></measure>
 MEAS
 <measure number="0"><attributes><key><fifths>1</fifths></key><time><beats>3</beats><beat-type>4</beat-type></time></attributes>
   <direction><direction-type><words>II. Andante</words></direction-type></direction>
   <note><pitch><step>D</step><octave>5</octave></pitch><duration>2</duration></note></measure>
 <measure number="1"><note><pitch><step>E</step><octave>5</octave></pitch><duration>6</duration></note></measure>
</part></score-partwise>"""
MEAS = "".join(f'<measure number="{i}"><note><pitch><step>C</step><octave>5</octave></pitch><duration>8</duration></note></measure>'
               for i in range(2, 9))


def test_movement_starts():
    assert _movement_starts(["1", "2", "3", "4", "5", "0", "1", "2", "1", "2"]) == [0, 5]
    assert _movement_starts(["1", "2", "3", "4", "5", "6", "1", "2"]) == [0, 6]


def test_split_keeps_attributes(tmp_path):
    from quartet_companion.io.musicxml import load_music_file
    src = tmp_path / "w.musicxml"
    src.write_text(XML.replace("MEAS", MEAS))
    files = split_movements(src, tmp_path / "out")
    assert len(files) == 2
    s2 = load_music_file(files[1], "x")
    assert len(s2.measures) == 2 and s2.measures["timesig"].iloc[0] == "3/4" and int(s2.measures["keysig"].iloc[0]) == 1
    assert s2.validate() == []
    s1 = load_music_file(files[0], "x")
    assert len(s1.measures) == 8


def test_search_ignores_accents():
    rows = [{"path": "Dvořák,_Antonín/String_Quartet_No.12", "name": "String Quartet No.12 “American”",
             "composer": "Dvořák, Antonín"},
            {"path": "Haydn,_Joseph/Op.76_No.3", "name": "String Quartet Op.76 No.3", "composer": "Haydn, Joseph"}]
    assert search(rows, ["dvorak", "american"]) == rows[:1]
    assert search(rows, ["haydn", "76", "3"]) == rows[1:]
    assert search(rows, ["haydn", "7"]) == []          # numbers match whole numbers only


def test_movement_starts_skip_unnumbered_bars():
    from quartet_companion.io.library import _movement_starts
    # K.465 in OpenScore: the Menuetto ends with an unnumbered bar "X4", then the finale starts at 0
    assert _movement_starts(["0", "1", "2", "63", "X4", "0", "1"]) == [0, 5]
    assert _movement_starts(["1", "2", "X1", "3", "4"]) == [0]


def test_unplayed_bars_after_final_barline_are_dropped():
    import xml.etree.ElementTree as ET
    from quartet_companion.io.library import _played_end

    def bar(final=False, words=""):
        m = ET.Element("measure")
        if words:
            ET.SubElement(ET.SubElement(ET.SubElement(m, "direction"), "direction-type"), "words").text = words
        if final:
            ET.SubElement(ET.SubElement(m, "barline"), "bar-style").text = "light-heavy"
        return m
    # Op.135/III in OpenScore: 54 bars, final barline, then the 5-bar motto of the finale
    ms = [bar() for _ in range(53)] + [bar(final=True)] + [bar(words="Grave")] + [bar() for _ in range(3)] + [bar(final=True)]
    assert _played_end(ms, 0, len(ms)) == 54
    # a Menuetto with Fine and a short Trio keeps everything
    ms = [bar() for _ in range(15)] + [bar(final=True, words="Fine")] + [bar(words="Trio")] + [bar() for _ in range(6)] + [bar(final=True)]
    assert _played_end(ms, 0, len(ms)) == len(ms)
