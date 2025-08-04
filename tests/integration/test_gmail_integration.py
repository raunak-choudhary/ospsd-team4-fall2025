"""Integration tests for Gmail implementation with real Gmail API."""

import asyncio
import time

import pytest

from email_api.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailNotFoundError,
)
from gmail_impl import GmailClient, GmailConfig


class TestGmailIntegration:
    """Integration tests for Gmail client with real API calls."""

    @pytest.mark.integration
    async def test_config_and_connection_integration(
        self, integration_config: GmailConfig
    ) -> None:
        """Test Gmail configuration and connection setup."""
        try:
            service = await integration_config.get_gmail_service()
            assert service is not None
        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    async def test_client_context_manager_integration(
        self, integration_config: GmailConfig
    ) -> None:
        """Test that the Gmail client context manager works with real API."""
        try:
            async with GmailClient(integration_config) as client:
                assert client._service is not None
        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    async def test_list_and_get_content_integration(
        self, integration_config: GmailConfig
    ) -> None:
        """Test listing messages and getting content with real API."""
        try:
            async with GmailClient(integration_config) as client:
                # Test listing messages
                emails = await client.list_inbox_messages(limit=5)
                assert isinstance(emails, list)
                assert len(emails) <= 5

                # If we have emails, test getting content
                if emails:
                    email = emails[0]
                    full_email = await client.get_email_content(email.id)
                    assert full_email.id == email.id
                    assert full_email.subject == email.subject

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    async def test_error_handling_integration(
        self, integration_config: GmailConfig
    ) -> None:
        """Test error handling with real API."""
        try:
            async with GmailClient(integration_config) as client:
                # Test with invalid email ID
                with pytest.raises(
                    (EmailNotFoundError, EmailConnectionError),
                    match=r".*"
                ):
                    await client.get_email_content("invalid_id_12345")

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    async def test_dependency_injection_integration(
        self, integration_config: GmailConfig
    ) -> None:
        """Test that dependency injection works properly between components."""
        # Test with different configurations
        config1 = GmailConfig(
            credentials_file=integration_config.credentials_file,
            token_file="test_token1.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        )

        config2 = GmailConfig(
            credentials_file=integration_config.credentials_file,
            token_file="test_token2.json",
            scopes=["https://www.googleapis.com/auth/gmail.readonly"],
        )

        # Both clients should work independently
        try:
            async with (
                GmailClient(config1) as client1,
                GmailClient(config2) as client2,
            ):
                emails1 = await client1.list_inbox_messages(limit=2)
                emails2 = await client2.list_inbox_messages(limit=2)

                # Both should work and return similar results
                assert isinstance(emails1, list)
                assert isinstance(emails2, list)

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    async def test_performance_and_efficiency(
        self, integration_config: GmailConfig
    ) -> None:
        """Test performance characteristics with real API."""
        try:
            async with GmailClient(integration_config) as client:
                # Test list performance
                start_time = time.time()
                emails = await client.list_inbox_messages(limit=10)
                list_time = time.time() - start_time

                # Should complete reasonably quickly (< 10 seconds)
                assert list_time < 10.0
                assert isinstance(emails, list)
                assert len(emails) <= 10

                # Test content retrieval performance if we have emails
                if emails:
                    start_time = time.time()
                    await client.get_email_content(emails[0].id)
                    content_time = time.time() - start_time

                    # Content retrieval should also be reasonable
                    assert content_time < 10.0

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.integration
    async def test_concurrent_operations(
        self, integration_config: GmailConfig
    ) -> None:
        """Test concurrent operations with real API."""
        try:
            async with GmailClient(integration_config) as client:
                # Test concurrent list operations
                tasks = [
                    client.list_inbox_messages(limit=3)
                    for _ in range(3)
                ]

                results = await asyncio.gather(*tasks)

                # All operations should succeed
                assert len(results) == 3
                for emails in results:
                    assert isinstance(emails, list)
                    assert len(emails) <= 3

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")
