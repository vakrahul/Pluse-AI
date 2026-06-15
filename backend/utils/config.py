from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "healthcare_analytics"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    cubejs_api_url: str = "http://localhost:4000/cubejs-api/v1"
    cubejs_api_secret: str = "healthcare_cube_secret_change_in_prod"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    jwt_secret: str = "change_me_in_production"
    redis_url: str = "redis://localhost:6379"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4jpassword"

    chroma_persist_dir: str = "./chroma_data"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
