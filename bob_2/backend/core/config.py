from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    steve_continuity_dir: str = "continuity"
    steve_runtime_dir: str = "runtime"
    steve_model: str = "gemini-2.0-flash"
    
    @property
    def model_name(self) -> str:
        if "gpt" in self.steve_model.lower() or "claude" in self.steve_model.lower():
            return "gemini-2.0-flash"
        return self.steve_model
    
    qdrant_collection: str = "hal_memory"
    
    google_api_key: str | None = None
    gemini_api_key: str | None = None
    
    @property
    def api_key(self) -> str | None:
        return self.google_api_key or self.gemini_api_key
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
