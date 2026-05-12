from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # tells it automatically load values from .env file
    model_config = SettingsConfigDict(
        env_file=".env", # .env file is for storing sensitive configuration like secret keys that shouldn't go into source control
        env_file_encoding="utf-8",
    )

    database_url: str # we are not setting a default which means we either need to set up in our system or in our .env file

    secret_key: SecretStr # A special type that doesn't leak the value in logs or when we print it out; if it accidentantly gets printed, then we see a bunch of asterics instead of the actual value 
    algorithm: str = "HS256" # standard for JWT
    access_token_expire_minutes: int = 30

    max_upload_size_bytes: int = 5 * 1024 * 1024 # a default of 5 mega bytes; helps prevent the server from huge file uploads

    posts_per_page: int = 10 # This is to centralize the posts per page setting. This is because if we want to change the page size later, we can change it here.

    reset_token_expire_minutes: int = 60

    mail_server: str = "localhost"
    mail_port: int = 587
    mail_username: str = ""
    mail_password: SecretStr = SecretStr("")
    mail_from: str = "noreply@example.com"
    mail_use_tls: bool = True

    frontend_url: str = "http://localhost:8001" # we hardcode this instead of pulling it from the request data as request data can be manipulated by attackers

settings = Settings() # type: ignore[call-arg] # loaded from the .env file


# the secret key in system environment variables takes precedence over that in the .env file.
# in case there is no key in both environment variable and .env file, then the default (Defined for agorithm and expire_minutes) are considered.