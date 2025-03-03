import os
import stat
import zipfile
from datetime import datetime
from pathlib import Path

import yaml

from lib.cmd.ready import ScummvmStateEntry
from lib.exo.dc import ScummvmMeta
from lib.util import (
    map_yag_platform,
    template,
)

PORTS_DATA_DIR = Path(os.environ["PORTS_DATA_DIR"])
PORTS_SRC_DIR = Path(os.environ["PORTS_SRC_DIR"])
EXO_DATA_DIR = Path(os.environ["EXO_DATA_DIR"])

GAME_LANG = "en"
SCUMMVM_VER = "2.9.0"
TZ = "America/Los_Angeles"


def add_installer(game: ScummvmStateEntry, release: ScummvmMeta.Entity) -> None:
    with open(PORTS_SRC_DIR / "scripts" / "templates" / "release.yaml.tmpl", "r", encoding="utf-8") as f:
        game_card = yaml.safe_load(f)
    game_card["descr"]["distro"]["url"] = "changeme"
    game_card["descr"]["distro"]["files"] = ["changeme"]
    game_card["descr"]["distro"]["format"] = "exoscummvm"
    game_card["descr"]["igdb_slug"] = game.igdb.slug
    game_card["descr"]["lang"] = GAME_LANG
    game_card["descr"]["name"] = game.igdb.name
    game_card["descr"]["platform"] = map_yag_platform(release.platform)
    game_card["descr"]["publisher"] = game.igdb.publisher
    game_card["descr"]["reqs"] = {
        "color_bits": 8,
        "midi": False,
        "screen_height": 480,
        "screen_width": 640,
        "ua": {"lock_pointer": False},
    }
    game_card["descr"]["runner"] = {"name": "scummvm", "ver": SCUMMVM_VER}
    game_card["descr"]["year_released"] = game.release_year
    game_card["descr"]["uuid"] = game.uuid
    game_card["descr"]["ts_added"] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")}{TZ}'
    yaml.SafeDumper.add_representer(
        type(None), lambda dumper, value: dumper.represent_scalar("tag:yaml.org,2002:null", "")
    )
    install_script_dir = PORTS_SRC_DIR / "ports" / "games" / game.igdb.slug
    install_script_dir.mkdir(parents=True, exist_ok=True)
    with open(install_script_dir / f"{game.uuid}.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(game_card, f, default_flow_style=False)


def copy_run_scripts(game: ScummvmStateEntry, game_dir: Path) -> None:
    tmpl_params = {
        "filtering": "true",
        "fullscreen": "true",
        "subtitles": "true",
    }
    template(
        PORTS_SRC_DIR / "lib" / "scummvm" / "templates" / "scummvm.ini.tmpl",
        game_dir / "scummvm.ini",
        params=tmpl_params,
    )

    tmpl_params = {
        "config": "scummvm.ini",
        "game": game.scummvm_game,
        "path": "./APP",
        "save_path": "./APP",
        "lang": GAME_LANG,
    }
    output_path = game_dir / "run.sh"
    template(PORTS_SRC_DIR / "lib" / "scummvm" / "templates" / "run.sh.tmpl", output_path, params=tmpl_params)
    output_path.chmod(output_path.stat().st_mode | stat.S_IEXEC)


def copy_game_data(game: ScummvmStateEntry, release: ScummvmMeta.Entity) -> None:
    game_dir = PORTS_DATA_DIR / "apps" / game.igdb.slug / game.uuid
    app_dir = game_dir / "APP"
    app_dir.mkdir(parents=True, exist_ok=True)
    zip_path = EXO_DATA_DIR / "eXoScummVM" / "eXo" / "eXoScummVM" / f"{game.parent_part}.zip"
    zipped_file_prefix = f"{game.parent_part}/{release.child_part}/"
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.namelist():
            if member.startswith(zipped_file_prefix) and len(member) > len(zipped_file_prefix):
                target_path = app_dir / member[len(zipped_file_prefix) :]
                if member.endswith("/"):
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    with zip_ref.open(member) as source, open(target_path, "wb") as target:
                        target.write(source.read())
    copy_run_scripts(game, game_dir)
