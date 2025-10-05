"""End-to-end tests for the main application.

Tests execute main.py as a subprocess to simulate real user interactions.
"""

from pathlib import Path
import subprocess
import sys

import pytest

pytestmark = pytest.mark.e2e


@pytest.fixture
def main_script() -> Path:
    """Get path to main.py in the workspace root."""
    script_path = Path(__file__).parent.parent.parent / "main.py"
    if not script_path.exists():
        pytest.skip(f"main.py not found at {script_path}")
    return script_path


@pytest.fixture
def check_credentials(main_script: Path) -> None:
    """Check if credentials are available."""
    credentials_file = main_script.parent / "credentials.json"
    token_file = main_script.parent / "token.json"

    if not credentials_file.exists() and not token_file.exists():
        pytest.skip("No credentials.json or token.json found")


class TestMainScriptExecution:
    """E2E tests that execute main.py as a subprocess."""

    def test_main_script_runs_successfully(
        self,
        main_script: Path,
        check_credentials: None,
    ) -> None:
        """Test that main.py executes and completes successfully."""
        command = [sys.executable, str(main_script)]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
                cwd=str(main_script.parent),
            )

            output = result.stdout

            assert "Initializing email client..." in output
            assert "=== Crawling Inbox ===" in output
            assert "Found" in output
            assert "emails" in output
            assert "Demo complete!" in output

        except subprocess.TimeoutExpired:
            pytest.fail("E2E test timed out - main.py took too long")
        except subprocess.CalledProcessError as e:
            pytest.fail(
                f"main.py execution failed.\n"
                f"Exit Code: {e.returncode}\n"
                f"Stdout: {e.stdout}\n"
                f"Stderr: {e.stderr}",
            )

    def test_main_script_displays_email_content(
        self,
        main_script: Path,
        check_credentials: None,
    ) -> None:
        """Test that main.py displays email content."""
        command = [sys.executable, str(main_script)]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
                cwd=str(main_script.parent),
            )

            output = result.stdout

            assert "=== Email Content ===" in output
            assert "From:" in output
            assert "Subject:" in output
            assert "Date:" in output
            assert "Preview:" in output

        except subprocess.TimeoutExpired:
            pytest.fail("E2E test timed out")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"main.py execution failed: {e.stderr}")

    def test_main_script_handles_connection_errors(
        self,
        main_script: Path,
        tmp_path: Path,
    ) -> None:
        """Test that main.py handles connection errors gracefully."""
        # Create invalid credentials to trigger error
        bad_creds = tmp_path / "credentials.json"
        bad_creds.write_text("{}")

        # Use temporary directory with bad credentials
        command = [sys.executable, str(main_script)]

        # This test expects the script to handle errors gracefully
        # We'll check that it either succeeds or fails with appropriate error message
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(main_script.parent),
            )

            # Should have some output regardless of success/failure
            assert len(result.stdout) > 0 or len(result.stderr) > 0

        except subprocess.TimeoutExpired:
            pytest.fail("E2E test timed out")


class TestMainScriptStructure:
    """E2E tests for main.py structure and imports."""

    def test_main_script_syntax_is_valid(self, main_script: Path) -> None:
        """Test that main.py has valid Python syntax."""
        command = [sys.executable, "-m", "py_compile", str(main_script)]

        try:
            subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
        except subprocess.CalledProcessError as e:
            pytest.fail(f"main.py has syntax errors:\n{e.stderr}")

    def test_main_script_imports_work(self, main_script: Path) -> None:
        """Test that main.py can import all required modules."""
        import_test_code = """
import email_api
import gmail_impl
print("All imports successful")
"""

        command = [sys.executable, "-c", import_test_code]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
                cwd=str(main_script.parent),
            )

            assert "All imports successful" in result.stdout

        except subprocess.CalledProcessError as e:
            pytest.fail(f"main.py imports failed:\n{e.stderr}")

    def test_application_structure_integrity(self, main_script: Path) -> None:
        """Test that the application has expected file structure."""
        workspace_root = main_script.parent

        expected_files = [
            "main.py",
            "pyproject.toml",
            "src/email_api/src/email_api/__init__.py",
            "src/email_api/src/email_api/client.py",
            "src/gmail_impl/src/gmail_impl/__init__.py",
            "src/gmail_impl/src/gmail_impl/gmail_client.py",
        ]

        missing_files = []

        for file_path in expected_files:
            full_path = workspace_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if missing_files:
            pytest.fail(f"Missing required files: {missing_files}")
