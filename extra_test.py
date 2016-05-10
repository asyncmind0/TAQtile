from unittest import TestCase
from dmenu import dmenu_run, list_executables, RecentRunner
from libqtile import sh, command, hook
from extra import autossh_term
from random import randint


class QtileRunTest(TestCase):
    def test_dmenu_run(self):
        dmenu_run(command.Client())

    def test_list_executables(self):
        self.assertIn("bash", list_executables())
        self.assertIn("python", list_executables())
    
    def test_autossh_term(self):
        print(autossh_term(title="shawk_left", port=9001))
