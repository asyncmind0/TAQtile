from unittest import TestCase
from dmenu import dmenu_run, list_executables, RecentRunner, list_bluetooth
from libqtile import sh, command, hook
from extra import autossh_term, SwitchToWindowGroup
from random import randint
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
import re


class QtileRunTest(TestCase):
    def test_dmenu_run(self):
        dmenu_run(command.Client())

    def test_list_executables(self):
        self.assertIn("bash", list_executables())
        self.assertIn("python", list_executables())
    
    def test_autossh_term(self):
        print(autossh_term(title="shawk_left", port=9001))


class TestDmenuListBluetooth(TestCase):
    def test_list_bluetooth(self):
        client = command.Client()
        list_bluetooth(client)


class TestSwitchToWindowGroup(TestCase):
    def test_switch_group(self):
        client = command.Client()
        sw = SwitchToWindowGroup(
            'mail',
            title=re.compile('Inbox .*$'),
            screen=PRIMARY_SCREEN,
            spawn=[
                {"cmd": 'google-chrome-stable --app="https://inbox.google.com/u/0/"', "match": re.compile("^Inbox .* melit.stevenjoseph@gmail.com$")},
                {"cmd": 'google-chrome-stable --app="https://inbox.google.com/u/1/"', "match": re.compile("^Inbox .* steven@streethawk.co$")},
                {"cmd": 'google-chrome-stable --app="https://inbox.google.com/u/2/"', "match": re.compile("^Inbox .* stevenjose@gmail.com$")},
                {"cmd": 'google-chrome-stable --app="https://inbox.google.com/u/3/"', "match": re.compile("^Inbox .* steven@stevenjoseph.in$")},
            ]
        )
        
        sw.window_exists(client, re.compile("^Inbox .* steven@stevenjoseph.in$"))
