# Email Client with Dependency Injection

[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](./htmlcov/index.html)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

Email client implementation demonstrating component-based architecture, dependency injection, and interface design principles.

## Architecture

### Component-Based Design

The project is structured as a workspace with independent components:

- **email_api**: Interface component defining contracts using Abstract Base Classes
- **gmail_impl**: Gmail implementation with OAuth2 authentication

Each component can be independently developed, tested, and published.

### Dependency Injection Pattern

This project uses **dependency injection** for simplicity and testability:

#### 1. API Package (`email_api`)

Defines the interface and a stub `get_client()` function:

```python
# email_api/client.py
def get_client() -> Client:
    """Return an instance of a Mail Client."""
    raise NotImplementedError
```

#### 2. Implementation Package (`gmail_impl`)

Directly replaces the API's `get_client()` function when imported:

```python
# gmail_impl/__init__.py
import email_api
from gmail_impl.gmail_client import GmailClient

# Dependency injection: Replace get_client with our implementation
email_api.get_client = lambda: GmailClient()
```

#### 3. Application Usage

Your code depends only on the API interface:

```python
import email_api
import gmail_impl  # noqa: F401  # Import injects the implementation

# Get client (returns GmailClient because we imported gmail_impl)
client = email_api.get_client()

for email in client.get_messages(limit=10):
    print(f"From: {email.sender.address}")
    print(f"Subject: {email.subject}")
```

## Project Structure

```
ospsd-ta-task/
├── src/
│   ├── email_api/              # Interface component
│   │   ├── src/email_api/
│   │   │   ├── __init__.py
│   │   │   └── client.py       # Client, Email, EmailAddress
│   │   ├── tests/              # Unit tests
│   │   └── pyproject.toml
│   └── gmail_impl/             # Gmail implementation
│       ├── src/gmail_impl/
│       │   ├── __init__.py     # Performs DI injection
│       │   └── gmail_client.py # GmailClient implementation
│       ├── tests/              # Unit tests
│       └── pyproject.toml
├── tests/                      # Integration and E2E tests
│   ├── integration/            # Real Gmail API tests
│   └── e2e/                    # Subprocess execution tests
├── main.py                     # Demo application
└── pyproject.toml              # Workspace configuration
```

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Gmail API credentials (for integration/E2E tests)

### Installation

```bash
git clone <repository-url>
cd ospsd-ta-task

# Install dependencies
uv sync --extra dev --extra email --extra gmail
```

### Gmail API Setup

For local development and testing:

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials as `credentials.json` in project root
5. Run the demo app to authenticate: `uv run python main.py`
6. A `token.json` file will be created after OAuth flow

**Note**: Both `credentials.json` and `token.json` are gitignored for security.

For detailed setup instructions, see [Getting Started Guide](docs/getting-started/index.md).

## Development

### Quick Start Commands

```bash
# Run unit tests (NO credentials needed)
uv run pytest src/email_api/tests/ src/gmail_impl/tests/ \
  --cov=src/email_api/src/email_api \
  --cov=src/gmail_impl/src/gmail_impl \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=80

# Run all tests with coverage (includes integration + e2e)
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Type checking (strict mode)
uv run mypy .

# Code quality (all rules enabled)
uv run ruff check . --select ALL
uv run ruff format .

# Run demo application
uv run python main.py
```

### Test Types

```bash
# Unit tests only (fast, mocked, no credentials)
uv run pytest src/email_api/tests/ src/gmail_impl/tests/

# Integration tests (real Gmail API, requires credentials.json)
uv run pytest tests/integration/ -v

# E2E tests (subprocess execution, requires credentials.json)
uv run pytest tests/e2e/ -v

# Run with markers
uv run pytest -m unit           # Unit tests only
uv run pytest -m integration    # Integration tests
uv run pytest -m e2e            # E2E tests
```

## Testing Strategy

This project achieves 97% coverage with a three-tier testing approach:

### Unit Tests (`src/*/tests/`)
- Test data models and business logic in isolation
- No credentials required
- Mock authentication and Gmail API
- Fast execution

### Integration Tests (`tests/integration/`)
- Requires credentials.json
- Validates OAuth2 flow and token management
- Tests actual Gmail API interactions
- Uses `email_api.get_client()` to respect DI pattern

### E2E Tests (`tests/e2e/`)
- Executes `main.py` via subprocess
- Validates complete user workflows
- Tests application structure and integration


## Testing Pattern

Replace `get_client()` for testing:

```python
import email_api
from unittest.mock import Mock

# Inject mock client
mock_client = Mock(spec=email_api.Client)
email_api.get_client = lambda: mock_client

# Test your code
client = email_api.get_client()
assert client is mock_client
```

## Quality Standards

### Static Analysis
- Type checking with mypy strict mode
- Linting with ruff (all rules enabled)
- Consistent formatting with ruff format
- Minimal exceptions (documented with rationale)

### Testing
- 97% test coverage across unit, integration, and E2E tests
- 51 tests total (32 unit + 19 integration/E2E)
- Unit tests provide 84% coverage (mocked)
- Integration/E2E tests bring total to 97%
- Reproducible, deterministic test suite
- Fast unit tests for rapid feedback

### Code Quality
- Zero linter violations
- Zero type errors
- All tests passing
- Documented exceptions with clear reasoning

See [Design Philosophy](docs/architecture/design-philosophy.md) for design principles.

## CI/CD Configuration

This project uses CircleCI for continuous integration. If you fork this repository:

### Environment Variables Required

Configure these in CircleCI project settings under Environment Variables:

- `GMAIL_CREDENTIALS_JSON` - Content of your `credentials.json` file
- `GMAIL_CI_TOKEN_JSON` - Pre-authenticated token for integration and E2E tests

See [Getting Started - CI/CD Setup](docs/getting-started/index.md#cicd-setup-circleci) for detailed instructions.

### Workflow Branches

- PR branches: Unit tests and linting only (no credentials needed)
- Main/develop branches: Full test suite including unit, integration, and E2E tests
- Feature branches with `gmail` or `integration`: Full test suite


## Technology Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **Language** | Python 3.12+ | Modern Python with type hints |
| **Package Manager** | uv | Fast, reliable dependency management |
| **Testing** | pytest + pytest-cov | Comprehensive test framework |
| **Type Checking** | mypy | Strict static type analysis |
| **Linting** | ruff | Fast Python linter (all rules) |
| **Formatting** | ruff format | Consistent code style |
| **CI/CD** | CircleCI | Automated testing and deployment |
| **Documentation** | MkDocs + Material | Professional documentation |
| **Architecture** | Component-based | dependency injection |

## Documentation

- **[Design Philosophy](docs/architecture/design-philosophy.md)**: Deep Classes and interface design
- **[Dependency Injection](docs/architecture/dependency-injection.md)**: How DI works in this project
- **[Testing Strategy](docs/architecture/testing.md)**: Comprehensive testing approach
- **[API Reference](docs/reference/)**: Component APIs and usage examples

Build and serve documentation locally:
```bash
uv run mkdocs serve
```
Open http://127.0.0.1:8000 in your browser.

## Design Principles

This project demonstrates **Deep Interfaces** from [A Philosophy of Software Design](https://web.stanford.edu/~ouster/cgi-bin/book.php):

```
┌─────────────────────────┐
│  Small, Simple Interface│  ← Low Cost (easy to use)
├─────────────────────────┤
│   Substantial           │  ← High Benefit (lots of functionality)
│   Functionality         │
└─────────────────────────┘
```


## License

MIT License - See LICENSE file for details.
