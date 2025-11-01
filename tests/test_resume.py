import io
import os
import sys
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from levelup.app import (
    analyzecv_pdf_withllm,
    display_analysis_results,
    display_comparative_benchmarking,
    display_competency_scores,
    display_development_recommendations,
    display_domain_scores,
    display_language_info,
    display_overall_summary,
    display_strategic_insights,
    extract_text_from_pdf,
)


def test_extract_text_from_pdf(mocker: MockerFixture) -> None:
    """Test extract_text_from_pdf function."""
    mock_reader = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "test"
    mock_reader.pages = [mock_page]

    mocker.patch("levelup.app.pypdf.PdfReader", return_value=mock_reader)

    assert extract_text_from_pdf(io.BytesIO(b"test")) == "test"


def test_analyzecv_pdf_withllm_success(mocker: MockerFixture) -> None:
    """Test successful analysis of a CV."""
    mock_response = MagicMock()
    mock_response.text = '{"language":"English","domain_scores":[{"domain":"IT","score":90,"justification":"Strong technical background"}]}'

    mocker.patch("levelup.app.get_resume_analysis_prompt", return_value="mocked prompt")
    mocker.patch("levelup.app.Model.generate_content", return_value=mock_response)

    result = analyzecv_pdf_withllm("Sample resume text", "English")

    assert result is not None
    assert result["language"] == "English"
    assert len(result["domain_scores"]) == 1
    assert result["domain_scores"][0]["domain"] == "IT"


def test_analyzecv_pdf_withllm_failure(mocker: MockerFixture) -> None:
    """Test handling of failure scenarios in analysis."""
    mock_response_no_json = MagicMock()
    mock_response_no_json.text = "No JSON here"

    mocker.patch("levelup.app.get_resume_analysis_prompt", return_value="mocked prompt")
    mocker.patch(
        "levelup.app.Model.generate_content", return_value=mock_response_no_json
    )
    mocker.patch("levelup.app.st.error")

    result = analyzecv_pdf_withllm("Sample resume text", "English")
    assert result is None

    mocker.patch(
        "levelup.app.Model.generate_content", side_effect=Exception("API Error")
    )
    result = analyzecv_pdf_withllm("Sample resume text", "English")
    assert result is None


def test_display_language_info(mocker: MockerFixture) -> None:
    """Test display of language information."""
    mock_st = mocker.patch("levelup.app.st")

    test_result = {"language": "Spanish"}
    display_language_info(test_result)

    mock_st.subheader.assert_called_once_with("Detected Language")
    mock_st.write.assert_called_once_with("Spanish")

    mock_st.reset_mock()
    display_language_info({})
    mock_st.write.assert_called_once_with("Not detected")


def test_display_domain_scores(mocker: MockerFixture) -> None:
    """Test display of domain scores."""
    mock_st = mocker.patch("levelup.app.st")

    test_result = {
        "domain_scores": [
            {"domain": "IT", "score": 90, "justification": "Good skills"},
            {"domain": "Management", "score": 80, "justification": "Some experience"},
        ]
    }

    display_domain_scores(test_result)

    mock_st.subheader.assert_called_once_with("Career Domain Fit Scores")
    mock_st.table.assert_called_once()

    mock_st.reset_mock()
    display_domain_scores({})
    mock_st.subheader.assert_called_once()
    mock_st.table.assert_not_called()


def test_display_competency_scores(mocker: MockerFixture) -> None:
    """Test display of competency scores."""
    mock_st = mocker.patch("levelup.app.st")

    test_result = {
        "competency_scores": [
            {
                "category": "Technical",
                "score": 90,
                "strength": "Good coding",
                "observation": "None",
            },
            {
                "category": "Communication",
                "score": 80,
                "strength": "Clear writing",
                "observation": "Needs work",
            },
        ]
    }

    display_competency_scores(test_result)

    mock_st.subheader.assert_called_once_with("Competency Evaluation")
    mock_st.table.assert_called_once()

    mock_st.reset_mock()
    display_competency_scores({})
    mock_st.table.assert_not_called()


