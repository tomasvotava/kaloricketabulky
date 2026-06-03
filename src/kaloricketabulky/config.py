"""Environment-backed configuration for the CLI/app layer."""

from dotenv import find_dotenv, load_dotenv
from env_proxy import EnvConfig, EnvProxy, Field

load_dotenv(find_dotenv(usecwd=True))


class _Settings(EnvConfig):
    """Settings read from KALORICKETABULKY_* environment variables (or a .env)."""

    env_proxy = EnvProxy(prefix="KALORICKETABULKY")

    email: str = Field(description="Login email (required).")
    password: str = Field(description="Login password (required).")
    base_url: str = Field(default="https://www.kaloricketabulky.cz", description="API base URL.")


Settings = _Settings()
