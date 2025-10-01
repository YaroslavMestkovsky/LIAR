import yaml


def get_configs(config_path: str, config_params: dict) -> list:
    """Загрузка конфига."""

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
        configs = []

        for config_class, parts in config_params.items():
            params = {}

            for part in parts:
                params.update(**config_data[part])

            configs.append(config_class(**params))

        return configs
