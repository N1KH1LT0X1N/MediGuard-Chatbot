"""
Pytest configuration and shared fixtures.
"""
import os
import pytest
import tempfile
from research_bot import app, init_db, get_db_connection


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    
    # Use a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def mock_gemini_response(monkeypatch):
    """Mock Gemini API responses."""
    def mock_generate(*args, **kwargs):
        return "This is a mock AI response for testing purposes."
    
    monkeypatch.setattr("research_bot.gemini_generate_text", mock_generate)


@pytest.fixture
def mock_search_results(monkeypatch):
    """Mock paper search API results."""
    def mock_search(*args, **kwargs):
        return [
            {
                "paperId": "test1",
                "title": "Test Paper on Transformers",
                "year": 2023,
                "url": "https://example.com/paper1",
                "authors": "Test Author et al.",
                "abstract": "This is a test abstract about transformers and attention mechanisms.",
            }
        ]
    
    monkeypatch.setattr("research_bot.search_papers_semantic_scholar", mock_search)
    monkeypatch.setattr("research_bot.search_papers_arxiv", mock_search)


@pytest.fixture
def sample_user_id():
    """Sample WhatsApp user ID for testing."""
    return "whatsapp:+1234567890"


@pytest.fixture
def sample_paper():
    """Sample paper data for testing."""
    return {
        "paperId": "sample123",
        "title": "Attention Is All You Need",
        "year": 2017,
        "url": "https://arxiv.org/abs/1706.03762",
        "authors": "Vaswani et al.",
        "abstract": (
            "The dominant sequence transduction models are based on complex recurrent "
            "or convolutional neural networks that include an encoder and a decoder. "
            "The best performing models also connect the encoder and decoder through "
            "an attention mechanism. We propose a new simple network architecture, "
            "the Transformer, based solely on attention mechanisms."
        ),
    }
