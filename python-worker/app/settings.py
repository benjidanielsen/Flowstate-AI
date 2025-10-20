"""Centralised environment configuration for the Python worker."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, SecretStr

load_dotenv()


class Settings(BaseModel):
    """Runtime configuration sourced from environment variables."""

    model_config = ConfigDict(populate_by_name=True)

    openai_api_key: Optional[SecretStr] = Field(default=None, alias="OPENAI_API_KEY")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    openai_api_url: str = Field(default="https://api.openai.com/v1/embeddings", alias="OPENAI_API_URL")
    backend_api_url: str = Field(default="http://localhost:3001", alias="BACKEND_API_URL")

    def require_openai_api_key(self) -> SecretStr:
        """Return the OpenAI API key or raise if it has not been configured."""

        if self.openai_api_key is None or not self.openai_api_key.get_secret_value():
            raise ValueError("OPENAI_API_KEY not configured")
        return self.openai_api_key


@lru_cache
def get_settings() -> Settings:
    """Load the application settings from environment variables."""

    return Settings.model_validate(os.environ)

