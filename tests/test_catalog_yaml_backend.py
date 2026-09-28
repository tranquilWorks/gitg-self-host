"""Native YAML parsing must preserve every released catalog value and fail safely."""

from pathlib import Path

import pytest
import yaml

from growth.domain.practice_content import PracticeContentError, _read_yaml

ROOT = Path(__file__).resolve().parents[1]


def test_native_safe_loader_preserves_every_catalog_yaml_document():
    for path in sorted((ROOT / "data/practices").rglob("*.yaml")):
        assert _read_yaml(path) == yaml.safe_load(path.read_text()), path


@pytest.mark.parametrize("native", [True, False])
def test_yaml_backend_rejects_python_object_construction(tmp_path, monkeypatch, native):
    if not native:
        monkeypatch.delattr(yaml, "CSafeLoader", raising=False)
    path = tmp_path / "unsafe.yaml"
    path.write_text("!!python/object/apply:builtins.str ['unsafe']")
    with pytest.raises(PracticeContentError, match="valid YAML"):
        _read_yaml(path)


def test_python_safe_loader_fallback_is_supported(tmp_path, monkeypatch):
    monkeypatch.delattr(yaml, "CSafeLoader", raising=False)
    path = tmp_path / "document.yaml"
    path.write_text("competency: '01.01'\nvalues: [true, null, 3]\n")
    assert _read_yaml(path) == {"competency": "01.01", "values": [True, None, 3]}
