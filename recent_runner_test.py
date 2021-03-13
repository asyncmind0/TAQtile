from unittest import TestCase
from recent_runner import RecentRunner
from dmenu import list_executables


class RecentRunnerTest(TestCase):
    def test_list(self):
        rr = RecentRunner("qtile_run", dbpath="~/.qtile_run_test.db")
        self.assertGreater(len(rr.list(list_executables())), 1)

    def test_recent_run(self):
        rr = RecentRunner("qtile_run", dbpath="~/.qtile_run_test.db")
        rr.insert("testcmd")
        rr.insert("testcmd2")
        rr.insert("testcmd1")
        rr.insert("cmdtest")
        rr.insert("blah")
        for res in rr.recent("cmd"):
            self.assertTrue(res.startswith("cmd"))
        results = rr.recent("test")
        print(results)
