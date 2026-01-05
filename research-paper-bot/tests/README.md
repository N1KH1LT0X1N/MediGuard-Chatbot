# Research-Paper-Chatbot Tests

This directory contains the test suite for the Research-Paper-Chatbot project.

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=research_bot --cov-report=html
```

View coverage report:
```bash
# On Windows
start htmlcov/index.html

# On macOS/Linux
open htmlcov/index.html
```

### Run Specific Test Files

```bash
pytest tests/test_bot_logic.py
pytest tests/test_api.py
pytest tests/test_search.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Tests Matching a Pattern

```bash
pytest -k "test_intent"
```

## Test Structure

- **`conftest.py`** - Shared fixtures and test configuration
- **`test_bot_logic.py`** - Unit tests for bot logic functions (intent detection, answer evaluation, etc.)
- **`test_api.py`** - Integration tests for Flask endpoints
- **`test_search.py`** - Tests for paper search functionality

## Writing Tests

### Example Test

```python
def test_detect_help_intent():
    """Test help intent detection."""
    assert detect_intent("help") == "help"
    assert detect_intent("I need help") == "help"
```

### Using Fixtures

```python
def test_with_mock_search(mock_search_results):
    """Test using mock search results."""
    results = search_papers_semantic_scholar("test")
    assert len(results) > 0
```

### Testing Flask Endpoints

```python
def test_endpoint(client):
    """Test Flask endpoint."""
    response = client.post('/whatsapp', data={'From': 'user', 'Body': 'help'})
    assert response.status_code == 200
```

## Mocking External APIs

Tests mock external API calls to:
- Avoid rate limits during testing
- Ensure consistent test results
- Speed up test execution
- Test error handling

Mocked services:
- Twilio WhatsApp API
- Groq API
- Semantic Scholar API
- arXiv API

## CI/CD Integration

Tests are designed to run in CI/CD pipelines (GitHub Actions, etc.):

```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pytest --cov=research_bot
```

## Test Coverage Goals

- **Unit tests**: >80% coverage
- **Integration tests**: All critical paths
- **API mocking**: All external services

## Troubleshooting

**Import errors**: Ensure `research_bot.py` is in the parent directory and dependencies are installed.

**Database errors**: Tests use temporary SQLite databases that are cleaned up automatically.

**Mock failures**: Check that mock patches match the actual function paths in `research_bot.py`.
