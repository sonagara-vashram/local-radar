from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # MongoDB settings
    MONGO_URI: str = Field("mongodb://localhost:27017", env="MONGO_URI")
    DATABASE_NAME: str = Field("LOCAL_RADAR", env="DATABASE_NAME")
    
    # Rate limiting settings
    RATE_LIMIT_CALLS: int = Field(10000, env="RATE_LIMIT_CALLS")
    RATE_LIMIT_PERIOD: int = Field(600, env="RATE_LIMIT_PERIOD")
    BLOCK_DURATION: int = Field(6000, env="BLOCK_DURATION")  # Temporary block for 10 minutes.
    PERMANENT_BLOCK_THRESHOULD: int = Field(30, env="PERMANENT_BLOCK_THRESHOULD") # After 3 offenses, permanent block.
    PERMANENT_BLOCK_DURATION: int = Field(864000, env="PERMANENT_BLOCK_DURATION") # Permanent block for 24 hours.
    
    # Redis settings (using Upstash Redis)
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: str = Field("", env="REDIS_PASSWORD")
    REDIS_SSL: bool = Field(False, env="REDIS_SSL")
    
    # JWT settings
    JWT_SECRET_KEY: str = Field("default_insecure_jwt_secret_change_me", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_TIME_MINUTES: int = Field(30, env="JWT_EXPIRATION_TIME_MINUTES")
    JWT_REFRESH_EXPIRATION_TIME_MINUTES: int = Field(1440, env="JWT_REFRESH_EXPIRATION_TIME_MINUTES")
    
    # Secure API key setting
    SECURE_API: str = Field("default_insecure_api_key_change_me", env="SECURE_API")
    
    # CORS settings
    CORS_ORIGINS: str = Field("http://localhost:3000,http://localhost:8000,https://local-radar.onrender.com,https://www.local-radar.onrender.com,https://www.localradar.tech,https://localradar.tech", env="CORS_ORIGINS")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse comma-separated CORS_ORIGINS into a list of strings."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def REDIS_URI(self) -> str:
        """
        Construct the Redis URI dynamically based on whether SSL is enabled
        and whether a password is provided.
        
        Returns:
            str: The full Redis URI.
        """
        protocol = "rediss" if self.REDIS_SSL else "redis"
        # If a password is provided, include it in the URI.
        if self.REDIS_PASSWORD:
            return f"{protocol}://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        else:
            return f"{protocol}://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()