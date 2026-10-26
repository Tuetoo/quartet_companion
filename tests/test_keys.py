from quartet_companion.keys import (dcml_local_key_name, key_label, midi_to_name, name_to_tpc,
                                    resolve_numeral_key, tpc_to_name)


def test_tpc_round_trip():
    for name in ["C", "G", "D", "F#", "Bb", "Eb", "Ab", "C#", "Cb", "E#"]:
        assert tpc_to_name(name_to_tpc(name)) == name


def test_local_keys_in_major():
    assert dcml_local_key_name("D", "I") == "D major"
    assert dcml_local_key_name("D", "V") == "A major"
    assert dcml_local_key_name("D", "vi") == "B minor"
    assert dcml_local_key_name("D", "bVI") == "Bb major"
    assert dcml_local_key_name("A", "iii") == "C# minor"


def test_local_keys_in_minor_use_natural_minor():
    assert dcml_local_key_name("a", "i") == "A minor"
    assert dcml_local_key_name("a", "III") == "C major"
    assert dcml_local_key_name("a", "V") == "E major"
    assert dcml_local_key_name("a", "VII") == "G major"
    assert dcml_local_key_name("c", "VI") == "Ab major"


def test_applied_keys():
    tpc, minor = resolve_numeral_key("V/V", 0, False)
    assert key_label(tpc, minor) == "D major"


def test_bad_numeral_falls_back():
    assert "of" in dcml_local_key_name("D", "xyz")


def test_midi_names():
    assert midi_to_name(60) == "C4"
    assert midi_to_name(69) == "A4"
