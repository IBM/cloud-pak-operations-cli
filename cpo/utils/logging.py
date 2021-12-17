#  Copyright 2021 IBM Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging

from typing import Any, Callable, Optional, Type

import click

from halo import Halo


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
            click.style(logging.Formatter.format(self, record), **colors[record.levelname])
            if record.levelname in colors
            else logging.Formatter.format(self, record)
        )


class ClickLoggingHandler(logging.Handler):
    """Click-based log handler"""

    def __init__(self):
        super().__init__()
        self._spinner: Optional[Halo] = None

    def emit(self, record: logging.LogRecord):
        """Prints the given log record using click.echo()

        Parameters
        ----------
        record
            log record
        """

        spinner_was_running = self._spinner is not None and self._spinner.spinner_id is not None

        if self._spinner is not None:
            self._spinner.stop()

        click.echo(self.format(record))

        if self._spinner is not None and spinner_was_running:
            self._spinner.start()

    def reset_spinner(self):
        self._spinner = None

    def set_spinner(self, spinner: Halo):
        self._spinner = spinner


class ScopedLoggingDisabler:
    """Temporarily disables logging when used as part of a with statement"""

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


class ScopedSpinnerDisabler:
    def __init__(self, click_logging_handler: ClickLoggingHandler, spinner: Halo):
        self._click_logging_handler = click_logging_handler
        self._spinner = spinner

    def __enter__(self):
        self._click_logging_handler.set_spinner(self._spinner)

    def __exit__(self, exc_type, exc_value, traceback):
        self.reset_spinner()

    def reset_spinner(self):
        self._click_logging_handler.reset_spinner()


def init_root_logger() -> ClickLoggingHandler:
    """Initializes the root logger to use an instance of
    ClickLoggingFormatter as a formatter and an instance of
    ClickLoggingHandler as a handler"""

    click_logging_handler = ClickLoggingHandler()
    click_logging_handler.formatter = ClickLoggingFormatter()

    logging.captureWarnings(True)
    logging.getLogger().handlers = [click_logging_handler]

    return click_logging_handler


def loglevel_command(name=None, default_log_level="INFO", **attrs) -> Callable[..., click.Command]:
    """Decorator creating a click.Command object with a --loglevel option

    Parameters
    ----------
    name
        command name
    default_log_level
        default log level
    """

    def decorator(f: Callable[..., Any]) -> click.Command:
        command = click.command(name, cls=_get_click_command_with_log_level_option(default_log_level), **attrs)(f)

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
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    )


def _get_click_command_with_log_level_option(default_log_level: str) -> Type[click.Command]:
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
