import json
from typing import List, Dict


class Target:
    def __init__(self, preset: str, name: str, manifest: str, interval: int = 0):
        self.preset = preset
        self.name = name
        self.manifest = manifest
        self.interval = interval

    def __repr__(self):
        return f"Target(preset='{self.preset}', name='{self.name}')"


class Preset:
    def __init__(self, export: str):
        self.export = export

    def __repr__(self):
        return f"Preset(export={self.export})"


class Config:
    def __init__(self, targets: List[Target], presets: Dict[str, Preset]):
        self.targets = targets
        self.presets = presets

    def get_preset(self, name: str) -> Preset:
        return self.presets.get(name)

    @staticmethod
    def from_json(json_content: str) -> "Config":
        data = json.loads(json_content)

        # Parse targets
        targets = [Target(**target) for target in data.get("targets", [])]

        # Parse presets
        presets = {
            key: Preset(**value) for key, value in data.get("presets", {}).items()
        }

        return Config(targets, presets)

    def to_json(self) -> str:
        return json.dumps(
            {
                "targets": [target.__dict__ for target in self.targets],
                "presets": {
                    key: preset.__dict__ for key, preset in self.presets.items()
                },
            },
            indent=2,
        )
