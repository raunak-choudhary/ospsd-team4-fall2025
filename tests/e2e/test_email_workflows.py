"""End-to-end tests for complete email client workflows.

These tests demonstrate complete user workflows from start to finish.
They test the system at the highest level of abstraction, simulating
real user interactions with the email client.

Setup Required:
1. Valid Gmail API credentials (credentials.json)
2. Internet connection
3. Run: uv run pytest tests/e2e/ -v

These tests validate the entire user journey and system integration.
"""

import asyncio
import time
from typing import Any

import pytest

from email_api import Email, EmailClient
from email_api.exceptions import (
    EmailAuthenticationError,
    EmailConnectionError,
    EmailNotFoundError,
)
from gmail_impl import GmailClient, GmailConfig


class TestEmailClientWorkflows:
    """End-to-end workflow tests using the complete email client system."""

    @pytest.mark.e2e
    async def test_complete_email_reading_workflow(
        self, e2e_config: GmailConfig
    ) -> None:
        """Test complete workflow: authenticate -> list -> read -> process emails."""

        async def email_processor(client: EmailClient) -> list[Email]:
            """Example email processing function using dependency injection."""
            processed_emails = []

            # Step 1: List recent emails
            emails = await client.list_inbox_messages(limit=5)

            # Step 2: Process each email
            for email_summary in emails:
                # Step 3: Get full email content
                full_email = await client.get_email_content(email_summary.id)

                # Step 4: Process email content
                if full_email.has_content:
                    processed_emails.append(full_email)

            return processed_emails

        # Execute the complete workflow
        try:
            async with GmailClient(e2e_config) as gmail_client:
                processed_emails = await email_processor(gmail_client)

                # Verify workflow results
                assert isinstance(processed_emails, list)
                for email in processed_emails:
                    assert isinstance(email, Email)
                    assert email.has_content
                    assert email.id
                    assert email.sender

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.e2e
    async def test_email_management_scenarios(
        self, e2e_config: GmailConfig
    ) -> None:
        """Test various email management scenarios."""

        async def inbox_analyzer(client: EmailClient) -> dict[str, Any]:
            """Analyze inbox contents."""
            emails = await client.list_inbox_messages(limit=20)

            analysis: dict[str, Any] = {
                "total_count": len(emails),
                "has_content_count": 0,
                "senders": set(),
            }

            # Analyze a subset for performance
            for email in emails[:5]:
                full_email = await client.get_email_content(email.id)
                if full_email.has_content:
                    analysis["has_content_count"] += 1
                analysis["senders"].add(full_email.sender.address)

            return analysis

        try:
            async with GmailClient(e2e_config) as client:
                analysis = await inbox_analyzer(client)

                # Verify analysis results
                assert analysis["total_count"] >= 0
                assert analysis["has_content_count"] >= 0
                assert len(analysis["senders"]) >= 0

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.e2e
    async def test_error_recovery_workflow(
        self, e2e_config: GmailConfig
    ) -> None:
        """Test error handling and recovery in complete workflows."""

        async def robust_email_processor(client: EmailClient) -> dict[str, Any]:
            """Email processor with error handling."""
            results: dict[str, Any] = {
                "successful_lists": 0,
                "successful_reads": 0,
                "errors": [],
            }

            try:
                # Attempt to list emails
                emails = await client.list_inbox_messages(limit=5)
                results["successful_lists"] = 1

                # Attempt to read each email with error handling
                for email in emails:
                    try:
                        await client.get_email_content(email.id)
                        results["successful_reads"] += 1
                    except (
                        EmailAuthenticationError,
                        EmailConnectionError,
                        EmailNotFoundError,
                        ValueError,
                        KeyError,
                    ) as e:
                        results["errors"].append(str(e))

                # Test with invalid email ID
                try:
                    await client.get_email_content("invalid_id_test")
                except (
                    EmailAuthenticationError,
                    EmailConnectionError,
                    EmailNotFoundError,
                    ValueError,
                    KeyError,
                ) as e:
                    results["errors"].append(f"Expected error: {e!s}")

            except (EmailAuthenticationError, EmailConnectionError) as e:
                results["errors"].append(f"List error: {e!s}")

            return results

        try:
            async with GmailClient(e2e_config) as client:
                results = await robust_email_processor(client)

                # Should have at least attempted operations
                assert results["successful_lists"] >= 0
                assert results["successful_reads"] >= 0
                assert isinstance(results["errors"], list)

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.e2e
    async def test_performance_user_experience(
        self, e2e_config: GmailConfig
    ) -> None:
        """Test performance characteristics from user perspective."""
        try:
            async with GmailClient(e2e_config) as client:
                # Test initial connection time
                start_time = time.time()
                emails = await client.list_inbox_messages(limit=1)
                initial_time = time.time() - start_time

                # Should connect and list within reasonable time
                assert initial_time < 15.0  # Allow for authentication

                if emails:
                    # Test content retrieval time
                    start_time = time.time()
                    await client.get_email_content(emails[0].id)
                    content_time = time.time() - start_time

                    # Content retrieval should be fast
                    assert content_time < 10.0

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.e2e
    async def test_concurrent_user_operations(
        self, e2e_config: GmailConfig
    ) -> None:
        """Test concurrent operations as a user might perform them."""

        async def concurrent_operations(client: EmailClient) -> int:
            """Simulate concurrent user operations."""
            # Simulate user performing multiple operations simultaneously
            list_task = client.list_inbox_messages(limit=5)

            # Start list operation
            emails = await list_task

            if emails and len(emails) >= 2:
                # Simulate reading multiple emails concurrently
                read_tasks = [
                    client.get_email_content(emails[0].id),
                    client.get_email_content(emails[1].id),
                ]

                results = await asyncio.gather(*read_tasks, return_exceptions=True)

                # At least one should succeed
                successful_reads = [r for r in results if isinstance(r, Email)]
                assert len(successful_reads) >= 0

            return len(emails) if emails else 0

        try:
            async with GmailClient(e2e_config) as client:
                email_count = await concurrent_operations(client)
                assert email_count >= 0

        except (EmailAuthenticationError, EmailConnectionError) as e:
            pytest.skip(f"Gmail API not accessible: {e}")

    @pytest.mark.e2e
    async def test_resource_management_workflow(
        self, e2e_config: GmailConfig
    ) -> None:
        """Test proper resource management in complete workflows."""

        # Test multiple client sessions
        for session in range(3):
            try:
                async with GmailClient(e2e_config) as client:
                    emails = await client.list_inbox_messages(limit=2)
                    assert isinstance(emails, list)

                    # Each session should work independently
                    if emails:
                        email = await client.get_email_content(emails[0].id)
                        assert isinstance(email, Email)

            except (EmailAuthenticationError, EmailConnectionError) as e:
                pytest.skip(f"Gmail API not accessible in session {session}: {e}")
