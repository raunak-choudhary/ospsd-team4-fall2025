# Getting Started

Quick start guide for setting up and using the Email Client with Dependency Injection.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud Console account (for Gmail implementation)

## Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ospsd-ta-task

# Install all dependencies
uv sync --extra dev --extra email --extra gmail
```

### 2. Gmail API Setup

To use the Gmail implementation, you need to set up OAuth2 credentials:

#### Create Google Cloud Project

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" and select "Library"
   - Search for "Gmail API"
   - Click "Enable"

#### Create OAuth2 Credentials

4. Navigate to "APIs & Services" and select "Credentials"
5. Click "Create Credentials" and choose "OAuth 2.0 Client ID"
6. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Add your email as a test user
   - Complete required fields including app name and support email
7. Select "Desktop app" as application type
8. Click "Create"
9. Download the credentials JSON file
10. Save the file as `credentials.json` in the project root directory:
    ```bash
    # Your project structure should look like:
    ospsd-ta-task/
    ├── credentials.json       # Place downloaded file here
    ├── src/
    ├── tests/
    └── main.py
    ```

#### First Run Authentication

On first run, the application will:
1. Open your browser for OAuth2 authentication
2. Ask you to sign in with your Google account
3. Request permission to access Gmail (read-only)
4. Create a `token.json` file to cache the access token
5. Subsequent runs will use the cached token (no browser popup)

Note: Keep `credentials.json` and `token.json` secure and never commit them to version control. Both files are already included in `.gitignore`.

## Quick Start

### Basic Usage

```python
import email_api
import gmail_impl  # noqa: F401  # Import injects implementation

# Get client via dependency injection
client = email_api.get_client()

# Fetch recent emails
for email in client.get_messages(limit=5):
    print(f"From: {email.sender.address}")
    print(f"Subject: {email.subject}")
    print(f"Date: {email.date_sent}")
```

### Demo Application

Run the included demo:

```bash
uv run python main.py
```

This will:
1. Open browser for OAuth2 authentication (first run only)
2. Fetch your 5 most recent emails
3. Display email content

## Development

### Running Tests

```bash
# All tests (unit + integration + e2e)
uv run pytest

# Unit tests only (fast, no credentials needed)
uv run pytest -m unit

# Integration tests (requires credentials.json)
uv run pytest -m integration

# E2E tests (requires credentials.json)
uv run pytest -m e2e
```

### Code Quality

```bash
# Type checking
uv run mypy src/

# Linting
uv run ruff check .

# Format code
uv run ruff format .

# Coverage report
uv run pytest --cov=src --cov-report=html
```

### Documentation

```bash
# Serve documentation locally at http://127.0.0.1:8000
uv run mkdocs serve

# Build static documentation
uv run mkdocs build
```

## Project Structure

```
ospsd-ta-task/
├── src/
│   ├── email_api/          # Interface component
│   └── gmail_impl/         # Gmail implementation
├── tests/
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── docs/                   # Documentation
├── main.py                 # Demo application
└── pyproject.toml          # Workspace configuration
```

## CI/CD Setup (CircleCI)

If you fork this repository and want to run integration/E2E tests in CI, you need to configure environment variables in CircleCI.

### Required Environment Variables

Navigate to your CircleCI project settings and select "Environment Variables" to add:

| Variable Name | Description | How to Get |
|--------------|-------------|------------|
| `GMAIL_CREDENTIALS_JSON` | Contents of your `credentials.json` file | Copy the entire JSON content from your local `credentials.json` |
| `GMAIL_CI_TOKEN_JSON` | Pre-authenticated token for integration and E2E tests | Run tests locally once to generate `token.json`, then copy its content |

### Setting Up Environment Variables

1. **Get credentials JSON**:
   ```bash
   # Copy content from your credentials.json
   cat credentials.json
   # Copy the entire output
   ```

2. **Generate token JSON** (first-time auth):
   ```bash
   # Run the demo app locally to authenticate
   uv run python main.py
   # This creates token.json after OAuth2 flow

   # Copy token content
   cat token.json
   # Copy the entire output
   ```

3. **Add to CircleCI**:
   - Go to CircleCI project, navigate to "Project Settings", then "Environment Variables"
   - Click "Add Environment Variable"
   - Name: `GMAIL_CREDENTIALS_JSON`
   - Value: Paste the credentials JSON content
   - Repeat for `GMAIL_CI_TOKEN_JSON`

### Workflow Behavior

- PR branches: Only run unit tests and linting (no credentials needed)
- Main/develop branches: Run full test suite including integration and E2E tests
- Feature branches with `gmail` or `integration` in name: Run full suite

Security Note: Environment variables are encrypted by CircleCI and only accessible during builds. Never expose them in logs or output.

## Next Steps

- Learn about [Dependency Injection](../architecture/dependency-injection.md)
- Understand the [Testing Strategy](../architecture/testing.md)
- Explore the [Email API Reference](../reference/email-api.md)
- Check out the [Gmail Implementation](../reference/gmail-impl.md)
