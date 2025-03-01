import os
import uuid
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


def get_best_release(releases: List[ScummvmMeta.Entity]) -> ScummvmMeta.Entity:
    preferred_platforms = ["Windows", "DOS", "MacOS"]
    for platform in preferred_platforms:
        release = get_platform_release(releases, platform)
        if release:
            return release
    raise ValueError(f"No suitable release found: {releases}")


def add_scummvm_game(game: ScummvmStateEntry) -> None:
    release = get_best_release(game.releases)
    uuid_str = str(uuid.uuid4())
    scummvm_add_installer(game, release, uuid_str)
    scummvm_copy_game_data(game, release, uuid_str)
    print(
        f"curl --request POST \\\n"
        f"  --url http://portsvc.yag.dc:8087/ports/apps/{game.igdb.slug}/releases/{uuid_str} \\\n"
        f"  --header 'content-type: application/x-yaml' \\\n"
        f"  --header 'user-agent: vscode-restclient' \\\n"
        f"  --data-binary '@/workspaces/ports/ports/games/{game.igdb.slug}/{uuid_str}.yaml'"
    )
