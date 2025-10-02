# Gmail Implementation Reference

The `gmail_impl` package provides a Gmail-based implementation of the email client interface.

## Module: `gmail_impl`

::: gmail_impl

## GmailClient

::: gmail_impl.GmailClient
    options:
      show_source: true
      members:
        - __init__
        - get_messages

## Features

### OAuth2 Authentication

GmailClient uses OAuth2 authentication with token caching:

1. **First Run**: Opens browser for user authorization
2. **Subsequent Runs**: Reuses cached token from `token.json`
3. **Token Refresh**: Automatically refreshes expired tokens

### Configuration

#### Default Paths

```python
# Default locations
credentials_file = "credentials.json"
token_file = "token.json"
```

#### Environment Variables

```python
# Override via environment
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
export GMAIL_TOKEN_PATH=/path/to/token.json
```

#### Direct Configuration

```python
from gmail_impl import GmailClient

client = GmailClient(
    credentials_file="/path/to/credentials.json",
    token_file="/path/to/token.json"
)
```

**Note**: Direct instantiation breaks dependency injection abstraction. Use environment variables for testing instead.

## Usage with Dependency Injection

```python
import email_api
import gmail_impl  # noqa: F401  # Performs DI injection

# Get client (returns GmailClient via DI)
client = email_api.get_client()

# Use the client
for email in client.get_messages(limit=10):
    print(f"From: {email.sender.address}")
    print(f"Subject: {email.subject}")
```

## Gmail API Setup

### 1. Create Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API

### 2. Create Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Application type: "Desktop app"
4. Download JSON as `credentials.json`

### 3. Configure OAuth Consent

1. Go to "OAuth consent screen"
2. User Type: "External"
3. Add test users (your Gmail address)
4. Scopes: `https://www.googleapis.com/auth/gmail.readonly`

### 4. Run Application

```bash
# First run - opens browser for auth
uv run python main.py

# Subsequent runs - uses token.json
uv run python main.py
```

## Implementation Details

### Message Parsing

GmailClient converts Gmail API responses to Email objects:

```python
# Gmail API format
{
    "id": "msg123",
    "payload": {
        "headers": [
            {"name": "Subject", "value": "Hello"},
            {"name": "From", "value": "John <john@example.com>"},
            ...
        ],
        "body": {"data": "base64_encoded_content"}
    }
}

# Converted to Email object
Email(
    id="msg123",
    subject="Hello",
    sender=EmailAddress(address="john@example.com", name="John"),
    ...
)
```

### HTML to Text Conversion

Email bodies are converted from HTML to plain text using html2text:

- Removes HTML tags
- Converts links to markdown format
- Preserves structure and readability

### Error Handling

**Authentication Errors**:

```python
try:
    client = email_api.get_client()
    emails = list(client.get_messages())
except RuntimeError as e:
    # OAuth2 failed, credentials invalid, etc.
    print(f"Authentication error: {e}")
```

**Connection Errors**:

```python
try:
    emails = list(client.get_messages())
except ConnectionError as e:
    # Network issues, Gmail API unavailable, etc.
    print(f"Connection error: {e}")
```

## Testing

### Unit Testing with Mocks

```python
from unittest.mock import patch
import email_api

def test_gmail_client():
    with patch("gmail_impl.gmail_client.build") as mock_build:
        # Configure mock Gmail service
        mock_service = mock_build.return_value
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "1"}]
        }

        # Test
        client = email_api.get_client()
        messages = list(client.get_messages(limit=1))
        assert len(messages) == 1
```

### Integration Testing

```python
import email_api
import gmail_impl  # noqa: F401

@pytest.mark.integration
def test_real_gmail():
    """Test with real Gmail API."""
    client = email_api.get_client()
    emails = list(client.get_messages(limit=1))
    assert isinstance(emails, list)
```

## Performance

- **Token Caching**: After first auth, no browser interaction needed
- **Lazy Evaluation**: Messages fetched on-demand via iterator
- **Pagination**: Handles large inboxes efficiently

## Security

- OAuth2 tokens stored in `token.json` (gitignored)
- Read-only Gmail API scope
- Credentials never logged or exposed
- Token refresh automatic and secure
