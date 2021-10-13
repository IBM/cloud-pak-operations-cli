import click
import pkg_resources

from dg.utils.logging import loglevel_command


@loglevel_command()
@click.option("--shell", help="Shell name", required=True, type=click.Choice(["bash", "zsh"]))
def get_shell_completion_script_location(shell: str):
    """Get the location of the shell completion script"""

    click.echo(f'{pkg_resources.require("data-gate-cli")[0].location}/dg/deps/autocomplete/dg-autocomplete-{shell}.sh')