def test_display_strategic_insights(mocker: MockerFixture) -> None:
    """Test display of strategic insights."""
    mock_st = mocker.patch("levelup.app.st")

    test_result = {"strategic_insights": "This candidate has potential"}
    display_strategic_insights(test_result)

    mock_st.subheader.assert_called_once_with("Strategic Insights")
    mock_st.write.assert_called_once_with("This candidate has potential")

    mock_st.reset_mock()
    display_strategic_insights({})
    mock_st.write.assert_called_once_with("N/A")


def test_display_development_recommendations(mocker: MockerFixture) -> None:
    """Test display of development recommendations."""
    mock_st = mocker.patch("levelup.app.st")

    test_result = {
        "development_recommendations": [
            "Learn more programming languages",
            "Improve communication skills",
        ]
    }

    display_development_recommendations(test_result)

    mock_st.subheader.assert_called_once_with("Development Recommendations")
    assert mock_st.markdown.call_count == 2
    mock_st.markdown.assert_any_call("- Learn more programming languages")

    mock_st.reset_mock()
    display_development_recommendations({})
    mock_st.subheader.assert_called_once()
    mock_st.markdown.assert_not_called()


def test_display_comparative_benchmarking(mocker: MockerFixture) -> None:
    """Test display of comparative benchmarking."""
    mock_st = mocker.patch("levelup.app.st")

    test_result = {"comparative_benchmarking": "Above average in the field"}
    display_comparative_benchmarking(test_result)

    mock_st.subheader.assert_called_once_with("Comparative Benchmarking")
    mock_st.write.assert_called_once_with("Above average in the field")

    mock_st.reset_mock()
    display_comparative_benchmarking({})
    mock_st.write.assert_called_once_with("N/A")


def test_display_overall_summary(mocker: MockerFixture) -> None:
    """Test display of overall summary."""
    mock_st = mocker.patch("levelup.app.st")

    test_result = {
        "overall_summary": {
            "overall_score": 85,
            "key_strengths": ["Technical knowledge", "Problem solving"],
            "areas_to_improve": ["Communication"],
            "talent_potential": "High",
        }
    }

    display_overall_summary(test_result)

    mock_st.subheader.assert_called_once_with("Overall Summary")
    mock_st.markdown.assert_any_call("**Overall Score:** 85/100")
    mock_st.markdown.assert_any_call("**Key Strengths:**")
    mock_st.markdown.assert_any_call("- Technical knowledge")
    mock_st.markdown.assert_any_call("- Problem solving")
    mock_st.markdown.assert_any_call("**Areas to Improve:**")
    mock_st.markdown.assert_any_call("- Communication")
    mock_st.markdown.assert_any_call("**Talent Potential:** High")

    mock_st.reset_mock()
    display_overall_summary({})
    mock_st.markdown.assert_any_call("**Overall Score:** N/A/100")


def test_display_analysis_results(mocker: MockerFixture) -> None:
    """Test the orchestrator function that displays all results."""
    mock_language = mocker.patch("levelup.app.display_language_info")
    mock_domain = mocker.patch("levelup.app.display_domain_scores")
    mock_competency = mocker.patch("levelup.app.display_competency_scores")
    mock_insights = mocker.patch("levelup.app.display_strategic_insights")
    mock_recommendations = mocker.patch(
        "levelup.app.display_development_recommendations"
    )
    mock_benchmarking = mocker.patch("levelup.app.display_comparative_benchmarking")
    mock_summary = mocker.patch("levelup.app.display_overall_summary")

    test_result = {"dummy": "data"}
    display_analysis_results(test_result)

    mock_language.assert_called_once_with(test_result)
    mock_domain.assert_called_once_with(test_result)
    mock_competency.assert_called_once_with(test_result)
    mock_insights.assert_called_once_with(test_result)
    mock_recommendations.assert_called_once_with(test_result)
    mock_benchmarking.assert_called_once_with(test_result)
    mock_summary.assert_called_once_with(test_result)
