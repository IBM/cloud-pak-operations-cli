import logging

from typing import Callable

import click


class ClickLoggingFormatter(logging.Formatter):
    """Click-based log formatter

    Instances of this formatter create colored log messages using the
    following format:

    YYYY-MM-DDThh:mm:ss±hhmm ["   DEBUG"|
                              "    INFO"|
                              " WARNING"|
                              "   ERROR"|
                              "CRITICAL"]: {message}
    """

    def __init__(self):
        super().__init__(
            datefmt="%Y-%m-%dT%H:%M:%S%z",
            fmt="%(asctime)s [%(levelname)8s]: %(message)s",
        )

    def format(self, record: logging.LogRecord) -> str:
        """Formats the given log record

        Parameters
        ----------
        record
            log record

        Returns
        -------
        str
            formatted log record message
        """

        colors = {
            "CRITICAL": dict(fg="magenta"),
            "DEBUG": dict(fg="blue"),
            "ERROR": dict(fg="red"),
            "WARNING": dict(fg="yellow"),
        }

        return (
            click.style(
                logging.Formatter.format(self, record), **colors[record.levelname]
            )
            if record.levelname in colors
            else logging.Formatter.format(self, record)
        )


class ClickLoggingHandler(logging.Handler):
    """Click-based log handler"""

    def emit(self, record: logging.LogRecord):
        """Prints the given log record using click.echo()

        Parameters
        ----------
        record
            log record
        """

        click.echo(self.format(record))


class ScopedLoggingDisabler:
    """Temprarily disables logging when used as part of a with statement"""

    def __init__(self, is_enabled=True) -> None:
        self._is_enabled = is_enabled
        self._previous_value = False

    def __enter__(self):
        if self._is_enabled:
            self._previous_value = logging.getLogger().disabled
            logging.getLogger().disabled = True

    def __exit__(self, exc_type, exc_value, traceback):
        if self._is_enabled:
            logging.getLogger().disabled = self._previous_value


def init_root_logger():
    """Initializes the root logger to use an instance of
    ClickLoggingFormatter as a formatter and an instance of
    ClickLoggingHandler as a handler"""

    click_logging_handler = ClickLoggingHandler()
    click_logging_handler.formatter = ClickLoggingFormatter()

    logging.getLogger().handlers = [click_logging_handler]


def loglevel_command(name=None, default_log_level="INFO", **attrs):
    """Decorator creating a click.Command object with a --loglevel option

    Parameters
    ----------
    name
        command name
    default_log_level
        default log level
    """

    def decorator(f):
        command = click.command(
            name, cls=_getClickCommandWithLogLevelOption(default_log_level), **attrs
        )(f)

        return command

    return decorator


def loglevel_option(default_log_level="INFO") -> Callable:
    """Decorator adding a --loglevel option to a Click command

    Parameters
    ----------
    default_log_level
        default log level
    """

    return click.option(
        "--loglevel",
        callback=lambda ctx, param, value: logging.getLogger().setLevel(value),
        default=default_log_level,
        expose_value=False,
        help="Log level",
        is_eager=True,
        type=click.Choice(
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
        ),
    )


def _getClickCommandWithLogLevelOption(default_log_level: str) -> type[click.Command]:
    """Creates a definition of a subclass of click.Command

    This method creates a definition of a subclass of click.Command. Click
    commands based on this subclass have a --loglevel option.

    Parameters
    ----------
    default_log_level
        default log level set when executing a command

    Returns
    -------
    click.Command
        Definition of a subclass of click.Command
    """

    class ClickCommandWithLogLevelOption(click.Command):
        """Click command with a --loglevel option"""

        def __init__(self, *args, **kwargs):
            """Constructor

            Appends a --loglevel option"""

            super().__init__(*args, **kwargs)

            option = click.Option(
                ["--loglevel"],
                callback=lambda ctx, param, value: logging.getLogger().setLevel(value),
                default=default_log_level,
                expose_value=False,
                help="Log level",
                is_eager=True,
                type=click.Choice(
                    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    case_sensitive=False,
                ),
            )

            self.params.append(option)

    return ClickCommandWithLogLevelOption
