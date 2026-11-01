import json
import os
import sys
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from levelup import config
from levelup.app import build_share_url, display_share_section, render_shared_analysis
from levelup.share import (
    generate_share_id,
    is_valid_share_id,
    load_shared_analysis,
    save_shared_analysis,
)

SAMPLE_RESULT = {
    "language": "English",
    "domain_scores": [{"domain": "IT", "score": 90, "justification": "Strong"}],
    "overall_summary": {"overall_score": 85},
}


def test_generate_share_id_is_unguessable_and_unique() -> None:
    ids = {generate_share_id() for _ in range(100)}
    assert len(ids) == 100
    for share_id in ids:
        assert is_valid_share_id(share_id)
        assert len(share_id) >= 16


def test_is_valid_share_id_rejects_malicious_ids() -> None:
    assert not is_valid_share_id("")
    assert not is_valid_share_id("short")
    assert not is_valid_share_id("../../../etc/passwd")
    assert not is_valid_share_id("id with spaces 1234")
    assert not is_valid_share_id("a" * 100)
    assert is_valid_share_id("abcDEF123456_-789012")


def test_save_and_load_roundtrip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "SHARED_RESULTS_DIR", str(tmp_path))

    share_id = save_shared_analysis(SAMPLE_RESULT, "English", "Data Scientist")

    assert is_valid_share_id(share_id)
    payload = load_shared_analysis(share_id)
    assert payload is not None
    assert payload["result"] == SAMPLE_RESULT
    assert payload["report_language"] == "English"
    assert payload["target_role"] == "Data Scientist"
    assert payload["share_id"] == share_id
    assert payload["created_at"]


def test_save_without_target_role(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "SHARED_RESULTS_DIR", str(tmp_path))

    share_id = save_shared_analysis(SAMPLE_RESULT, "Turkish")

    payload = load_shared_analysis(share_id)
    assert payload is not None
    assert payload["target_role"] is None
    assert payload["report_language"] == "Turkish"


def test_load_unknown_or_invalid_share_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "SHARED_RESULTS_DIR", str(tmp_path))

    assert load_shared_analysis("a" * 22) is None
    assert load_shared_analysis("../../../etc/passwd") is None


def test_load_corrupted_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(config, "SHARED_RESULTS_DIR", str(tmp_path))

    bad_json_id = "a" * 22
    (tmp_path / f"{bad_json_id}.json").write_text("not json", encoding="utf-8")
    assert load_shared_analysis(bad_json_id) is None

    bad_shape_id = "b" * 22
    (tmp_path / f"{bad_shape_id}.json").write_text(
        json.dumps({"result": "not a dict"}), encoding="utf-8"
    )
    assert load_shared_analysis(bad_shape_id) is None


def test_build_share_url_from_context(mocker: MockerFixture) -> None:
    mock_st = mocker.patch("levelup.app.st")
    mock_st.context.url = "http://localhost:8501/?foo=1"

    url = build_share_url("tok123")

    assert url == "http://localhost:8501/?foo=1&share_id=tok123"


def test_build_share_url_without_context(mocker: MockerFixture) -> None:
    mock_st = mocker.patch("levelup.app.st")
    mock_st.context.url = ""

    assert build_share_url("tok123") == "?share_id=tok123"


def test_render_shared_analysis_found(mocker: MockerFixture) -> None:
    mock_st = mocker.patch("levelup.app.st")
    mock_tabs = mocker.patch("levelup.app.display_analysis_tabs")
    mocker.patch(
        "levelup.app.load_shared_analysis",
        return_value={
            "result": SAMPLE_RESULT,
            "report_language": "English",
            "target_role": "Data Scientist",
        },
    )

    render_shared_analysis("tok123")

    mock_st.error.assert_not_called()
    mock_st.markdown.assert_any_call("**Target Role:** Data Scientist")
    mock_tabs.assert_called_once_with(SAMPLE_RESULT)


def test_render_shared_analysis_not_found(mocker: MockerFixture) -> None:
    mock_st = mocker.patch("levelup.app.st")
    mock_tabs = mocker.patch("levelup.app.display_analysis_tabs")
    mocker.patch("levelup.app.load_shared_analysis", return_value=None)

    render_shared_analysis("unknown")

    mock_st.error.assert_called_once()
    mock_tabs.assert_not_called()


def test_display_share_section_generates_link(mocker: MockerFixture) -> None:
    mock_st = mocker.patch("levelup.app.st")
    mock_st.session_state = {}
    mock_st.button.return_value = True
    mock_st.context.url = "http://example.com/"
    mocker.patch("levelup.app.save_shared_analysis", return_value="tok123")

    display_share_section(SAMPLE_RESULT, "English", None)

    assert mock_st.session_state["share_id"] == "tok123"
    mock_st.code.assert_called_once_with(
        "http://example.com/?share_id=tok123", language=None
    )


def test_display_share_section_handles_storage_error(mocker: MockerFixture) -> None:
    mock_st = mocker.patch("levelup.app.st")
    mock_st.session_state = {}
    mock_st.button.return_value = True
    mocker.patch("levelup.app.save_shared_analysis", side_effect=OSError("disk full"))

    display_share_section(SAMPLE_RESULT, "English", None)

    mock_st.error.assert_called_once()
    mock_st.code.assert_not_called()
