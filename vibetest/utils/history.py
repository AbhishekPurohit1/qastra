import json
from pathlib import Path

HISTORY_FILE = Path("vibetest_history.json")


def _load_history():
    try:
        if not HISTORY_FILE.exists():
            return {}
        with HISTORY_FILE.open() as f:
            return json.load(f)
    except Exception:
        return {}


def _save_history(data):
    try:
        with HISTORY_FILE.open("w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        # History persistence is best-effort; failures should not break tests.
        pass


def save_fingerprint(label, fingerprint):

    data = _load_history()
    data[label] = fingerprint
    _save_history(data)


def load_fingerprint(label):

    data = _load_history()
    return data.get(label)

