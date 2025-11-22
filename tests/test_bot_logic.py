"""
Unit tests for bot logic functions.
"""
import pytest
from research_bot import (
    detect_intent,
    is_qna_start,
    extract_query_from_text,
    evaluate_answer,
    capabilities_message,
    help_message,
)


class TestIntentDetection:
    """Test intent detection functionality."""
    
    def test_detect_qna_start(self):
        """Test Q&A start intent detection."""
        assert detect_intent("ready for Q&A") == "qna_start"
        assert detect_intent("let's do qna") == "qna_start"
        assert detect_intent("start qna") == "qna_start"
    
    def test_detect_help(self):
        """Test help intent detection."""
        assert detect_intent("help") == "help"
        assert detect_intent("I need help") == "help"
    
    def test_detect_status(self):
        """Test status intent detection."""
        assert detect_intent("status") == "status"
        assert detect_intent("where am I") == "status"
    
    def test_detect_reset(self):
        """Test reset intent detection."""
        assert detect_intent("reset") == "reset"
        assert detect_intent("clear session") == "reset"
    
    def test_detect_paper_search(self):
        """Test paper search intent detection."""
        assert detect_intent("transformer attention mechanisms") == "paper"
        assert detect_intent("https://arxiv.org/abs/1706.03762") == "paper"
        assert detect_intent("10.48550/arXiv.1706.03762") == "paper"
    
    def test_detect_ambiguous(self):
        """Test ambiguous intent detection."""
        assert detect_intent("hi") == "ambiguous"
        assert detect_intent("ok") == "ambiguous"


class TestQueryExtraction:
    """Test query extraction from user text."""
    
    def test_extract_arxiv_url(self):
        """Test arXiv URL extraction."""
        text = "Check this paper: https://arxiv.org/abs/1706.03762"
        query = extract_query_from_text(text)
        assert "1706.03762" in query
    
    def test_extract_doi(self):
        """Test DOI extraction."""
        text = "Look at https://doi.org/10.48550/arXiv.1706.03762"
        query = extract_query_from_text(text)
        assert "10.48550" in query
    
    def test_extract_plain_text(self):
        """Test plain text query."""
        text = "transformer attention mechanisms"
        query = extract_query_from_text(text)
        assert query == text


class TestAnswerEvaluation:
    """Test Q&A answer evaluation."""
    
    def test_evaluate_good_answer(self):
        """Test evaluation of good answer."""
        keywords = ["transformer", "attention", "mechanism"]
        user_answer = "The transformer uses an attention mechanism"
        score, feedback = evaluate_answer(user_answer, keywords)
        assert score >= 2
        assert "great" in feedback.lower() or "covered" in feedback.lower()
    
    def test_evaluate_poor_answer(self):
        """Test evaluation of insufficient answer."""
        keywords = ["transformer", "attention", "mechanism"]
        user_answer = "I don't know"
        score, feedback = evaluate_answer(user_answer, keywords)
        assert score == 0
        assert "try" in feedback.lower() or "consider" in feedback.lower()
    
    def test_evaluate_no_keywords(self):
        """Test evaluation with no keywords."""
        keywords = []
        user_answer = "Some answer"
        score, feedback = evaluate_answer(user_answer, keywords)
        assert score == 1
        assert "thanks" in feedback.lower()


class TestMessageGeneration:
    """Test message generation functions."""
    
    def test_capabilities_message(self):
        """Test capabilities message generation."""
        msg = capabilities_message()
        assert len(msg) > 0
        assert "help" in msg.lower() or "find" in msg.lower()
    
    def test_help_message(self):
        """Test help message generation."""
        msg = help_message()
        assert len(msg) > 0
        assert "command" in msg.lower()
