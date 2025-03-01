import json
import os
from itertools import islice
from pathlib import Path
from typing import (
    List,
    Optional,
)

from lib.cmd.ready import ScummvmStateEntry
from lib.runner import Runner
from lib.yag.ports import add_scummvm_game

EXO_DATA_DIR = Path(os.environ["EXO_DATA_DIR"])
SCRAPERS_DATA_DIR = Path(os.environ["SCRAPERS_DATA_DIR"])

PREPARE_GAMES_LIMIT = 1


def prepare_scummvm_games() -> None:
    def get_good_scummvm_games(entieies: List[ScummvmStateEntry], limit: int) -> List[ScummvmStateEntry]:
        res = (
            entry
            for entry in entieies
            if (entry.igdb.title_sim_ratio > 0.9)
            and (not entry.in_ports)
            and (entry.release_year < 2000)
            and (entry.igdb.publisher is not None)
        )
        return list(islice(res, limit))

    with open(EXO_DATA_DIR / "tmp" / "scummvm-state.json", "r", encoding="utf-8") as f:
        all_games = [ScummvmStateEntry.Schema().load(entry) for entry in json.load(f)]
        good_games = get_good_scummvm_games(all_games, limit=PREPARE_GAMES_LIMIT)
        for gg in good_games:
            add_scummvm_game(gg)


def run(runner: Optional[Runner]) -> None:
    if runner == Runner.SCUMMVM:
        prepare_scummvm_games()
    elif runner == Runner.DOS:
        pass
    elif runner == Runner.WIN3X:
        pass
    else:
        prepare_scummvm_games()
        pass
