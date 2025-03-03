import os
from pathlib import Path
from typing import (
    List,
    Optional,
)

import yaml

from lib.cmd.ready import ScummvmStateEntry
from lib.exo.dc import ScummvmMeta
from lib.yag.scummvm import add_installer as scummvm_add_installer
from lib.yag.scummvm import copy_game_data as scummvm_copy_game_data

PORTS_DATA_DIR = Path(os.environ["PORTS_DATA_DIR"])
PORTS_SRC_DIR = Path(os.environ["PORTS_SRC_DIR"])
EXO_DATA_DIR = Path(os.environ["EXO_DATA_DIR"])


def extract_yaml_data(file_path: str) -> Optional[dict]:
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Error reading {file_path}: {e}")
            return None


def get_ports_metadata(ports_src_path: Path) -> List:
    res = []
    for root, _, files in os.walk(ports_src_path / "ports" / "games" / ""):
        for file in files:
            if file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                res.append(extract_yaml_data(file_path))
    return res


def get_platform_release(releases: List[ScummvmMeta.Entity], platform: str) -> Optional[ScummvmMeta.Entity]:
    for r in releases:
        if r.platform == platform:
            return r
    return None


def get_best_release(releases: List[ScummvmMeta.Entity]) -> Optional[ScummvmMeta.Entity]:
    preferred_platforms = ["Windows", "DOS"]
    for platform in preferred_platforms:
        release = get_platform_release(releases, platform)
        if release:
            return release
    return None


def add_scummvm_game(game: ScummvmStateEntry) -> None:
    release = get_best_release(game.releases)

    if release is None:
        print(f"Suitable release not found for {game.releases}")
        return
    scummvm_add_installer(game, release)
    scummvm_copy_game_data(game, release)
