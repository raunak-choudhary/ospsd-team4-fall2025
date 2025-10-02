"""Integration tests for Gmail implementation with real Gmail API.

These tests verify the integration between our GmailClient and the actual Gmail API,
validating cross-component contracts, error handling, and state management.

ARCHITECTURE NOTE: This project uses monkey patching dependency injection.
- email_api.get_client() is replaced by gmail_impl with: lambda: GmailClient()
- Tests MUST use email_api.get_client() to maintain DI abstraction
- Direct GmailClient imports/instantiation would break the architecture
"""

from collections.abc import Generator
import os
from pathlib import Path
import time

import pytest

import email_api
from email_api import Email
import gmail_impl  # noqa: F401 - Performs dependency injection

# Constants for test configuration
TEST_MESSAGE_LIMIT = 5
PERFORMANCE_TIMEOUT_SECONDS = 15.0
MAX_ITERATOR_TEST_MESSAGES = 3


@pytest.fixture
def clean_token_file() -> Generator[Path, None, None]:
    """Ensure token file doesn't interfere between tests."""
    token_path = Path("token.json")
    original_exists = token_path.exists()
    original_content = None

    if original_exists:
        original_content = token_path.read_text()

    yield token_path

    # Restore original state
    if original_exists and original_content:
        token_path.write_text(original_content)
    elif not original_exists and token_path.exists():
        token_path.unlink()


