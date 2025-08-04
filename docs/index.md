# OSPSD - Email Client - TA Assignment Solution

Professional email client implementation using component-based architecture, dependency injection patterns, and modern Python development practices.

## Overview

A modular email client implementing clean architecture principles and interface design patterns. Built with professional software development standards including comprehensive testing, type safety, and maintainable code structure.

## Architecture

Component-based system where each component:
- Defines clear contracts using Python protocols
- Maintains zero dependencies between interface and implementation
- Can be independently developed, tested, and published
- Hides complex functionality behind simple interfaces

### Components

- **email_api**: Core interface component defining email client contracts and data models
- **gmail_impl**: Gmail implementation component providing OAuth2-authenticated email access

## Project Structure

```
email-client/
├── src/
│   ├── email_api/              # Interface component
│   ├── gmail_impl/             # Gmail implementation component
│   └── component.md            # Component development guidelines
├── tests/                      # Integration/E2E tests
├── pyproject.toml              # Workspace configuration
└── main.py                     # Project entry point
```

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
git clone <repository-url>
cd email-client-system

# Full development setup
uv sync --extra dev --extra email --extra gmail
```

### Development

```bash
# Run all tests
uv run pytest

# Component-specific tests
uv run pytest src/email_api/tests/
uv run pytest src/gmail_impl/tests/

# Type checking
uv run mypy src/

# Code quality
uv run ruff check .

# Coverage
uv run pytest --cov=src --cov-report=html

# Documentation
uv run mkdocs serve  # Live preview at http://127.0.0.1:8000
uv run mkdocs build  # Build static site

# Demo
uv run python main.py
```

## Usage

```python
from email_api import EmailClient, Email, EmailAddress

async def process_emails(client: EmailClient) -> None:
    """Dependency injection pattern - implementation provided externally."""
    async with client:
        emails = await client.list_inbox_messages(limit=5)
        for email in emails:
            if email.has_content:
                print(f"From: {email.sender.display_name}")
                print(f"Subject: {email.subject}")
```

## Quality Standards

- **Type Safety**: Full mypy strict mode compliance
- **Code Quality**: All ruff rules enabled with documented exceptions
- **Test Coverage**: ≥85% coverage requirement
- **Professional Standards**: Clean, maintainable, production-ready code

## Technology Stack

- **Language**: Python 3.12+
- **Package Management**: uv
- **Testing**: pytest with asyncio and coverage
- **Type Checking**: mypy (strict mode)
- **Code Quality**: ruff
- **Architecture**: Component-based with dependency injection

## License

MIT License - See LICENSE file for details. 