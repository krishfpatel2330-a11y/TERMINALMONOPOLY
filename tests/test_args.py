"""
Unit tests for utils/args.py (command line argument parsing).

Run from the repository root with:
    python -m unittest tests.test_args -v
"""
import contextlib
import io
import unittest

from utils.args import parse_banker_args, parse_player_args


class BankerArgsTest(unittest.TestCase):
    """Tests for the Banker's command line arguments."""

    def test_defaults(self):
        """With no arguments every flag is off and nothing is overridden."""
        args = parse_banker_args([])
        self.assertIsNone(args.test)
        self.assertIsNone(args.cash)
        self.assertIsNone(args.players)
        for flag in (args.local, args.stayopen, args.skipcalib, args.silent, args.debtok):
            self.assertFalse(flag)

    def test_valid_overrides(self):
        """Existing flags, the test number and the new options are all read."""
        args = parse_banker_args(["2", "-local", "-silent", "--cash", "3000", "--players", "4"])
        self.assertEqual(args.test, 2)
        self.assertTrue(args.local)
        self.assertTrue(args.silent)
        self.assertFalse(args.debtok)
        self.assertEqual(args.cash, 3000)
        self.assertEqual(args.players, 4)

    def test_invalid_input(self):
        """Bad values and unknown flags exit instead of being ignored."""
        bad_inputs = (["--cash", "abc"], ["--cash", "-50"], ["--players", "0"],
                      ["--players", "11"], ["-notaflag"])
        for argv in bad_inputs:
            with self.subTest(argv=argv):
                # argparse prints its usage message to stderr; keep the test output clean.
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        parse_banker_args(argv)


class PlayerArgsTest(unittest.TestCase):
    """Tests for the Player's command line arguments."""

    def test_defaults(self):
        """With no arguments the player starts in normal (non-debug) mode."""
        args = parse_player_args([])
        self.assertFalse(args.local)
        self.assertFalse(args.withnet)
        self.assertFalse(args.skipcalib)
        self.assertIsNone(args.debug)

    def test_debug_with_connection_details(self):
        """-debug accepts no values, or a name, IP address and port."""
        self.assertEqual(parse_player_args(["-debug"]).debug, [])
        args = parse_player_args(["-debug", "Krish", "127.0.0.1", "3131", "-skipcalib"])
        self.assertEqual(args.debug, ["Krish", "127.0.0.1", "3131"])
        self.assertTrue(args.skipcalib)

    def test_invalid_debug_details(self):
        """A malformed IP, a bad port or a missing value is rejected."""
        bad_inputs = (["-debug", "Krish", "localhost", "3131"],
                      ["-debug", "Krish", "127.0.0.1", "port"],
                      ["-debug", "Krish", "127.0.0.1"])
        for argv in bad_inputs:
            with self.subTest(argv=argv):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        parse_player_args(argv)


if __name__ == "__main__":
    unittest.main()
