from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str = "dev-token-change-me"
    influxdb_org: str = "performance-lab"
    influxdb_bucket: str = "performance_lab"
    grafana_final_cut_url: str = ""
    grafana_logic_pro_url: str = ""
    grafana_xcode_url: str = ""
    mock_repos_dir: str = "repos"
    cors_origins: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
