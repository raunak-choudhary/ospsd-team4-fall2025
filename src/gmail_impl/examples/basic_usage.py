"""Basic usage example for Gmail Implementation.

This example demonstrates how to:
1. Configure Gmail API credentials
2. Connect to Gmail using async context manager
3. List recent inbox messages
4. Get full content of an email

Note: This example uses print() statements instead of logging for clarity
and educational purposes. In production code, prefer proper logging.
"""

import asyncio

from email_api.exceptions import EmailError
from gmail_impl import GmailClient, GmailConfig


async def main() -> None:
    """Demonstrate basic Gmail client usage."""
    # Configure Gmail client
    config = GmailConfig(
        credentials_file="credentials.json",
        token_file="token.json",
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )

    try:
        # Use async context manager for proper connection handling
        async with GmailClient(config) as client:
            print("Connected to Gmail API successfully!")

            # List recent emails
            print("Listing recent emails...")
            emails = await client.list_inbox_messages(limit=3)

            print(f"Found {len(emails)} recent emails:")
            for i, email in enumerate(emails, 1):
                print(f"\n{i}. Subject: {email.subject}")
                print(f"   From: {email.sender}")
                print(f"   Date: {email.date_sent}")
                print("   Content: Not loaded (for performance)")

            # Get full content of first email
            if emails:
                print("\n" + "=" * 60)
                print("GETTING FULL EMAIL CONTENT")
                print("=" * 60)
                first_email_id = emails[0].id
                full_email = await client.get_email_content(first_email_id)

                print(f"\nSubject: {full_email.subject}")
                print(f"From: {full_email.sender}")
                print(f"To: {', '.join(str(r) for r in full_email.recipients)}")
                print(f"Date sent: {full_email.date_sent}")
                print(f"Date received: {full_email.date_received}")

                if full_email.has_content:
                    content = full_email.get_content()
                    content_type = (
                        "Text" if full_email.has_text_content else "HTML only"
                    )
                    print(f"\nContent Type: {content_type}")
                    print(f"Content Length: {len(content):,} characters")

                    print("\n" + "-" * 50)
                    print("EMAIL CONTENT:")
                    print("-" * 50)

                    # Show full content (clean up excessive whitespace)
                    lines = content.split("\n")
                    clean_lines = [line.strip() for line in lines if line.strip()]
                    clean_content = "\n".join(clean_lines)
                    print(clean_content)

                    print("-" * 50)

                    # Show content type details
                    content_types = []
                    if full_email.has_text_content:
                        content_types.append("Plain Text")
                    if full_email.has_html_content:
                        content_types.append("HTML")
                    print(f"Available formats: {', '.join(content_types)}")

                else:
                    print("\nNo readable content found in email.")

    except EmailError as e:
        print(f"Email system error: {e}")
        print("Make sure you have set up Gmail API credentials correctly.")
    except OSError as e:
        print(f"System error: {e}")
        print("Check your internet connection and file permissions.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")


if __name__ == "__main__":
    print("Gmail Implementation Example")
    print("=" * 30)
    asyncio.run(main())
