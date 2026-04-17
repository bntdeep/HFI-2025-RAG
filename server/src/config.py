from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve .env relative to the server/ package root,
# regardless of the working directory the script is run from.
_SERVER_ROOT = Path(__file__).parent.parent  # src/ -> server/
_ENV_FILE = _SERVER_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # EPAM DIAL proxy
    epam_dial_api_key: str = "not-set"
    epam_dial_base_url: str = "https://ai-proxy.lab.epam.com"
    api_version: str = "2024-12-01-preview"

    # Model deployments
    main_llm_deployment: str = "gpt-4o"
    main_llm_temperature: float = 0.1
    main_llm_max_tokens: int = 4096

    vision_llm_deployment: str = "gpt-4o"
    vision_llm_max_tokens: int = 1024

    embeddings_deployment: str = "text-embedding-3-large-1"
    embeddings_dimensions: int = 3072

    # Storage paths — relative values are resolved from server/ root, not CWD
    chroma_db_path: str = ""
    metadata_db_path: str = ""
    uploads_path: str = ""

    # Chunking
    chunk_size_tokens: int = 1000
    chunk_overlap_tokens: int = 200
    min_chunk_size_tokens: int = 50

    # MCP server
    mcp_server_port: int = 8000

    # REST API server
    rest_api_port: int = 8080

    @property
    def azure_endpoint(self) -> str:
        return self.epam_dial_base_url

    def _resolve(self, value: str, default_name: str) -> Path:
        """
        Resolve a storage path to an absolute Path.
        If the env value is empty or relative, anchor it under server/ root
        so the location is the same regardless of working directory.
        """
        p = Path(value) if value else Path(default_name)
        if not p.is_absolute():
            p = _SERVER_ROOT / p
        return p

    @property
    def chroma_db_dir(self) -> Path:
        return self._resolve(self.chroma_db_path, "chroma_db")

    @property
    def metadata_db_file(self) -> Path:
        return self._resolve(self.metadata_db_path, "metadata.db")

    @property
    def uploads_dir(self) -> Path:
        return self._resolve(self.uploads_path, "uploads")


settings = Settings()
