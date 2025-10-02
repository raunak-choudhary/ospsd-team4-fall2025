# Testing Strategy

This project follows a comprehensive testing strategy with three distinct test layers.

## Test Pyramid

```
         /\
        /E2\     End-to-End Tests (Subprocess execution)
       /____\
      /      \
     / Integ  \  Integration Tests (Real Gmail API)
    /__________\
   /            \
  /     Unit     \ Unit Tests (Mocked dependencies)
 /________________\
```

## Unit Tests

**Location**: `src/*/tests/`

**Purpose**: Test components in isolation with mocked dependencies

**Characteristics**:
- Fast execution (< 1 second total)
- No network calls
- Mock Gmail API responses
- Test data models and business logic

**Example**:

```python
from unittest.mock import patch
import email_api

def test_get_messages_with_limit():
    """Test message retrieval respects limit parameter."""
    with patch("gmail_impl.gmail_client.build") as mock_build:
        # Configure mock
        mock_service = mock_build.return_value
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        }

        # Test
        client = email_api.get_client()
        messages = list(client.get_messages(limit=2))

        assert len(messages) == 2
```

**Run**:

```bash
uv run pytest src/ -m unit
```

## Integration Tests

**Location**: `tests/integration/`

**Purpose**: Validate integration with real Gmail API

**Characteristics**:
- Real Gmail API calls
- OAuth2 authentication flow
- Token caching validation
- Cross-component contract testing
- Requires credentials.json

**What They Test**:
- Gmail API connectivity
- OAuth2 flow and token refresh
- Data serialization (Gmail API → Email objects)
- Error propagation across boundaries
- State management

**Example**:

```python
import email_api
import gmail_impl  # noqa: F401

@pytest.mark.integration
def test_oauth_token_reuse():
    """Verify OAuth token is cached and reused."""
    client = email_api.get_client()

    # First call creates token
    list(client.get_messages(limit=1))
    first_mtime = Path("token.json").stat().st_mtime

    # Second call reuses token
    list(client.get_messages(limit=1))
    second_mtime = Path("token.json").stat().st_mtime

    assert first_mtime == second_mtime
```

**Run**:

```bash
uv run pytest tests/integration/ -m integration
```

**Setup**: Requires Gmail API credentials in `credentials.json`

## E2E Tests

**Location**: `tests/e2e/`

**Purpose**: Test complete application execution as a user would

**Characteristics**:
- Execute `main.py` via subprocess
- Validate stdout output
- Test syntax, imports, file structure
- True process isolation
- Simulate real user interaction

**What They Test**:
- Application entry point works
- All imports resolve correctly
- Complete workflow execution
- Error handling at application level

**Example**:

```python
import subprocess
import sys

@pytest.mark.e2e
def test_main_script_runs_successfully():
    """Test that main.py executes successfully."""
    result = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    assert "Initializing email client..." in result.stdout
    assert "Demo complete!" in result.stdout
```

**Run**:

```bash
uv run pytest tests/e2e/ -m e2e
```

## Test Markers

Tests are marked with pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests

**Run specific types**:

```bash
# Unit only (fast, no credentials needed)
uv run pytest -m unit

# Integration only (requires credentials)
uv run pytest -m integration

# E2E only (requires credentials)
uv run pytest -m e2e

# All tests
uv run pytest
```

## Coverage Requirements

- **Overall**: 97% code coverage achieved
- **Unit tests**: 84% coverage (fast feedback during development)
- **Integration/E2E tests**: Additional 13% coverage (validates real API contracts and workflows)
- **Minimum threshold**: 80% for CI pipeline

## CI/CD Strategy

### Pull Requests (PR Check)

- Run: Unit tests + Linting + Type checking
- Fast feedback (< 2 minutes)
- No credentials required

### Main Branch (Full Suite)

- Run: All tests (unit + integration + e2e)
- Requires Gmail API credentials as secrets
- Comprehensive validation

## Best Practices

### Unit Tests

- Use `with patch()` for each test to maintain DI architecture
- Test one thing per test
- Use descriptive test names
- Avoid testing implementation details

### Integration Tests

- Use `email_api.get_client()` to respect DI pattern
- Test cross-component contracts
- Validate error propagation
- Avoid testing Gmail API internals

### E2E Tests

- Test complete workflows
- Validate stdout/stderr output
- Use subprocess execution
- Avoid testing internal implementation
