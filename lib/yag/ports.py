import os
from pathlib import Path
from typing import (
    List,
    Optional,
    Tuple,
)

import yaml

from lib.cmd.ready import ScummvmStateEntry
from lib.const import (
    SUPPORTED_DISTRO_FORMATS,
    SUPPORTED_PLATFORMS,
)
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


def candidate_priority(release: ScummvmMeta.Entity) -> Tuple[int, int]:
    preferred_platforms = SUPPORTED_PLATFORMS
    preferred_distro_formats = SUPPORTED_DISTRO_FORMATS
    distro_rank = (
        preferred_distro_formats.index(release.distro_format)
        if release.distro_format in preferred_distro_formats
        else len(preferred_distro_formats)
    )
    platform_rank = (
        preferred_platforms.index(release.platform)
        if release.platform in preferred_platforms
        else len(preferred_platforms)
    )
    return (distro_rank, platform_rank)


def get_best_release(releases: List[ScummvmMeta.Entity]) -> Optional[ScummvmMeta.Entity]:
    releases = sorted(releases, key=candidate_priority)
    if releases[0].platform in SUPPORTED_PLATFORMS:
        return releases[0]
    return None


def add_scummvm_game(game: ScummvmStateEntry) -> None:
    release = get_best_release(game.releases)

    if release is None:
        print(f"Suitable release not found for {game.releases}")
        return
    scummvm_add_installer(game, release)
    scummvm_copy_game_data(game, release)
