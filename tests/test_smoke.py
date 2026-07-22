def test_package_imports():
    import importlib
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

    module = importlib.import_module("codeharness")
    assert module is not None
