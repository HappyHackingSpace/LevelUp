import math
from typing import Any, cast

import altair as alt
import pandas as pd  # type: ignore[import-untyped]

SCORE_MAX = 100.0

BAND_HIGH = "High (75-100)"
BAND_MEDIUM = "Medium (50-74)"
BAND_LOW = "Low (0-49)"

BAND_ORDER: list[str] = [BAND_HIGH, BAND_MEDIUM, BAND_LOW]
BAND_COLORS: dict[str, str] = {
    BAND_HIGH: "#0ca30c",
    BAND_MEDIUM: "#fab219",
    BAND_LOW: "#d03b3b",
}


def _coerce_score(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(score) or math.isinf(score):
        return None
    return min(max(score, 0.0), SCORE_MAX)


def score_band(score: float) -> str:
    if score >= 75.0:
        return BAND_HIGH
    if score >= 50.0:
        return BAND_MEDIUM
    return BAND_LOW


def build_score_frame(
    items: list[Any] | None,
    label_key: str,
    score_key: str = "score",
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get(label_key) or "").strip()
        score = _coerce_score(item.get(score_key))
        if not label or score is None:
            continue
        rows.append({"label": label, "score": score, "band": score_band(score)})
    frame = pd.DataFrame(rows, columns=["label", "score", "band"])
    return frame.sort_values("score", ascending=False, kind="stable").reset_index(
        drop=True
    )


def _score_bar_chart(frame: pd.DataFrame, label_title: str) -> alt.Chart:
    chart = (
        alt.Chart(frame)
        .mark_bar(cornerRadiusEnd=4, height=18)
        .encode(
            x=alt.X(
                "score:Q",
                title="Score",
                scale=alt.Scale(domain=[0, SCORE_MAX]),
            ),
            y=alt.Y("label:N", title=None, sort="-x"),
            color=alt.Color(
                "band:N",
                title="Score band",
                scale=alt.Scale(
                    domain=BAND_ORDER,
                    range=[BAND_COLORS[band] for band in BAND_ORDER],
                ),
                legend=alt.Legend(orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("label:N", title=label_title),
                alt.Tooltip("score:Q", title="Score"),
                alt.Tooltip("band:N", title="Band"),
            ],
        )
    )
    return cast(alt.Chart, chart)


def competency_scores_chart(
    competency_scores: list[dict[str, Any]] | None,
) -> alt.Chart | None:
    frame = build_score_frame(competency_scores, "category")
    if frame.empty:
        return None
    return _score_bar_chart(frame, "Competency")


def domain_scores_chart(
    domain_scores: list[dict[str, Any]] | None,
) -> alt.Chart | None:
    frame = build_score_frame(domain_scores, "domain")
    if frame.empty:
        return None
    return _score_bar_chart(frame, "Domain")
