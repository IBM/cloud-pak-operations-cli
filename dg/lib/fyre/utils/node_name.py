import re as regex

from typing import Optional

import click


def validate_node_name(ctx, param, value) -> Optional[str]:
    if value is not None and regex.match("(inf|(master|worker)\\d+)$", value) is None:
        raise click.BadParameter("Invalid node name")

    return value
