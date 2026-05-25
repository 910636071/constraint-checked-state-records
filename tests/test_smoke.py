from case_bank import load_cases
from scripts.make_cases import build_cases, write_jsonl


def test_case_generation_and_loading(tmp_path):
    path = tmp_path / "cases.jsonl"
    write_jsonl(build_cases(20), path)
    cases = load_cases(path)
    assert len(cases) == 20
    assert all(case["traces"] for case in cases)
