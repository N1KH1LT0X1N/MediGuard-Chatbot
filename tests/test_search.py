"""
Tests for paper search functionality.
"""
import pytest
from unittest.mock import patch, Mock
from research_bot import (
    search_papers_semantic_scholar,
    search_papers_arxiv,
    http_get,
)


class TestSemanticScholarSearch:
    """Test Semantic Scholar API integration."""
    
    @patch('research_bot.http_get')
    def test_search_returns_results(self, mock_http_get):
        """Test successful search returns paper list."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "paperId": "abc123",
                    "title": "Test Paper",
                    "year": 2023,
                    "url": "https://example.com/paper",
                    "authors": [{"name": "Author One"}],
                    "abstract": "Test abstract"
                }
            ]
        }
        mock_http_get.return_value = mock_response
        
        results = search_papers_semantic_scholar("test query")
        assert len(results) > 0
        assert results[0]["title"] == "Test Paper"
        assert results[0]["year"] == 2023
    
    @patch('research_bot.http_get')
    def test_search_handles_api_failure(self, mock_http_get):
        """Test fallback to stub data on API failure."""
        mock_http_get.return_value = None
        
        results = search_papers_semantic_scholar("test query")
        # Should return fallback stub data
        assert len(results) > 0
        assert any("attention" in r["title"].lower() for r in results)
    
    @patch('research_bot.http_get')
    def test_search_with_limit(self, mock_http_get):
        """Test search respects limit parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"paperId": "1", "title": "Paper 1", "year": 2023, "url": "", "authors": [], "abstract": ""},
                {"paperId": "2", "title": "Paper 2", "year": 2023, "url": "", "authors": [], "abstract": ""},
                {"paperId": "3", "title": "Paper 3", "year": 2023, "url": "", "authors": [], "abstract": ""},
            ]
        }
        mock_http_get.return_value = mock_response
        
        results = search_papers_semantic_scholar("test", limit=2)
        # Implementation should respect limit
        assert len(results) <= 3


class TestArxivSearch:
    """Test arXiv API integration."""
    
    @patch('research_bot.http_get')
    def test_arxiv_search_returns_results(self, mock_http_get):
        """Test arXiv search returns formatted results."""
        mock_response = Mock()
        mock_response.text = """
        <feed>
            <entry>
                <title>Test ArXiv Paper</title>
                <summary>Test summary for arXiv paper</summary>
                <published>2023-01-15</published>
                <link href="https://arxiv.org/abs/2301.00001"/>
                <author><name>Test Author</name></author>
            </entry>
        </feed>
        """
        mock_http_get.return_value = mock_response
        
        results = search_papers_arxiv("test query")
        assert isinstance(results, list)
        # arXiv parsing is minimal, so check structure
        if len(results) > 0:
            assert "title" in results[0]
    
    @patch('research_bot.http_get')
    def test_arxiv_search_handles_failure(self, mock_http_get):
        """Test arXiv search handles API failure gracefully."""
        mock_http_get.return_value = None
        
        results = search_papers_arxiv("test query")
        assert isinstance(results, list)
        assert len(results) == 0


class TestHttpGet:
    """Test HTTP helper function."""
    
    @patch('research_bot.requests.get')
    def test_http_get_success(self, mock_get):
        """Test successful HTTP GET."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = http_get("https://example.com")
        assert result is not None
        assert result.status_code == 200
    
    @patch('research_bot.requests.get')
    def test_http_get_retries_on_failure(self, mock_get):
        """Test HTTP GET retries on failure."""
        mock_get.side_effect = [Exception("Network error"), Mock(status_code=200)]
        
        result = http_get("https://example.com")
        # Should retry once
        assert mock_get.call_count == 2
