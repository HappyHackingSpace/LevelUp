# Contributing to LevelUP

Thank you for your interest in contributing to LevelUP! We welcome contributions of all kinds.

## Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🌟 Star the repository
- 📢 Share with others

## Development Setup

### Prerequisites

- Python 3.13+
- UV package manager
- Git

### Getting Started

1. **Fork the Repository**

   ```bash
   git clone https://github.com/HappyHackingSpace/LevelUp.git
   cd levelup
   ```

2. **Install Dependencies**

   ```bash
   uv sync
   ```

3. **Create a Development Environment**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run Tests**

   ```bash
   uv run pytest
   ```

## Code Style

We use the following tools for code quality:

- **Ruff**: Linting and formatting
- **Black**: Code formatting (via Ruff)
- **mypy**: Type checking
- **pytest**: Testing

### Running Linters

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type checking
uv run mypy levelup
```

## Pull Request Process

1. **Create a Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**

   - Write clear, concise code
   - Add tests for new features
   - Update documentation
   - Follow existing code style

3. **Commit Your Changes**

   ```bash
   git commit -m "Add: brief description of changes"
   ```

   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for documentation
   - `Refactor:` for code improvements

4. **Push and Open a PR**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Wait for Review**

   - All PRs require at least one approval
   - Address feedback promptly
   - Keep PRs focused and reasonably sized

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Aim for good test coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### Example Test

```python
def test_analyze_cv_success(client):
    # Arrange
    test_file = open("tests/fixtures/sample_cv.pdf", "rb")

    # Act
    response = client.post(
        "/api/v1/analyze",
        files={"file": test_file},
        data={"language": "English"}
    )

    # Assert
    assert response.status_code == 200
    assert "domain_scores" in response.json()
```

## Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Follow Google-style docstrings
- Include type hints

### Example

```python
def analyze_cv(text: str, language: str) -> dict:
    """Analyze CV text and generate insights.

    Args:
        text: Extracted CV text content
        language: Target language for report

    Returns:
        Dictionary containing analysis results

    Raises:
        ValueError: If text is empty
        APIError: If API request fails
    """
    ...
```

### Updating Documentation

When adding features:

1. Update relevant docs in `docs/`
2. Add examples if applicable
3. Update README if needed
4. Keep API docs in sync

## Project Structure

```
levelup/
├── levelup/
│   ├── api/          # API routes
│   ├── crud/         # Database operations
│   ├── database/     # DB configuration
│   ├── models/       # Data models
│   └── prompts/      # AI prompts
├── docs/             # Documentation
├── tests/            # Test suite
└── scripts/          # Utility scripts
```

## Issue Reporting

### Bug Reports

Include:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots if applicable

### Feature Requests

Include:

- Clear description of the feature
- Use case/justification
- Proposed implementation (if any)
- Examples

## Code of Conduct

Please read our [Code of Conduct](../CODE_OF_CONDUCT.md) before contributing.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

- Discord: [Happy Hacking Space](https://discord.gg/happyhackingspace)
- GitHub Discussions: [HappyHackingSpace/levelup](https://github.com/HappyHackingSpace/LevelUp/discussions)

Thank you for contributing! 🎉
