import json
from dataclasses import (
    field,
)
from pathlib import Path
from typing import (
    ClassVar,
    List,
    Optional,
    Type,
)

from marshmallow import Schema
from marshmallow_dataclass import dataclass


@dataclass
class IgdbCompany:
    id: int
    name: str


@dataclass
class IgdbGame:
    slug: str
    name: str
    publisher: Optional[str]
    genres: List[dict] = field(default_factory=list)
    platforms: List[int] = field(default_factory=list)
    Schema: ClassVar[Type[Schema]] = Schema  # pylint: disable=invalid-name


def get_data(data_path: Path) -> List[IgdbGame]:
    companies = []
    with open(data_path / "igdb" / "companies.json", "r", encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)
        for item in data:
            companies.append(
                IgdbCompany(
                    id=item["id"],
                    name=item["name"],
                )
            )
    companies_dict = {company.id: company.name for company in companies}

    games = []
    with open(data_path / "igdb" / "games.json", "r", encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)
        for item in data:
            publisher = next((comp for comp in item.get("involved_companies", []) if comp.get("publisher", True)), None)
            games.append(
                IgdbGame(
                    slug=item.get("slug"),
                    name=item["name"],
                    publisher=companies_dict[publisher["company"]] if publisher else None,
                    genres=[g["name"] for g in item.get("genres", [])],
                    platforms=item.get("platforms", []),
                )
            )

    return games
