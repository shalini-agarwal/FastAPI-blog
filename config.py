from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # tells it automatically load values from .env file
    model_config = SettingsConfigDict(
        env_file=".env", # .env file is for storing sensitive configuration like secret keys that shouldn't go into source control
        env_file_encoding="utf-8",
    )

    secret_key: SecretStr # A special type that doesn't leak the value in logs or when we print it out; if it accidentantly gets printed, then we see a bunch of asterics instead of the actual value 
    algorithm: str = "HS256" # standard for JWT
    access_token_expire_minutes: int = 30

settings = Settings() # loaded from the .env file


# the secret key in system environment variables takes precedence over that in the .env file.
# in case there is no key in both environment variable and .env file, then the default (Defined for agorithm and expire_minutes) are considered.