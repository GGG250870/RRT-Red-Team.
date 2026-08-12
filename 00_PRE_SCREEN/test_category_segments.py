#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    pre_screen = load_module("00_PRE_SCREEN/pre_screen.py", "pre_screen")
    build_batch = load_module("00_PRE_SCREEN/build_batch.py", "build_batch")

    assert pre_screen.infer_target_segment("ristorazione", "menu degustazione chef michelin") == "fine_dining"
    assert pre_screen.infer_target_segment("ristorazione", "pizzeria forno a legna impasto") == "pizzeria"
    assert pre_screen.infer_target_segment("ristorazione", "trattoria cucina tradizionale") == "trattoria_osteria"
    assert pre_screen.infer_target_segment("ristorazione", "prenota il tuo tavolo") == "ristorazione_generic"

    assert build_batch.normalize_target_segment("ristorazione", "pizza") == "pizzeria"
    assert build_batch.normalize_target_segment("ristorazione", "alta_cucina") == "fine_dining"
    assert "tripadvisor.it" in build_batch.review_portals_for("ristorazione", "pizzeria")
    assert "michelin.com" in build_batch.review_portals_for("ristorazione", "fine_dining")

    print(json.dumps({"status": "PASS", "tests": 1}))


if __name__ == "__main__":
    main()
