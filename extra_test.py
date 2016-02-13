from unittest import TestCase
from dmenu import dmenu_run, list_executables
from libqtile import sh, command


class QtileRunTest(TestCase):
    def test_dmenu_run(self):
        dmenu_run(command.Client())

    def test_list_executables(self):
        self.assertIn("bash", list_executables())
        self.assertIn("python", list_executables())
    
