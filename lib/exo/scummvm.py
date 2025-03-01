import os
import zipfile
from pathlib import Path
from typing import (
    List,
    Optional,
)

import defusedxml.ElementTree as ET

from lib.exo.dc import (
    GameMeta0,
    GameMeta1,
    GameMeta2,
    ScummvmMeta,
)
from lib.util import CaseInsensitiveDict


def _extract_platform(path_part: str) -> Optional[str]:
    platforms = {
        "Acorn",
        "Advsys",
        "Amiga",
        "Amstrad",
        "Apple II",
        "Atari ST",
        "C64",
        "CPC",
        "DOS",
        "IF",
        "FM-Towns",
        "Mac",
        "Macintosh",
        "Multi-Platform",
        "PC-98",
        "PS1",
        "ScummC",
        "ScummGEN",
        "Sega",
        "Windows",
        "ZCode",
        "ZX Spectrum",
    }
    return next((platform for platform in platforms if platform.lower() in path_part.lower()), None)


def _extract_distro_format(path_part: str) -> Optional[str]:
    distros = {"CD", "DVD", "Floppy"}
    return next((distro for distro in distros if distro.lower() in path_part.lower()), None)


def _parse_XOScummVMMetadata(zip_path: Path) -> List[GameMeta1]:  # pylint: disable=invalid-name
    xml_files = {
        "xml/all/ScummVM.xml",
        "xml/all/ScummVM SVN.xml",
    }
    res = []
    for xml_file in xml_files:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            with zip_ref.open(xml_file) as f:
                tree = ET.parse(f)
                root = tree.getroot()
                for game in root.findall("Game"):
                    if game.findtext("Title") == "eXoScummVM":
                        # Setup eXoScummVM.bat "game". A bug?
                        continue
                    res.append(
                        GameMeta1(
                            game.findtext("RootFolder").split("\\")[-1],
                            game.findtext("Title"),
                            game.findtext("Publisher"),
                            game.findtext("Rating"),
                            int(game.findtext("ReleaseYear")),
                            game.findtext("Genre").split("; "),
                        )
                    )
    return res


def _parse_utilSVM(zip_path: Path) -> List[GameMeta2]:  # pylint: disable=invalid-name
    res = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        with zip_ref.open("scummvm.txt") as f:
            for line in f:
                line_parts = line.decode("utf-8", errors="ignore").strip().split(";")
                scummvm_ver_parts = line_parts[2].split("\\")
                scummvm_ver = scummvm_ver_parts[0] if len(scummvm_ver_parts) == 2 else None
                res.append(
                    GameMeta2(
                        str(line_parts[0]),
                        str(line_parts[1]),
                        str(scummvm_ver),
                    )
                )
    return res


def _parse_eXoScummVM(root_dir: Path) -> List[GameMeta0]:  # pylint: disable=invalid-name
    res = []
    zip_files = [f for f in os.listdir(root_dir) if f.endswith(".zip")]
    for zip_file in zip_files:
        zip_path = os.path.join(root_dir, zip_file)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            file_list = set(zip_ref.namelist())
            game_meta0 = GameMeta0("", [])
            for file_path in file_list:
                # matching only paths like e.g.: /1.5 Ritter (Windows)/1.5 Ritter (Windows)/
                if file_path.endswith("/"):
                    path_parts = file_path.strip("/").split("/")
                    if len(path_parts) != 2:
                        continue
                    has_menu = file_path + "menu.txt" in file_list
                    platform = _extract_platform(path_parts[1]) or _extract_platform(path_parts[0])
                    distro_fmt = _extract_distro_format(path_parts[1]) or _extract_distro_format(path_parts[0])
                    child_part = path_parts[1]
                    game_meta0.releases.append(GameMeta0.Entity(child_part, has_menu, platform, distro_fmt))
                    game_meta0.parent_part = path_parts[0]
            res.append(game_meta0)
    return res


def _upd_releases(meta_arr: List[ScummvmMeta], meta2_arr: List[GameMeta2]) -> None:
    releases_dict = CaseInsensitiveDict({})
    for m in meta_arr:
        for ix, r in enumerate(m.releases):
            releases_dict[r.child_part] = (m.parent_part, ix)

    meta_dict = CaseInsensitiveDict({m.parent_part: m for m in meta_arr})

    for m2 in meta2_arr:
        if (m2.parent_part not in releases_dict) and (m2.parent_part not in meta_dict):
            print(f"ERROR: entry is present only in scummvm.txt: {m2.parent_part}")
            continue
        if m2.parent_part in meta_dict:
            continue
        release_descr = releases_dict[m2.parent_part]
        release: ScummvmMeta.Entity = meta_dict[release_descr[0]].releases[release_descr[1]]
        release.scummvm_game = m2.scummvm_game
        release.scummvm_ver = m2.scummvm_ver


def get_meta(data_path: Path) -> List[ScummvmMeta]:
    meta0_arr = _parse_eXoScummVM(data_path / "eXoScummVM" / "eXo" / "eXoScummVM")
    meta1_arr = _parse_XOScummVMMetadata(data_path / "eXoScummVM" / "Content" / "XOScummVMMetadata.zip")
    meta2_arr = _parse_utilSVM(data_path / "eXoScummVM" / "eXo" / "util" / "utilSVM.zip")

    meta1_dict: CaseInsensitiveDict = CaseInsensitiveDict({meta1.parent_part: meta1 for meta1 in meta1_arr})
    meta2_dict: CaseInsensitiveDict = CaseInsensitiveDict({meta2.parent_part: meta2 for meta2 in meta2_arr})

    res = []

    for meta0 in meta0_arr:
        scummvm_game = None
        scummvm_ver = None
        meta2: Optional[GameMeta2] = meta2_dict.get(meta0.parent_part)
        if meta2:
            scummvm_game = meta2.scummvm_game
            scummvm_ver = meta2.scummvm_ver
        else:
            print(f"ERROR: entry is absent in scummvm.txt: {meta0.parent_part}")
            continue
        meta1: Optional[GameMeta1] = meta1_dict.get(meta0.parent_part)
        if meta1:
            meta = ScummvmMeta(
                parent_part=meta0.parent_part,
                title=meta1.title,
                publisher=meta1.publisher,
                rating=meta1.rating,
                release_year=meta1.release_year,
                genre=meta1.genre,
                releases=[
                    ScummvmMeta.Entity(**vars(entity), scummvm_game=None, scummvm_ver=None) for entity in meta0.releases
                ],
                scummvm_game=scummvm_game,
                scummvm_ver=scummvm_ver,
            )
            res.append(meta)
        else:
            print(f"ERROR: entry is absent in scummvm.xml: {meta0.parent_part}")

    _upd_releases(res, meta2_arr)

    return res
