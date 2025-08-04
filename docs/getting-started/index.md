# Getting Started

Quick start guide for setting up and using the Email Client System.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud Console account (for Gmail implementation)

## Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd email-client

# Install all dependencies
uv sync --extra dev --extra email --extra gmail
```

### 2. Gmail Setup (Optional)

If you want to use the Gmail implementation:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials for a desktop application
5. Download the credentials JSON file as `credentials.json`

## Quick Start

### Using the Interface

```python
from email_api import EmailClient, Email, EmailAddress

async def process_emails(client: EmailClient) -> None:
    """Process emails using dependency injection."""
    async with client:
        emails = await client.list_inbox_messages(limit=5)
        for email in emails:
            print(f"From: {email.sender.email}")
            print(f"Subject: {email.subject}")
```

### Gmail Implementation

```python
import asyncio
from gmail_impl import GmailClient, GmailConfig

async def main():
    config = GmailConfig(
        credentials_file="credentials.json",
        token_file="token.json"
    )
    
    async with GmailClient(config) as client:
        emails = await client.list_inbox_messages(limit=5)
        print(f"Found {len(emails)} emails")

asyncio.run(main())
```

## Development

### Running Tests

```bash
# All tests
uv run pytest

# Component-specific tests
uv run pytest src/email_api/tests/
uv run pytest src/gmail_impl/tests/
```

### Code Quality

```bash
# Type checking
uv run mypy .

# Linting
uv run ruff check .

# Coverage report
uv run pytest --cov=src --cov-report=html
```

### Documentation

```bash
# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build
```

## Next Steps

- Check out the [API Reference](../reference/interfaces.md) for detailed interface documentation
- Explore the [Gmail Implementation](../reference/gmail-client.md) for specific Gmail features
- Review the component guidelines in `src/component.md` 