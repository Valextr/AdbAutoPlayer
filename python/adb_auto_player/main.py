import argparse
import json
import logging
import sys
from typing import NoReturn

from adb_auto_player.adb import wm_size_reset, get_device, get_running_app
from adb_auto_player import Command, Game
from adb_auto_player.games import AFKJourney, InfinityNikki
from adb_auto_player.logging_setup import setup_json_log_handler, setup_text_log_handler


def _get_games() -> list[Game]:
    return [
        AFKJourney(),
        InfinityNikki(),
    ]


def main() -> None:
    commands = _get_commands()
    command_names = []
    for cmd in commands:
        command_names.append(cmd.name)

    parser = argparse.ArgumentParser(description="AFK Journey")
    parser.add_argument(
        "command",
        help="Command to run",
        choices=command_names,
    )
    parser.add_argument(
        "--output",
        choices=["json", "text", "raw"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="DEBUG",
        help="Log level",
    )

    args = parser.parse_args()
    match args.output:
        case "json":
            setup_json_log_handler(args.log_level)
        case "text":
            setup_text_log_handler(args.log_level)
        case _:
            logging.getLogger().setLevel(args.log_level)

    for cmd in commands:
        if str.lower(cmd.name) == str.lower(args.command):
            __run_command(cmd)

    sys.exit(1)


def get_gui_games_menu() -> str:
    menu = []
    for game in _get_games():
        options = game.get_gui_options()
        menu.append(options.to_dict())

    return json.dumps(menu)


def _get_commands() -> list[Command]:
    commands = [
        Command(
            name="GUIGamesMenu",
            action=_print_gui_games_menu,
        ),
        Command(
            name="WMSizeReset",
            action=wm_size_reset,
        ),
        Command(
            name="GetRunningGame",
            action=_print_running_game,
        ),
    ]

    for game in _get_games():
        commands += game.get_cli_menu_commands()

    return commands


def _print_gui_games_menu() -> None:
    print(get_gui_games_menu())
    return None


def _print_running_game() -> None:
    running_game = _get_running_game()
    if running_game:
        logging.info(f"Running game: {_get_running_game()}")
    else:
        logging.debug("No running game")
    return None


def _get_running_game() -> str | None:
    try:
        device = get_device()
        package_name = get_running_app(device)
        if not package_name:
            return None
        for game in _get_games():
            if any(pn in package_name for pn in game.package_names):
                return game.get_gui_options().game_title
    except Exception as e:
        logging.error(e)
    return None


def __run_command(cmd: Command) -> NoReturn:
    try:
        cmd.run()
    except Exception as e:
        logging.error(f"{e}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    logging.getLogger("PIL").setLevel(logging.INFO)
    main()
