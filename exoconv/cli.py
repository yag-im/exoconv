import click

from lib.cmd.ready import run as run_ready
from lib.cmd.steady import run as run_steady
from lib.runner import Runner


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--runner", type=click.Choice([runner.value for runner in Runner], case_sensitive=False), required=False)
def ready(runner: str) -> int:
    run_ready(Runner(runner) if runner else None)
    return 0


@cli.command()
@click.option("--runner", type=click.Choice([runner.value for runner in Runner], case_sensitive=False), required=False)
def steady(runner: str) -> int:
    run_steady(Runner(runner) if runner else None)
    return 0


if __name__ == "__main__":
    cli()
