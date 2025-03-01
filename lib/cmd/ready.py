import json
import os
from pathlib import Path
from typing import (
    List,
    Optional,
)

from lib.cmd.dc import ScummvmStateEntry
from lib.exo.scummvm import ScummvmMeta
from lib.exo.scummvm import get_meta as get_scummvm_meta
from lib.runner import Runner
from lib.util import (
    CaseInsensitiveDict,
    get_similar_string,
)
from lib.yag.igdb import IgdbGame
from lib.yag.igdb import get_data as get_igdb_data
from lib.yag.ports import get_ports_metadata as get_ports_data

EXO_DATA_DIR = Path(os.environ["EXO_DATA_DIR"])
PORTS_SRC_DIR = Path(os.environ["PORTS_SRC_DIR"])
SCRAPERS_DATA_DIR = Path(os.environ["SCRAPERS_DATA_DIR"])


# merger
def gen_scummvm_state(igdb_data: List[IgdbGame], ports_meta: List[dict]) -> None:
    scummvm_meta: List[ScummvmMeta] = get_scummvm_meta(Path(EXO_DATA_DIR))
    final_res: List[ScummvmStateEntry] = []
    igdb_titles_set = set({game.name.lower() for game in igdb_data})
    igdb_titles_dict = CaseInsensitiveDict({game.name: game for game in igdb_data})
    ports_slugs_dict = CaseInsensitiveDict({port["descr"]["igdb_slug"]: port for port in ports_meta})
    for sm in scummvm_meta:
        sim = get_similar_string(sm.title.lower(), igdb_titles_set)
        igdb_entry: IgdbGame = igdb_titles_dict[sim[0]]
        ports_entry = ports_slugs_dict.get(igdb_entry.slug, None)
        fin_entry = ScummvmStateEntry(
            **vars(sm),
            igdb=ScummvmStateEntry.IgdbMeta(
                slug=igdb_entry.slug,
                name=igdb_entry.name,
                title_sim_ratio=sim[1],
                publisher=igdb_entry.publisher,
            ),
            in_ports=ports_entry is not None,
            ports_year=ports_entry["descr"]["year_released"] if ports_entry else None,
        )
        final_res.append(fin_entry)
        final_res = sorted(final_res, key=lambda fr: fr.title.lower())
    with open(EXO_DATA_DIR / "tmp" / "scummvm-state.json", "w", encoding="utf-8") as f:
        json.dump([ScummvmStateEntry.Schema().dump(fr) for fr in final_res], f, indent=4)


def run(runner: Optional[Runner]) -> None:
    ports_meta = get_ports_data(Path(PORTS_SRC_DIR))
    igdb_data = get_igdb_data(Path(SCRAPERS_DATA_DIR))
    if runner == Runner.SCUMMVM:
        gen_scummvm_state(igdb_data, ports_meta)
    elif runner == Runner.DOS:
        pass
    elif runner == Runner.WIN3X:
        pass
    else:
        gen_scummvm_state(igdb_data, ports_meta)
        pass
