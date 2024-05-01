from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    mongo_host: str = "mongodb://localhost:27017/"
    mongo_database: str = "college_project"
    mongo_username: str
    mongo_password: str

    jwt_signing_secret_key: str
    jwt_signing_algorithm: str = "HS256"

    root_user_email: str
    root_user_full_name: str
    root_user_password: str

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_from_name: str = "College Project"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True
    mail_template_folder: str = "templates"


settings = Settings() # type: ignore

