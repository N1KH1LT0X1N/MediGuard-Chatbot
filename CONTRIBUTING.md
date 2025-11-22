# Contributing to Research-Paper-Chatbot

First off, thank you for considering contributing to Research-Paper-Chatbot! 🎉

The following is a set of guidelines for contributing to this project. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
  - [Git Commit Messages](#git-commit-messages)
  - [Python Style Guide](#python-style-guide)
- [Testing](#testing)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, screenshots, etc.)
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (OS, Python version, dependency versions)

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when creating issues.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) when creating issues.

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes** following our style guidelines
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes** (`pytest`)
5. **Update documentation** if you've changed functionality
6. **Write a clear commit message** following our guidelines
7. **Submit a pull request** using our template

## Development Setup

1. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Research-Paper-Chatbot.git
   cd Research-Paper-Chatbot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the app:**
   ```bash
   python research_bot.py
   ```

6. **Run tests:**
   ```bash
   pytest
   ```

## Style Guidelines

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- Consider starting the commit message with an applicable emoji:
  - 🎨 `:art:` - Improve structure/format of the code
  - ⚡️ `:zap:` - Improve performance
  - 🔥 `:fire:` - Remove code or files
  - 🐛 `:bug:` - Fix a bug
  - ✨ `:sparkles:` - Introduce new features
  - 📝 `:memo:` - Add or update documentation
  - 🚀 `:rocket:` - Deploy stuff
  - ✅ `:white_check_mark:` - Add or update tests
  - 🔒 `:lock:` - Fix security issues
  - ⬆️ `:arrow_up:` - Upgrade dependencies
  - ⬇️ `:arrow_down:` - Downgrade dependencies
  - 🔧 `:wrench:` - Add or update configuration files

**Example:**
```
✨ Add multi-document comparison feature

- Implement document comparison logic
- Add new API endpoint /compare
- Update UI to support comparison view

Closes #123
```

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for code formatting (line length: 100)
- Use [flake8](https://flake8.pycqa.org/) for linting
- Use type hints where possible
- Write docstrings for all functions, classes, and modules

**Format your code:**
```bash
black research_bot.py --line-length 100
flake8 research_bot.py --max-line-length 100
```

**Example function:**
```python
def search_papers(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Search for research papers using Semantic Scholar API.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of paper dictionaries with title, authors, abstract, etc.
        
    Raises:
        ValueError: If query is empty or limit is invalid
    """
    if not query.strip():
        raise ValueError("Query cannot be empty")
    # Implementation...
```

## Testing

- Write tests for new functionality
- Ensure all tests pass before submitting PR
- Aim for meaningful test coverage (not just 100%)
- Use pytest fixtures for common setup
- Mock external API calls (Twilio, Gemini, Semantic Scholar)

**Test structure:**
```python
# tests/test_search.py
import pytest
from research_bot import search_papers_semantic_scholar

def test_search_papers_valid_query():
    results = search_papers_semantic_scholar("transformer", limit=1)
    assert len(results) > 0
    assert "title" in results[0]
    assert "authors" in results[0]

def test_search_papers_empty_query():
    results = search_papers_semantic_scholar("", limit=3)
    assert isinstance(results, list)
```

**Run tests with coverage:**
```bash
pytest --cov=research_bot --cov-report=html
```

## Project Structure

When adding new features, follow the existing structure:

```
research_bot.py              # Main application
├── Config & Initialization  # Environment setup, API clients
├── Database helpers         # SQLite operations
├── External APIs            # Paper search functions
├── AI helpers              # Gemini integration
├── Bot logic               # Intent detection, handlers
└── Flask routes            # Webhook endpoints
```

## Questions?

Feel free to open an issue with the label `question` or reach out to the maintainers.

## Recognition

Contributors will be recognized in our README and release notes. Thank you for helping make Research-Paper-Chatbot better! 🙏
