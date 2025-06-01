import json
from typing import List, Dict


class Target:
    def __init__(
        self, preset: str, name: str, manifest: str, interval: int = 0, **kwargs
    ):
        self.preset = preset
        self.name = name
        self.manifest = manifest
        self.interval = interval
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"Target(preset='{self.preset}', name='{self.name}')"


class Preset:
    def __init__(self, export: str, **kwargs):
        self.export = export
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"Preset(export={self.export})"


class Push:
    def __init__(self, name: str, app: str, enabled: bool = True, **kwargs):
        self.name = name
        self.app = app
        self.enabled = enabled
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"PushConfig(app='{self.app}', enabled={self.enabled})"


class Config:
    def __init__(
        self,
        targets: List[Target],
        presets: Dict[str, Preset],
        pushes: List[Push],
    ):
        self.targets = targets
        self.presets = presets
        self.pushes = pushes

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

        pushes = [Push(**push) for push in data.get("pushes", [])]

        return Config(targets, presets, pushes)

    def to_json(self) -> str:
        return json.dumps(
            {
                "targets": [target.__dict__ for target in self.targets],
                "presets": {
                    key: preset.__dict__ for key, preset in self.presets.items()
                },
                "pushes": [push.__dict__ for push in self.pushes],
            },
            indent=2,
        )
