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


class Export:
    def __init__(self, name: str, type: str, **kwargs):
        self.name = name
        self.type = type
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"Export(name='{self.name}')"


class Preset:
    def __init__(self, name: str, exports: list[dict], **kwargs):
        self.name = name
        self.exports = [Export(**export) for export in exports]
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"Preset(name={self.name})"


class Push:
    def __init__(self, name: str, app: str, enabled: bool = True, **kwargs):
        self.name = name
        self.app = app
        self.enabled = enabled
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"Push(app='{self.app}', enabled={self.enabled})"


class Config:
    def __init__(
        self,
        targets: List[Target],
        presets: List[Preset],
        pushes: List[Push],
    ):
        self.targets = targets
        self.presets = presets
        self.pushes = pushes

    def get_preset(self, name: str) -> Preset | None:
        for preset in self.presets:
            if preset.name == name:
                return preset
        return None

    @staticmethod
    def from_json(json_content: str) -> "Config":
        data = json.loads(json_content)

        targets = [Target(**target) for target in data.get("targets", [])]
        presets = [Preset(**preset) for preset in data.get("presets", [])]
        pushes = [Push(**push) for push in data.get("pushes", [])]

        return Config(targets, presets, pushes)

    def to_json(self) -> str:
        return json.dumps(
            {
                "targets": [target.__dict__ for target in self.targets],
                "presets": [preset.__dict__ for preset in self.presets],
                "pushes": [push.__dict__ for push in self.pushes],
            },
            indent=2,
        )
