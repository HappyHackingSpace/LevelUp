from typing import Any

import altair as alt
from pytest_mock import MockerFixture

from levelup.app import display_competencies_tab, display_domains_tab
from levelup.charts import (
    BAND_HIGH,
    BAND_LOW,
    BAND_MEDIUM,
    BAND_ORDER,
    build_score_frame,
    competency_scores_chart,
    domain_scores_chart,
    score_band,
)

SAMPLE_DOMAINS: list[dict[str, Any]] = [
    {"domain": "Data Science", "score": 88, "justification": "Strong ML background"},
    {"domain": "Software Engineering", "score": 61, "justification": "Some backend"},
    {"domain": "Product Management", "score": 42, "justification": "Limited exposure"},
]

SAMPLE_COMPETENCIES: list[dict[str, Any]] = [
    {"category": "Core Skills", "score": 90, "strength": "X", "observation": "Y"},
    {"category": "Communication", "score": 55, "strength": "X", "observation": "Y"},
    {"category": "Leadership", "score": 30, "strength": "X", "observation": "Y"},
]


def test_score_band_boundaries() -> None:
    assert score_band(0) == BAND_LOW
    assert score_band(49.9) == BAND_LOW
    assert score_band(50) == BAND_MEDIUM
    assert score_band(74.9) == BAND_MEDIUM
    assert score_band(75) == BAND_HIGH
    assert score_band(100) == BAND_HIGH


def test_build_score_frame_sorts_descending() -> None:
    frame = build_score_frame(
        [
            {"domain": "B", "score": 40},
            {"domain": "A", "score": 90},
            {"domain": "C", "score": 70},
        ],
        "domain",
    )
    assert list(frame["label"]) == ["A", "C", "B"]
    assert list(frame["score"]) == [90.0, 70.0, 40.0]
    assert list(frame["band"]) == [BAND_HIGH, BAND_MEDIUM, BAND_LOW]


def test_build_score_frame_drops_invalid_entries() -> None:
    frame = build_score_frame(
        [
            {"domain": "Valid", "score": "75"},
            {"domain": "", "score": 80},
            {"domain": "NoScore"},
            {"domain": "BadScore", "score": "n/a"},
            {"domain": "BoolScore", "score": True},
            {"domain": "NoneScore", "score": None},
            "not-a-dict",
        ],
        "domain",
    )
    assert list(frame["label"]) == ["Valid"]
    assert list(frame["score"]) == [75.0]


def test_build_score_frame_clamps_out_of_range_scores() -> None:
    frame = build_score_frame(
        [
            {"domain": "TooHigh", "score": 150},
            {"domain": "TooLow", "score": -20},
        ],
        "domain",
    )
    assert list(frame["score"]) == [100.0, 0.0]


def test_build_score_frame_empty_inputs() -> None:
    assert build_score_frame([], "domain").empty
    assert build_score_frame(None, "domain").empty


def test_domain_scores_chart_returns_chart() -> None:
    chart = domain_scores_chart(SAMPLE_DOMAINS)
    assert isinstance(chart, alt.Chart)
    spec = chart.to_dict()
    assert spec["encoding"]["x"]["field"] == "score"
    assert spec["encoding"]["x"]["scale"]["domain"] == [0, 100.0]
    assert spec["encoding"]["y"]["field"] == "label"
    assert spec["encoding"]["color"]["field"] == "band"
    assert spec["encoding"]["color"]["scale"]["domain"] == BAND_ORDER


def test_domain_scores_chart_empty_returns_none() -> None:
    assert domain_scores_chart([]) is None
    assert domain_scores_chart(None) is None
    assert domain_scores_chart([{"domain": "X", "score": "bad"}]) is None


def test_competency_scores_chart_returns_chart() -> None:
    chart = competency_scores_chart(SAMPLE_COMPETENCIES)
    assert isinstance(chart, alt.Chart)
    frame = chart.data
    assert list(frame["label"]) == ["Core Skills", "Communication", "Leadership"]
    assert list(frame["band"]) == [BAND_HIGH, BAND_MEDIUM, BAND_LOW]


def test_competency_scores_chart_empty_returns_none() -> None:
    assert competency_scores_chart([]) is None
    assert competency_scores_chart(None) is None


def test_display_domains_tab_renders_chart(mocker: MockerFixture) -> None:
    mock_st = mocker.patch("levelup.app.st")

    display_domains_tab({"domain_scores": SAMPLE_DOMAINS})
    mock_st.altair_chart.assert_called_once()
    mock_st.dataframe.assert_called_once()

    mock_st.reset_mock()
    display_domains_tab({})
    mock_st.altair_chart.assert_not_called()
    mock_st.info.assert_called_once()


def test_display_competencies_tab_renders_chart(mocker: MockerFixture) -> None:
    mock_st = mocker.patch("levelup.app.st")

    display_competencies_tab({"competency_scores": SAMPLE_COMPETENCIES})
    mock_st.altair_chart.assert_called_once()
    mock_st.dataframe.assert_called_once()

    mock_st.reset_mock()
    display_competencies_tab({"competency_scores": []})
    mock_st.altair_chart.assert_not_called()
    mock_st.info.assert_called_once()
