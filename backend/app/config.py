from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    base_model: str = "Qwen/Qwen2.5-7B-Instruct"
    lora_adapter_path: str = ""
    hf_api_token: str = ""
    use_hf_inference_api: bool = False

    # External APIs
    amadeus_api_key: str = ""
    amadeus_api_secret: str = ""
    openweathermap_api_key: str = ""
    google_places_api_key: str = ""

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    allowed_origins: str = "http://localhost:3000"
    chroma_dir: str = "./chroma_db"
    log_level: str = "INFO"

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def has_local_adapter(self) -> bool:
        return bool(self.lora_adapter_path) and Path(self.lora_adapter_path).exists()


@lru_cache
def get_settings() -> Settings:
    return Settings()
