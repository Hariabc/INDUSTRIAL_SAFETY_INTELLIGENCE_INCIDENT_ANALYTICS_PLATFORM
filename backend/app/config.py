from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Industrial Safety Intelligence Platform"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./industrial_safety.db"

    # Acknowledgement SLA in seconds
    ACK_SLA_CRITICAL_SECONDS: int = 300
    ACK_SLA_HIGH_SECONDS: int = 900
    ACK_SLA_MEDIUM_SECONDS: int = 1800
    ACK_SLA_LOW_SECONDS: int = 3600

    # Detection parameters
    ALARM_FLOOD_THRESHOLD: int = 10
    ALARM_FLOOD_WINDOW_MINUTES: int = 10
    REPEATED_UNSAFE_WINDOW_HOURS: int = 24
    REPEATED_UNSAFE_MIN_EVENTS: int = 3
    NUISANCE_ALARM_MIN_COUNT: int = 15
    NUISANCE_MAX_INCIDENT_RATE: float = 0.05

    # Generator defaults
    RANDOM_SEED: int = 20261022
    GEN_PLANTS: int = 4
    GEN_MACHINES: int = 60
    GEN_ALARMS: int = 200
    GEN_EVENTS: int = 50000
    GEN_DAYS: int = 30

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")


settings = Settings()
