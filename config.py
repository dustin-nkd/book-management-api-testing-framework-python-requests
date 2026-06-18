"""
config.py
--------
Centralized configuration loader.
Reads all environment variables from the .env file and exposes them as typed attributes for use throughout the framework.
Pattern: Single source of truth for all configuration.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file into os.environ before reading values
load_dotenv()


@dataclass(frozen=True)  # frozen=True: immutable, prevents accidental overwrites
class Config:
    """
    Holds all framework configuration values.
    frozen=True ensures values cannot be modified at runtime.
    """
    # --- Server ---
    base_url: str
    env: str
    # --- Authentication ---
    test_email: str
    test_password: str
    # --- Reporting ---
    allure_reports_dir: str
    # --- HTTP Settings ---
    request_timeout: int  # Default timeout (seconds) for all HTTP requests
    verify_ssl: bool      # Enable/disable SSL verification


def _load_config() -> Config:
    """
    Factory function: reads environment variables and returns a Config object.
    Raises ValueError if any required variable is missing.
    """
    # List of variables that must be present in .env
    required_vars = ["BASE_URL", "TEST_EMAIL", "TEST_PASSWORD"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(
            f"❌ Missing required environment variables: {missing}\n"
            f"🙏 Please check your .env file"
        )
    return Config(
        base_url=os.getenv("BASE_URL", "https://book.anhtester.com").rstrip("/"),
        env=os.getenv("ENV", "production"),
        test_email=os.getenv("TEST_EMAIL", ""),
        test_password=os.getenv("TEST_PASSWORD", ""),
        allure_reports_dir=os.getenv("ALLURE_RESULTS_DIR", "allure-results"),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        verify_ssl=os.getenv("VERIFY_SSL", "true").lower() == "true",
    )

# Singleton instance - import directly anywhere in the framework
# Example: from config import settings
settings = _load_config()