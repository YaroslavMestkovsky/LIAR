from dataclasses import dataclass

import yaml


@dataclass
class FastAPIConfig:
    host: str
    port: int
    debug: bool


def get_config(config_path: str = ".configs/fast_api.yaml") -> FastAPIConfig:
    """Загрузка конфига."""

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

        return FastAPIConfig(**config_data["web"])
