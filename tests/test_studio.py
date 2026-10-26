"""The add-a-piece page's server (no browser, no network)."""
import json
import threading
import urllib.error
import urllib.request

from quartet_companion import studio


def test_suggest_prefix():
    ex = {"k525_1", "mozart_k458_1"}
    assert studio.suggest_prefix({"composer": "Mozart, Wolfgang Amadeus", "name": "String Quartet No.17, K.458", "id": "1"}, ex) == "mozart_k458_2"
    assert studio.suggest_prefix({"composer": "Haydn, Joseph", "name": "String Quartet, Op.76 No.4", "id": "2"}, ex) == "haydn_op76_4"
    assert studio.suggest_prefix({"composer": "Schubert, Franz", "name": "String Quartet in A minor, D.804", "id": "3"}, ex) == "schubert_d804"
    assert studio.suggest_prefix({"composer": "Debussy, Claude", "name": "String Quartet", "id": "8661306"}, ex) == "debussy_8661306"


def test_add_rejects_bad_requests(tmp_path):
    (tmp_path / "site").mkdir()
    (tmp_path / "site" / "index.html").write_text("<html></html>")
    (tmp_path / "incoming").mkdir()
    (tmp_path / "incoming" / "a.mp3").write_bytes(b"x")
    (tmp_path / "pieces" / "used_1").mkdir(parents=True)
    (tmp_path / "pieces" / "used_1" / "config.json").write_text(json.dumps({"audio": {"path": "incoming/a.mp3"}}))
    t = threading.Thread(target=studio.serve, args=(tmp_path, 8791), daemon=True)
    t.start()
    import time
    time.sleep(0.8)

    def post(body):
        req = urllib.request.Request("http://127.0.0.1:8791/api/add", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            return 200, json.load(urllib.request.urlopen(req))
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)
    assert post({"id": "1", "prefix": "Bad!", "audio": []})[1]["code"] == "bad_name"
    assert post({"id": "1", "prefix": "used", "audio": []})[1]["code"] == "name_taken"
    assert post({"id": "1", "prefix": "new", "audio": ["../secret.mp3"]})[1]["code"] == "bad_file"
    inc = json.load(urllib.request.urlopen("http://127.0.0.1:8791/api/incoming"))
    assert inc == [{"path": "incoming/a.mp3", "name": "a.mp3", "mb": 0.0, "used": True}]
