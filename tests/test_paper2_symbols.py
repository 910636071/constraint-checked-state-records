from scripts.check_paper2_symbols import PAPER, check_text


def test_paper2_symbol_contract():
    text = PAPER.read_text(encoding="utf-8")
    assert check_text(text) == []
