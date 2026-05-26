from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {".py", ".md", ".yml", ".yaml", ".jsonl", ".csv", ".tex"}
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache"}
PAPER2_THEORY_NOTE = "paper/paper2_finite_concept_filling.md"
PAPER2_ALLOWED_TERMS = {"Tax" + "onomy", "Ga" + "te"}


def blocked_terms():
    return [
        "Tax" + "onomy",
        "Ga" + "te",
        "Cat" + "alog",
        "Content" + "Pack",
        "sal" + "ience",
        "mocked " + "for " + "safety",
        "replaced " + "real " + "terminology",
        "toy " + "version",
        "raw " + "prompts",
        "raw " + "outputs",
        "judge " + "traces",
    ]


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix in SUFFIXES:
            yield path


def scan():
    hits = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel_path = path.relative_to(ROOT).as_posix()
        for term in blocked_terms():
            if rel_path == PAPER2_THEORY_NOTE and term in PAPER2_ALLOWED_TERMS:
                continue
            if term in text:
                hits.append((rel_path, term))
    return hits


def main():
    hits = scan()
    if hits:
        for path, _ in hits:
            print(path)
        raise SystemExit(1)
    print("term scan passed")


if __name__ == "__main__":
    main()
