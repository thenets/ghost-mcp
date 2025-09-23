"""Configuration management with environment variable precedence."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class GhostMode(str, Enum):
    """Ghost API mode."""
    READONLY = "readonly"
    READWRITE = "readwrite"
    AUTO = "auto"


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: LogLevel = LogLevel.INFO
    structured: bool = True
    request_id: bool = True


class GhostConfig(BaseModel):
    """Ghost API configuration."""
    url: HttpUrl = Field(default="http://localhost:2368")
    content_api_key: Optional[str] = None
    admin_api_key: Optional[str] = None
    version: str = "v5.0"
    mode: GhostMode = GhostMode.AUTO
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 2.0


class Config(BaseModel):
    """Main configuration class."""
    ghost: GhostConfig = Field(default_factory=GhostConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def load(cls, env_file: Optional[str] = None) -> "Config":
        """Load configuration with precedence: env vars > .env file > defaults."""
        # Load .env file if specified or if .env exists
        env_path = Path(env_file) if env_file else Path(".env")
        if env_path.exists():
            load_dotenv(env_path)

        # Create config with environment variables taking precedence
        ghost_config = GhostConfig(
            url=os.getenv("GHOST_URL", "http://localhost:2368"),
            content_api_key=os.getenv("GHOST_CONTENT_API_KEY"),
            admin_api_key=os.getenv("GHOST_ADMIN_API_KEY"),
            version=os.getenv("GHOST_VERSION", "v5.0"),
            mode=GhostMode(os.getenv("GHOST_MODE", "auto")),
            timeout=int(os.getenv("GHOST_TIMEOUT", "30")),
            max_retries=int(os.getenv("GHOST_MAX_RETRIES", "3")),
            retry_backoff_factor=float(os.getenv("GHOST_RETRY_BACKOFF_FACTOR", "2.0")),
        )

        logging_config = LoggingConfig(
            level=LogLevel(os.getenv("LOG_LEVEL", "info")),
            structured=os.getenv("LOG_STRUCTURED", "true").lower() == "true",
            request_id=os.getenv("LOG_REQUEST_ID", "true").lower() == "true",
        )

        return cls(ghost=ghost_config, logging=logging_config)


# Global configuration instance
config = Config.load()