import json
import os
import random
from pathlib import Path
from typing import (
    List,
    Optional,
)

from lib.cmd.ready import ScummvmStateEntry
from lib.cmd.ready import run as run_ready
from lib.runner import Runner
from lib.yag.ports import (
    add_scummvm_game,
    get_best_release,
)

EXO_DATA_DIR = Path(os.environ["EXO_DATA_DIR"])
SCRAPERS_DATA_DIR = Path(os.environ["SCRAPERS_DATA_DIR"])
DISCORD_HOOK_YAG_NEW_RELEASES_CHANNEL = os.environ["DISCORD_HOOK_YAG_NEW_RELEASES_CHANNEL"]

PREPARE_GAMES_LIMIT = 10


def prepare_scummvm_games() -> None:
    def get_good_scummvm_games(entries: List[ScummvmStateEntry], limit: int) -> List[ScummvmStateEntry]:
        filtered_entries = []
        for entry in entries:
            best_release = get_best_release(entry.releases)
            if (
                (entry.igdb.title_sim_ratio > 0.9)
                and (not entry.in_ports)
                and (entry.release_year < 2000)
                and (entry.igdb.publisher is not None)
                and (best_release is not None)
                and (best_release.has_menu is False)
            ):
                filtered_entries.append(entry)
        # return random subset to avoid alphabetical bias
        return random.sample(filtered_entries, min(limit, len(filtered_entries)))

    with open(EXO_DATA_DIR / "tmp" / "scummvm-state.json", "r", encoding="utf-8") as f:
        all_games = [ScummvmStateEntry.Schema().load(entry) for entry in json.load(f)]
        good_games = get_good_scummvm_games(all_games, limit=PREPARE_GAMES_LIMIT)
        for game in good_games:
            add_scummvm_game(game)
        for game in good_games:
            print(
                f"curl --request POST \\\n"
                f"  --url http://portsvc.yag.dc:8087/ports/apps/{game.igdb.slug}/releases/{game.uuid} \\\n"
                f"  --header 'content-type: application/x-yaml' \\\n"
                f"  --header 'user-agent: vscode-restclient' \\\n"
                f"  --data-binary '@/workspaces/ports/ports/games/{game.igdb.slug}/{game.uuid}.yaml'\n"
            )
        for game in good_games:
            print(f"./publish.sh {game.igdb.slug} {game.uuid}\n")
        for game in good_games:
            print(
                f'curl -X POST "{DISCORD_HOOK_YAG_NEW_RELEASES_CHANNEL}" \\\n'
                f'     -H "Content-Type: application/json" \\\n'
                f'     -d \'{{"content": "https://yag.im/games/{game.uuid}/{game.igdb.slug}"}}\'\n'
            )


def run(runner: Optional[Runner]) -> None:
    run_ready(runner)
    if runner == Runner.SCUMMVM:
        prepare_scummvm_games()
    elif runner == Runner.DOS:
        pass
    elif runner == Runner.WIN3X:
        pass
    else:
        prepare_scummvm_games()
        pass
