"""
Command line argument parsing for the Banker and Player programs.

This module only depends on the standard library so that it can be imported
(and unit tested) without starting the game, opening sockets, or drawing to
the screen.
"""
import argparse

# Player ids are sent over the network as a single digit (0-9).
MAX_PLAYERS = 10
MAX_PORT = 65535


def positive_int(value: str) -> int:
    """Convert value to an int and require it to be greater than zero."""
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a whole number")
    if number <= 0:
        raise argparse.ArgumentTypeError(f"{number} must be greater than 0")
    return number


def player_count(value: str) -> int:
    """Convert value to an int between 1 and MAX_PLAYERS."""
    number = positive_int(value)
    if number > MAX_PLAYERS:
        raise argparse.ArgumentTypeError(f"at most {MAX_PLAYERS} players are supported")
    return number


def is_valid_ip(address: str) -> bool:
    """Return True if address looks like an IPv4 address (xxx.xxx.xxx.xxx)."""
    parts = address.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)


def build_banker_parser() -> argparse.ArgumentParser:
    """Create the argument parser for banker.py."""
    parser = argparse.ArgumentParser(
        prog="banker.py",
        description="Host a game of Terminal Monopoly.",
        allow_abbrev=False,
    )
    parser.add_argument("test", nargs="?", type=int, default=None,
                        help="unit test preset to run (asked for interactively if omitted)")
    parser.add_argument("-local", "--local", action="store_true",
                        help="host on localhost port 33333 and skip screen calibration")
    parser.add_argument("-stayopen", "--stayopen", action="store_true",
                        help="keep the server open after all players disconnect")
    parser.add_argument("-skipcalib", "--skipcalib", action="store_true",
                        help="skip screen calibration")
    parser.add_argument("-silent", "--silent", action="store_true",
                        help="hide verbose output in the banker's output areas")
    parser.add_argument("-debtok", "--debtok", action="store_true",
                        help="allow players to go into debt in the casino")
    parser.add_argument("--cash", type=positive_int, default=None, metavar="AMOUNT",
                        help="starting cash for each player (overrides the test preset)")
    parser.add_argument("--players", type=player_count, default=None, metavar="COUNT",
                        help=f"number of players, 1-{MAX_PLAYERS} (overrides the test preset)")
    return parser


def build_player_parser() -> argparse.ArgumentParser:
    """Create the argument parser for player.py."""
    parser = argparse.ArgumentParser(
        prog="player.py",
        description="Join (or host) a game of Terminal Monopoly as a player.",
        allow_abbrev=False,
    )
    parser.add_argument("-local", "--local", action="store_true",
                        help="connect to a banker running with -local")
    parser.add_argument("-withnet", "--withnet", action="store_true",
                        help="enable network commands while in debug mode")
    parser.add_argument("-skipcalib", "--skipcalib", action="store_true",
                        help="skip screen calibration and use compatibility colors")
    parser.add_argument("-debug", "--debug", nargs="*", default=None, metavar="NAME IP PORT",
                        help="debug mode; optionally give a name, banker IP and port to connect")
    return parser


def parse_banker_args(argv: list = None) -> argparse.Namespace:
    """
    Parse the Banker's command line arguments.

    Parameters:
        argv (list): Arguments to parse. Defaults to sys.argv[1:] when None.

    Returns:
        argparse.Namespace with test, local, stayopen, skipcalib, silent,
        debtok, cash and players.
    """
    return build_banker_parser().parse_args(argv)


def parse_player_args(argv: list = None) -> argparse.Namespace:
    """
    Parse the Player's command line arguments.

    Parameters:
        argv (list): Arguments to parse. Defaults to sys.argv[1:] when None.

    Returns:
        argparse.Namespace with local, withnet, skipcalib and debug. debug is
        None when the flag is absent, [] for "-debug" alone, or
        [name, ip, port] when connection details are given.
    """
    parser = build_player_parser()
    args = parser.parse_args(argv)
    if args.debug:
        if len(args.debug) != 3:
            parser.error("-debug takes either no values or exactly three: NAME IP PORT")
        name, ip, port = args.debug
        if not is_valid_ip(ip):
            parser.error("Invalid IP address format. Please use the format xxx.xxx.xxx.xxx")
        if not port.isdigit() or not 0 < int(port) <= MAX_PORT:
            parser.error(f"Invalid port. Please use a number between 1 and {MAX_PORT}")
    return args
