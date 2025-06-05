from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # MongoDB settings
    MONGO_URI: str = Field("mongodb+srv://vasramdev:42PlTKupaU9f5Dhh@cluster0.aydnalb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", env="MONGO_URI")
    DATABASE_NAME: str = Field("LOCAL_RADAR", env="DATABASE_NAME")
    
    
    # Rate limiting settings
    RATE_LIMIT_CALLS: int = Field(10000, env="RATE_LIMIT_CALLS")
    RATE_LIMIT_PERIOD: int = Field(600, env="RATE_LIMIT_PERIOD")
    BLOCK_DURATION: int = Field(6000, env="BLOCK_DURATION")  # Temporary block for 10 minutes.
    PERMANENT_BLOCK_THRESHOULD: int = Field(30, env="PERMANENT_BLOCK_THRESHOULD") # After 3 offenses, permanent block.
    PERMANENT_BLOCK_DURATION: int = Field(864000, ev="PERMANENT_BLOCK_DURATION") # Permanent block for 24 hours.
    
    # Redis settings (using Upstash Redis)
    REDIS_HOST: str = Field("settling-cricket-44286.upstash.io", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: str = Field('Aaz-AAIjcDE0NzViZWJhMmVkYjg0YWE1OGZiNTI4Yzc1ZGQ3Y2Q1MXAxMA', env="REDIS_PASSWORD")
    REDIS_SSL: bool = Field(True, env="REDIS_SSL")
    
    # JWT settings
    JWT_SECRET_KEY: str = Field("5bae84a9c6b30c422a3e1627a74da01f26713939dfabdae0e8c5a182c9020283", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_TIME_MINUTES: int = Field(30, env="JWT_EXPIRATION_TIME_MINUTES")
    JWT_REFRESH_EXPIRATION_TIME_MINUTES: int = Field(1440, env="JWT_REFRESH_EXPIRATION_TIME_MINUTES")
    
    # Secure API key setting
    SECURE_API: str = Field("A9x2GzQ7mS4pL1r0", env="SECURE_API")
    
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