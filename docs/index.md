# Email Client with Dependency Injection

Professional email client demonstrating component-based architecture and dependency injection patterns.

## Overview

This project implements a modular email client with clean separation between interface and implementation. It showcases professional software development practices including type safety, comprehensive testing, and maintainable architecture.

## Key Features

- Component-based architecture with independent packages
- Dependency injection using monkey-patching
- Full type safety with mypy strict mode
- 97% test coverage across unit, integration, and E2E tests
- OAuth2 authentication with Gmail API

## Quick Example

```python
import email_api
import gmail_impl  # noqa: F401

client = email_api.get_client()
for email in client.get_messages(limit=5):
    print(f"{email.sender.address}: {email.subject}")
```

## Documentation

### Getting Started
- [Installation and Setup](getting-started/index.md) - Install dependencies and configure Gmail API
- [Basic Usage](getting-started/index.md#quick-start) - Run the demo application

### Architecture
- [Design Philosophy](architecture/design-philosophy.md) - Deep interfaces and abstraction principles
- [Dependency Injection](architecture/dependency-injection.md) - How DI works in this project
- [Testing Strategy](architecture/testing.md) - Unit, integration, and E2E testing approach

### API Reference
- [Email API](reference/email-api.md) - Interface definitions and data models
- [Gmail Implementation](reference/gmail-impl.md) - OAuth2, message parsing, error handling

## Technology Stack

- Python 3.12+ with strict type checking
- uv for dependency management
- pytest with 97% coverage
- mypy strict mode
- ruff linting
- mkdocs-material documentation

## Development

```bash
# Install and run
uv sync --extra dev --extra email --extra gmail
uv run python main.py

# Test and validate
uv run pytest                # All tests
uv run mypy src/            # Type checking
uv run ruff check .         # Linting
```

## License

MIT License
