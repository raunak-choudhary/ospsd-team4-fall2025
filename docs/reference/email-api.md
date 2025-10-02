# Email API Reference

The `email_api` package provides the interface contract for email clients.

## Module: `email_api`

::: email_api

## Client Interface

::: email_api.Client
    options:
      show_source: true
      members:
        - get_messages

## Data Models

### Email

::: email_api.Email
    options:
      show_source: true

### EmailAddress

::: email_api.EmailAddress
    options:
      show_source: true
      members:
        - __str__

## Dependency Injection

### get_client

::: email_api.get_client
    options:
      show_source: true

## Usage Example

```python
import email_api
import gmail_impl  # noqa: F401  # Import injects implementation

# Get client via dependency injection
client = email_api.get_client()

# Fetch messages
for email in client.get_messages(limit=10):
    print(f"From: {email.sender.address}")
    print(f"Subject: {email.subject}")
    print(f"Date: {email.date_sent}")

    # Access body content
    if email.body:
        preview = email.body[:100]
        print(f"Preview: {preview}...")

    # Access recipients
    for recipient in email.recipients:
        print(f"To: {recipient.address}")
```

## Data Model Details

### EmailAddress

Represents an email address with optional display name.

**Attributes**:

- `address` (str): Email address (e.g., "user@example.com")
- `name` (str | None): Optional display name

**String Representation**:

- With name: `"John Doe <user@example.com>"`
- Without name: `"user@example.com"`

### Email

Represents a complete email message.

**Attributes**:

- `id` (str): Unique message identifier
- `subject` (str): Email subject (may be empty string)
- `sender` (EmailAddress): Email sender
- `recipients` (list[EmailAddress]): List of recipients
- `date_sent` (datetime): When email was sent
- `date_received` (datetime): When email was received
- `body` (str): Email body content (plain text)

**Notes**:

- All dates are timezone-aware
- Body is converted from HTML to plain text if needed
- Recipients list may be empty
- Subject is never None (empty string if missing)

## Client Interface

### get_messages

```python
def get_messages(self, *, limit: int | None = None) -> Iterator[Email]
```

Returns an iterator of emails from the inbox.

**Parameters**:

- `limit` (int | None): Maximum number of emails to fetch (None = no limit)

**Returns**:

- Iterator[Email]: Iterator of Email objects

**Raises**:

- `ConnectionError`: If unable to connect to mail service
- `RuntimeError`: If authentication fails

**Usage**:

```python
# Fetch limited number
for email in client.get_messages(limit=5):
    process(email)

# Fetch all (use with caution)
for email in client.get_messages():
    if should_stop():
        break
    process(email)
```

## Testing

Mock the client for testing:

```python
from unittest.mock import Mock
import email_api

# Inject mock
mock_client = Mock(spec=email_api.Client)
email_api.get_client = lambda: mock_client

# Test
client = email_api.get_client()
assert client is mock_client
```
