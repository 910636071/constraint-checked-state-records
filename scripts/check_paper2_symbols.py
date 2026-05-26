from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "paper2_finite_concept_filling.md"

REQUIRED_DEFINITIONS = [
    "Definition 1 (Finite concept space)",
    "Definition 2 (Typed symbolic record)",
    "Definition 3 (Constraint set)",
    "Definition 4 (Append-only event sequence)",
    "Definition 5 (Validation interface)",
    "Definition 6 (Typing interface)",
    "Definition 7 (Commitment interface)",
    "Definition 8 (Accepted observation sequence)",
    "Definition 9 (Vector estimator)",
    "Definition 10 (Scalar estimator)",
]

REQUIRED_SYMBOLS = [
    "`K`",
    "`n`",
    "`C`",
    "`E_t`",
    "`V`",
    "`T`",
    "`J`",
    "`B_m`",
    "`phi`",
    "`X_i`",
    "`C_m`",
    "`Y_i`",
    "`mu_hat_m`",
    "`E`",
]

FORBIDDEN_PHRASES = [
    "Concept" + "Object",
    "Event" + "Log",
    "Asset" + "Ga" + "te",
    "Tax" + "onomy" + "Ga" + "te",
    "Judgement" + "Ga" + "te",
    "Paper " + "3",
    "render" + "er",
    "raw " + "text " + "variance",
]


def check_text(text):
    missing = []
    for item in REQUIRED_DEFINITIONS:
        if item not in text:
            missing.append(f"missing definition: {item}")
    for item in REQUIRED_SYMBOLS:
        if item not in text:
            missing.append(f"missing symbol: {item}")
    for item in FORBIDDEN_PHRASES:
        if item in text:
            missing.append(f"forbidden phrase: {item}")
    return missing


def main():
    text = PAPER.read_text(encoding="utf-8")
    missing = check_text(text)
    if missing:
        for item in missing:
            print(item)
        raise SystemExit(1)
    print("paper2 symbol check passed")


if __name__ == "__main__":
    main()