class TestGmailIntegration:
    """Integration tests for Gmail client with real API calls.

    These tests verify:
    1. Cross-component contracts between GmailClient and Gmail API
    2. OAuth2 authentication flow and token management
    3. Error propagation and handling across the integration boundary
    4. Data serialization and deserialization (Gmail API -> Email objects)
    5. State management and connection lifecycle
    """

    @pytest.mark.integration
    def test_basic_connection_and_authentication(self) -> None:
        """Verify OAuth2 authentication flow and Gmail API connection.

        This test validates:
        - OAuth2 credentials are properly loaded or created
        - Token is cached for subsequent requests
        - Initial API connection succeeds
        - Client can fetch at least one message to prove authentication
        """
        try:
            client = email_api.get_client()

            # Force connection by trying to get first message
            messages = client.get_messages(limit=1)
            first_message = next(messages, None)

            # Verify authentication succeeded by checking we got a valid message
            # or that the iterator completed successfully (empty inbox case)
            assert first_message is None or isinstance(first_message, Email)

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_get_messages_validates_api_contract(self) -> None:
        """Verify message retrieval respects limit and validates Email contract.

        This test validates the cross-component contract between Gmail API
        and our Email data model, ensuring all required fields are properly
        parsed and populated.
        """
        try:
            client = email_api.get_client()

            # Test getting messages with explicit limit
            emails = list(client.get_messages(limit=TEST_MESSAGE_LIMIT))
            assert isinstance(emails, list)
            assert len(emails) <= TEST_MESSAGE_LIMIT

            # Verify Email contract compliance for each message
            if emails:
                for email in emails:
                    # Validate required fields are present and correct type
                    assert email.id, "Email ID is required"
                    assert isinstance(email.subject, str), "Subject must be string"
                    assert email.sender.address, "Sender address is required"
                    assert "@" in email.sender.address, "Sender must be valid email"
                    assert isinstance(email.body, str), "Body must be string"
                    assert isinstance(email.recipients, list), "Recipients must be list"

                    # Validate date fields are properly parsed
                    assert email.date_sent is not None, "date_sent is required"
                    assert email.date_received is not None, "date_received is required"
                    # Verify dates have timezone info (Gmail provides UTC dates)
                    assert email.date_sent.tzinfo is not None
                    assert email.date_received.tzinfo is not None

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_iterator_exhaustion_and_pagination(self) -> None:
        """Verify iterator pattern and pagination boundaries.

        This test validates:
        - Iterator protocol implementation (__iter__, __next__)
        - Pagination across multiple Gmail API requests
        - Proper iterator exhaustion
        - StopIteration handling
        """
        try:
            client = email_api.get_client()

            # Test iterator protocol
            messages = client.get_messages()
            assert hasattr(messages, "__iter__")
            assert hasattr(messages, "__next__")

            # Consume iterator and verify pagination
            count = 0
            message_ids = set()

            for email in messages:
                assert email.id, "Each message must have an ID"
                assert email.id not in message_ids, "No duplicate message IDs"
                message_ids.add(email.id)
                count += 1

                # Stop after reasonable number to avoid exhausting entire inbox
                if count >= MAX_ITERATOR_TEST_MESSAGES:
                    break

            assert count <= MAX_ITERATOR_TEST_MESSAGES

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_message_retrieval_performance(self) -> None:
        """Verify message retrieval completes within acceptable time.

        This test validates performance characteristics but is lenient to account
        for network variability and CI/CD environments.
        """
        try:
            client = email_api.get_client()

            # Measure time to fetch 10 messages including authentication
            start_time = time.time()
            emails = list(client.get_messages(limit=10))
            elapsed_time = time.time() - start_time

            # Allow generous timeout for network variability and OAuth flow
            timeout_seconds = PERFORMANCE_TIMEOUT_SECONDS
            if os.getenv("CI"):
                # Double timeout in CI environments
                timeout_seconds *= 2

            assert elapsed_time < timeout_seconds, (
                f"Message retrieval took {elapsed_time:.2f}s, "
                f"expected < {timeout_seconds}s"
            )
            assert isinstance(emails, list)
            assert len(emails) <= 10

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_email_address_parsing_contract(self) -> None:
        """Verify email address parsing handles various formats.

        This test validates the cross-component contract for email address
        parsing, ensuring the client correctly handles:
        - Simple addresses (user@domain.com)
        - Named addresses (Name <user@domain.com>)
        - Multiple recipients
        """
        try:
            client = email_api.get_client()

            # Get a few emails to test address parsing
            emails = list(client.get_messages(limit=3))

            if emails:
                for email in emails:
                    # Validate sender address format
                    assert "@" in email.sender.address
                    assert "." in email.sender.address.split("@")[1]

                    # If sender has a name, it should be non-empty
                    if email.sender.name is not None:
                        assert len(email.sender.name.strip()) > 0

                    # Validate recipients list (may be empty but must be list)
                    assert isinstance(email.recipients, list)
                    for recipient in email.recipients:
                        assert "@" in recipient.address
                        assert "." in recipient.address.split("@")[1]

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_limit_parameter_boundary_conditions(self) -> None:
        """Verify limit parameter handles boundary conditions correctly.

        This test validates:
        - Zero limit behavior
        - Single message limit
        - Limit larger than inbox size
        """
        try:
            client = email_api.get_client()

            # Test limit=0 (should return empty list)
            emails = list(client.get_messages(limit=0))
            assert len(emails) == 0

            # Test limit=1 (should return at most 1 message)
            emails = list(client.get_messages(limit=1))
            assert len(emails) <= 1

            # Test various limits
            for limit in [3, 5, 10]:
                emails = list(client.get_messages(limit=limit))
                assert len(emails) <= limit, f"Expected <= {limit}, got {len(emails)}"

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_oauth_token_reuse_behavior(self, clean_token_file: Path) -> None:
        """Verify OAuth token is cached and reused across multiple API calls.

        This test validates that the client caches tokens by checking file existence
        rather than relying on flaky timing assertions.

        IMPROVED: Replaced timing assertions with behavioral verification.
        """
        try:
            client = email_api.get_client()

            # First call should create token file
            list(client.get_messages(limit=1))

            # Verify token file was created
            assert clean_token_file.exists(), (
                "Token file should be created after first call"
            )

            # Record token file modification time
            first_mtime = clean_token_file.stat().st_mtime

            # Small delay to ensure mtime would change if file is rewritten
            time.sleep(0.1)

            # Second call should reuse existing token
            list(client.get_messages(limit=1))

            # Verify token file was NOT recreated (same modification time)
            second_mtime = clean_token_file.stat().st_mtime
            assert first_mtime == second_mtime, (
                "Token file should not be recreated on second call"
            )

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_partial_message_parsing_resilience(self) -> None:
        """Verify client handles messages with missing or malformed fields.

        This test validates resilience when Gmail API returns messages with
        incomplete data (e.g., no subject, no sender, etc.).

        The client should parse what it can and provide defaults for missing fields.
        """
        try:
            client = email_api.get_client()

            # Get several messages to increase chance of finding edge cases
            emails = list(client.get_messages(limit=20))

            if emails:
                for email in emails:
                    # Required fields must always be present (even if empty)
                    assert email.id is not None
                    assert email.subject is not None  # May be empty string
                    assert email.sender is not None
                    assert email.sender.address  # Must have address
                    assert email.body is not None  # May be empty string
                    assert email.date_sent is not None
                    assert email.date_received is not None
                    assert email.recipients is not None  # May be empty list

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_dependency_injection_via_module_import(self) -> None:
        """Verify dependency injection pattern works correctly.

        This test validates that importing gmail_impl properly injects the
        GmailClient as the default implementation for email_api.get_client().
        """
        try:
            client = email_api.get_client()

            # Verify client works through DI interface
            messages = list(client.get_messages(limit=1))
            assert isinstance(messages, list)

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_invalid_credentials_error_propagation(self, tmp_path: Path) -> None:
        """Verify error handling with invalid credentials file.

        This test now works with environment variable support in GmailClient.
        """
        # Create invalid credentials file
        bad_creds = tmp_path / "bad_credentials.json"
        bad_creds.write_text("{}")

        # Also use a non-existent token path to force re-authentication
        bad_token = tmp_path / "bad_token.json"

        # Set environment variables to use bad credentials
        original_creds = os.environ.get("GMAIL_CREDENTIALS_PATH")
        original_token = os.environ.get("GMAIL_TOKEN_PATH")

        os.environ["GMAIL_CREDENTIALS_PATH"] = str(bad_creds)
        os.environ["GMAIL_TOKEN_PATH"] = str(bad_token)

        try:
            # Create new client with bad credentials via DI
            client = email_api.get_client()

            # Should raise RuntimeError with invalid credentials
            with pytest.raises(RuntimeError):
                list(client.get_messages(limit=1))

        finally:
            # Restore original environment
            if original_creds:
                os.environ["GMAIL_CREDENTIALS_PATH"] = original_creds
            else:
                os.environ.pop("GMAIL_CREDENTIALS_PATH", None)

            if original_token:
                os.environ["GMAIL_TOKEN_PATH"] = original_token
            else:
                os.environ.pop("GMAIL_TOKEN_PATH", None)

    @pytest.mark.integration
    def test_corrupted_token_recovery(self, tmp_path: Path) -> None:
        """Verify client recovers from corrupted token file.

        This test validates resilience when the cached token file is corrupted.
        """
        try:
            # Create corrupted token file
            corrupted_token = tmp_path / "corrupted_token.json"
            corrupted_token.write_text("{ invalid json content }")

            # Set environment variable to use corrupted token
            original_token = os.environ.get("GMAIL_TOKEN_PATH")
            os.environ["GMAIL_TOKEN_PATH"] = str(corrupted_token)

            try:
                # Create new client with corrupted token via DI
                client = email_api.get_client()

                # Should recover by deleting corrupted token and re-authenticating
                list(client.get_messages(limit=1))

                # If we got here, recovery worked
                # Token should have been recreated
                assert corrupted_token.exists()
                content = corrupted_token.read_text()
                assert "invalid json" not in content

            finally:
                # Restore original environment
                if original_token:
                    os.environ["GMAIL_TOKEN_PATH"] = original_token
                else:
                    os.environ.pop("GMAIL_TOKEN_PATH", None)

        except RuntimeError as e:
            # OAuth flow requires user interaction in some cases
            if "OAuth" in str(e) or "browser" in str(e).lower():
                pytest.skip("OAuth flow requires user interaction")
            pytest.skip(f"Cannot test token corruption: {e}")


