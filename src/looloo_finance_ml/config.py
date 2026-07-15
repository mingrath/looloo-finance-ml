"""Environment-backed configuration with explicit credential boundaries."""

from __future__ import annotations

from dataclasses import dataclass
import os


class ConfigError(ValueError):
    """Raised when required runtime configuration is missing or invalid."""


@dataclass(frozen=True)
class RuntimeConfig:
    """Non-secret runtime settings; secret values are read only at call time."""

    artifacts_dir: str = "artifacts"
    alpaca_data_url: str = "https://data.alpaca.markets/v2"
    sec_user_agent: str | None = None
    webull_env: str = "uat"
    webull_base_url: str = "https://th-api.uat.webullbroker.com"

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        env = os.getenv("WEBULL_ENV", "uat").lower()
        if env not in {"uat", "production"}:
            raise ConfigError("WEBULL_ENV must be 'uat' or 'production'")
        default_webull = (
            "https://th-api.uat.webullbroker.com" if env == "uat" else "https://api.webull.co.th"
        )
        return cls(
            artifacts_dir=os.getenv("LOOLOO_ARTIFACTS_DIR", "artifacts"),
            alpaca_data_url=os.getenv("ALPACA_DATA_URL", "https://data.alpaca.markets/v2"),
            sec_user_agent=os.getenv("SEC_USER_AGENT"),
            webull_env=env,
            webull_base_url=os.getenv("WEBULL_BASE_URL", default_webull),
        )

    def require_sec_user_agent(self) -> str:
        if not self.sec_user_agent or "@" not in self.sec_user_agent:
            raise ConfigError("SEC_USER_AGENT must include an application name and contact email")
        return self.sec_user_agent

    @staticmethod
    def require_alpaca_credentials() -> tuple[str, str]:
        key = os.getenv("ALPACA_API_KEY")
        secret = os.getenv("ALPACA_API_SECRET")
        if not key or not secret:
            raise ConfigError(
                "ALPACA_API_KEY and ALPACA_API_SECRET are required for live data-build"
            )
        return key, secret

    @staticmethod
    def require_webull_credentials() -> tuple[str, str]:
        key = os.getenv("WEBULL_APP_KEY")
        secret = os.getenv("WEBULL_APP_SECRET")
        if not key or not secret:
            raise ConfigError(
                "WEBULL_APP_KEY and WEBULL_APP_SECRET are required for webull-compare"
            )
        return key, secret
