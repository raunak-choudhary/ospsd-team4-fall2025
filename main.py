"""Example usage of the email client with dependency injection."""

import email_api
import gmail_impl  # noqa: F401  # type: ignore[reportUnusedImport]  # Import injects GmailClient implementation


def main() -> None:
    """Demonstrate email client functionality."""
    try:
        print("Initializing email client...")
        client = email_api.get_client()

        # Crawl inbox
        print("\n=== Crawling Inbox ===")
        emails = list(client.get_messages(limit=5))
        print(f"Found {len(emails)} emails")

        if not emails:
            print("Inbox is empty")
            return

        # Pick and display email content
        print("\n=== Email Content ===")
        for i, email in enumerate(emails, 1):
            print(f"\nEmail {i}:")
            print(f"  From: {email.sender}")
            print(f"  Subject: {email.subject}")
            print(f"  Date: {email.date_sent}")
            preview = email.body[:100].replace("\n", " ") if email.body else "(no body)"
            print(f"  Preview: {preview}...")

        print("\nDemo complete!")

    except ConnectionError as e:
        print(f"\nConnection Error: {e}")
        print("Please check your internet connection.")
    except RuntimeError as e:
        print(f"\nAuthentication Error: {e}")
        print("Please check your Gmail API credentials.")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        raise


if __name__ == "__main__":
    main()
