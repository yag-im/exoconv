import uuid
from dataclasses import field
from typing import (
    ClassVar,
    Optional,
    Type,
)

from marshmallow import Schema
from marshmallow_dataclass import dataclass

from lib.exo.dc import ScummvmMeta


@dataclass
class ScummvmStateEntry(ScummvmMeta):
    @dataclass
    class IgdbMeta:
        slug: str
        name: str
        title_sim_ratio: float
        publisher: Optional[str]

    igdb: IgdbMeta
    in_ports: bool
    ports_year: Optional[int]
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    Schema: ClassVar[Type[Schema]] = Schema  # pylint: disable=invalid-name
