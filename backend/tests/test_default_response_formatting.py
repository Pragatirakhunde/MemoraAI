from types import SimpleNamespace
from unittest.mock import Mock, patch

from langchain_core.messages import HumanMessage, SystemMessage

from app.services.llm_service import DEFAULT_ANSWER_FORMATTING, LLMService


def test_default_formatting_is_applied_without_user_request():
    fake_model = SimpleNamespace(
        invoke=Mock(return_value=SimpleNamespace(content="### Answer\n\n- Point"))
    )

    with patch("app.services.llm_service.settings", SimpleNamespace(GOOGLE_API_KEY="test-key")), patch(
        "app.services.llm_service.ChatGoogleGenerativeAI", return_value=fake_model
    ):
        service = LLMService()
        result = service.generate("What is PayFlow?")

    assert result == "### Answer\n\n- Point"
    messages = fake_model.invoke.call_args.args[0]
    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)
    assert "EVERY answer by default" in messages[0].content
    assert "not an instruction that depends on the user's wording" in messages[0].content
    assert messages[1].content == "What is PayFlow?"


def test_default_formatting_contract_has_simple_and_complex_answer_rules():
    assert "simple question" in DEFAULT_ANSWER_FORMATTING
    assert "meaningful Markdown headings" in DEFAULT_ANSWER_FORMATTING
    assert "fenced code blocks" in DEFAULT_ANSWER_FORMATTING
