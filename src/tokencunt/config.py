"""Configuration module for TokenCUNT."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Optional
import os


class Config(BaseSettings):
    """Application configuration with priority: env vars → config file → defaults."""
    
    model_config = SettingsConfigDict(
        env_prefix="MINIMAX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # API Configuration
    api_key: str = Field(default="")
    group_id: str = Field(default="")
    
    # Model Configuration  
    default_model: str = Field(default="MiniMax-M2.5")
    
    # Budget Configuration
    default_budget: int = Field(default=100000)  # tokens
    
    # Session Configuration
    session_dir: Path = Field(
        default_factory=lambda: Path.home() / ".tokencunt" / "sessions"
    )
    
    # Config file path
    config_file: Optional[Path] = Field(
        default_factory=lambda: Path.home() / ".tokencunt" / "config.yaml"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_config_file()
    
    def load_config_file(self):
        """Load additional config from YAML file if exists."""
        try:
            import yaml
        except ImportError:
            return
            
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    data = yaml.safe_load(f) or {}
                # Apply file config (lower priority than env vars)
                for key, value in data.items():
                    if not getattr(self, key, None):  # Only if not set by env
                        setattr(self, key, value)
            except Exception:
                pass
    
    @property
    def is_configured(self) -> bool:
        """Check if basic configuration is present."""
        return bool(self.api_key and self.group_id)


# Global config instance
config = Config()