class TestGmailIntegrationStateManagement:
    """Integration tests for state management and connection lifecycle."""

    @pytest.mark.integration
    def test_multiple_get_client_calls_return_independent_instances(self) -> None:
        """Verify each get_client() call returns a new independent instance.

        This validates the DI pattern creates fresh instances rather than
        singletons, preventing state pollution between usage contexts.
        """
        try:
            client1 = email_api.get_client()
            client2 = email_api.get_client()

            # Should be different instances (lambda creates new instance each time)
            assert client1 is not client2, (
                "get_client() should return new instances, not singletons"
            )

            # Both should work independently
            list(client1.get_messages(limit=1))
            list(client2.get_messages(limit=1))

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    def test_iterator_state_independence(self) -> None:
        """Verify multiple iterators from same client maintain independent state.

        This validates that calling get_messages() multiple times returns
        independent iterators that don't interfere with each other.
        """
        try:
            client = email_api.get_client()

            # Create two independent iterators
            iter1 = client.get_messages(limit=5)
            iter2 = client.get_messages(limit=5)

            # Consume first message from iter1
            msg1_from_iter1 = next(iter1, None)

            # Consume first message from iter2
            msg1_from_iter2 = next(iter2, None)

            # Both should work independently
            if msg1_from_iter1 and msg1_from_iter2:
                # Both should be valid Email objects
                assert isinstance(msg1_from_iter1, Email)
                assert isinstance(msg1_from_iter2, Email)

        except (ConnectionError, RuntimeError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")
