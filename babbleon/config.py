from pathlib import Path
import json


class BabbleonConfig:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = json.load(self.config_path.open())

    def get_reference_file(self) -> Path:
        return Path(self.config["reference"])

    def get_output_dir(self) -> Path:
        return Path(self.config["output"])

    def get_output_format(self) -> str:
        return self.config["output_format"]

    def get_target_languages(self) -> list[str]:
        return self.config["languages"]
