# Gmail Implementation

A Gmail implementation of the `EmailClient` protocol with OAuth2 authentication and dependency injection.

## Overview

This component provides a concrete implementation of the `EmailClient` protocol from the `email-api` component, using the Gmail API. It follows clean interface design principles with a simple API that encapsulates complex Gmail API interactions, authentication, and message parsing.

## Features

- **Protocol Compliance**: Implements the `EmailClient` protocol exactly
- **Dependency Injection**: Gmail API service is injected, not created internally
- **OAuth2 Authentication**: Secure authentication with automatic token refresh
- **Async Support**: Full async/await support with context manager
- **Error Handling**: Comprehensive error handling with specific exception types
- **Message Parsing**: Handles complex MIME structures and multipart messages

## Installation

This component is part of a uv workspace. Install dependencies using:

```bash
uv sync
```

## Setup

### 1. Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the credentials JSON file

### 2. Credentials Setup

1. Save the downloaded credentials file as `credentials.json` in your project root
2. The first time you run the application, it will open a browser for OAuth2 authorization
3. A `token.json` file will be created automatically for future use

## Usage

### Basic Usage

```python
import asyncio
from gmail_impl import GmailClient, GmailConfig

async def main():
    # Configure Gmail client
    config = GmailConfig(
        credentials_file="credentials.json",
        token_file="token.json"
    )
    
    # Use async context manager for automatic connection management
    async with GmailClient(config) as client:
        # List recent emails
        emails = await client.list_inbox_messages(limit=5)
        print(f"Found {len(emails)} emails")
        
        # Get full content of first email
        if emails:
            email = await client.get_email_content(emails[0].id)
            print(f"Subject: {email.subject}")
            print(f"From: {email.sender}")
            print(f"Content: {email.get_content()}")

asyncio.run(main())
```

See the `examples/` directory for more complete usage examples.

### Configuration Options

```python
from gmail_impl import GmailConfig

# Custom configuration
config = GmailConfig(
    credentials_file="/path/to/credentials.json",
    token_file="/path/to/token.json",
    scopes=[
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
)
```

### Error Handling

```python
from email_api.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailNotFoundError,
)

async def handle_errors():
    config = GmailConfig("credentials.json")
    
    try:
        async with GmailClient(config) as client:
            emails = await client.list_inbox_messages()
    except EmailAuthenticationError as e:
        print(f"Authentication failed: {e}")
        print(f"Error code: {e.error_code}")
    except EmailConnectionError as e:
        print(f"Connection failed: {e}")
    except EmailNotFoundError as e:
        print(f"Email not found: {e}")
```

## Examples

The `examples/` directory contains complete usage examples:

- `basic_usage.py` - Basic Gmail client usage with inbox listing and content retrieval

To run an example:

```bash
# From the project root
cd src/gmail_impl
uv run python examples/basic_usage.py
```

## Development

### Running Tests

```bash
# Run all tests for this component
uv run pytest src/gmail_impl/tests/

# Run with coverage
uv run pytest src/gmail_impl/tests/ --cov=src/gmail_impl --cov-report=html

# Run specific test file
uv run pytest src/gmail_impl/tests/test_client.py -v
```

### Code Quality

```bash
# Run linting
uv run ruff check src/gmail_impl/

# Run type checking
uv run mypy src/gmail_impl/

# Format code
uv run ruff format src/gmail_impl/
```

## Architecture

### Dependency Injection

The Gmail client uses dependency injection for the Gmail API service:

```python
# The GmailConfig handles service creation
service = await config.get_gmail_service()

# The service is injected into the client during context manager entry
async with GmailClient(config) as client:
    # client._service now contains the injected Gmail API service
    pass
```

This design enables:
- Easy testing with mock services
- Flexible configuration and authentication
- Clean separation of concerns

### Interface Design

The implementation follows clean interface design principles:

- **Minimal API Surface**: Core methods for listing messages and retrieving content
- **Substantial Implementation**: Complex OAuth2 authentication, Gmail API interaction, MIME parsing, and error handling are encapsulated behind the simple interface
- **Clear Abstraction**: Users interact with high-level email operations without needing to understand Gmail API specifics

### Error Translation

Gmail API errors are translated to the interface's exception hierarchy:

- HTTP 401/403 → `EmailAuthenticationError`
- HTTP 400 with "Invalid id value" → `EmailNotFoundError`
- Other errors → `EmailConnectionError`

## Gmail API Scopes

The component uses these OAuth2 scopes by default:

- `https://www.googleapis.com/auth/gmail.readonly` - Read access to Gmail

## Troubleshooting

### Authentication Issues

1. **Credentials file not found**: Ensure `credentials.json` exists and is valid
2. **OAuth2 flow fails**: Check internet connection and browser settings
3. **Token expired**: Delete `token.json` to force re-authentication
4. **Scope issues**: Verify the required scopes are enabled in Google Cloud Console

### Connection Issues

1. **Gmail API disabled**: Enable Gmail API in Google Cloud Console
2. **Rate limiting**: Implement retry logic or reduce request frequency
3. **Network issues**: Check internet connection and firewall settings

### Message Parsing Issues

1. **Encoding problems**: The component handles UTF-8 and base64url encoding automatically
2. **Missing content**: Some emails may not have text/HTML content
3. **Complex MIME structures**: The parser handles nested multipart messages

## Dependencies

- `email-api` - Interface definitions and data models
- `google-auth` - Google authentication library
- `google-auth-oauthlib` - OAuth2 flow implementation
- `google-api-python-client` - Gmail API client

## License

MIT 