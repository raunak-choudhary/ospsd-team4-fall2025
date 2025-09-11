# Email API Interface Component

Protocol-based email client interface for dependency injection and modular architecture.

## Overview

The `email-api` component provides type-safe interfaces for email client implementations. It defines contracts without implementation details, enabling dependency injection and testable architectures.

## Features

- **Protocol-Based Design**: Uses `typing.Protocol` for flexible implementation contracts
- **Async-First**: Built for modern async Python applications
- **Type Safety**: Full mypy strict mode compliance
- **Immutable Data Models**: Thread-safe dataclass-based email and address models
- **Zero Dependencies**: Pure interface definitions

## Installation

```bash
# From workspace root
uv sync --extra email

# With development dependencies
uv sync --extra dev --extra email
```

## Usage

### Basic Interface

```python
from email_api import EmailClient, Email, EmailAddress

async def my_email_processor(client: EmailClient) -> None:
    """Process emails using injected client implementation."""
    async with client:
        emails = await client.list_inbox_messages(limit=10)
        for email in emails:
            if email.has_content:
                content = email.get_content()
                print(f"From: {email.sender.email}")
                print(f"Subject: {email.subject}")
                print(f"Content: {content[:100]}...")
```

### Data Models

```python
from email_api import Email, EmailAddress
from datetime import datetime, timezone

# Email addresses
sender = EmailAddress(email="user@example.com", name="User Name")

# Email objects
email = Email(
    id="msg_123",
    subject="Important Message",
    sender=sender,
    recipients=[EmailAddress(email="recipient@example.com")],
    body_text="Plain text content",
    body_html="<p>HTML content</p>",
    timestamp=datetime.now(timezone.utc),
    is_read=False
)

# Check content availability
if email.has_content:
    content = email.get_content()  # Prefers text over HTML
```

### Exception Handling

```python
from email_api import EmailError, EmailConnectionError, EmailAuthenticationError

try:
    emails = await client.list_inbox_messages()
except EmailAuthenticationError as e:
    print(f"Authentication failed: {e}")
except EmailConnectionError as e:
    print(f"Connection error: {e}")
except EmailError as e:
    print(f"General email error: {e}")
```

## Interface Contract

```python
class EmailClient(Protocol):
    async def list_inbox_messages(self, limit: int = 10) -> list[Email]:
        """List recent inbox messages."""
        ...
    
    async def get_email_content(self, email_id: str) -> Email:
        """Retrieve full email content by ID."""
        ...
    
    async def close(self) -> None:
        """Clean up resources and close connections."""
        ...
    
    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        ...
```

## Testing

```bash
# Run component tests
uv run pytest src/email_api/tests/

# With coverage
uv run pytest src/email_api/tests/ --cov=src/email_api/src/email_api

# Type checking
uv run mypy src/email_api/

# Linting
uv run ruff check src/email_api/
```

## Quality Standards

- **Comprehensive Test Coverage**: Extensive unit test suite
- **Strict Type Checking**: Full mypy strict mode compliance  
- **Clean Code**: All ruff rules enabled with documented exceptions
- **Async Context Management**: Proper resource handling patterns
- **Immutable Data**: Thread-safe, predictable data models

---

**Component**: Email API Interface  
**License**: MIT
