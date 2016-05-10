import sqlite3
from os.path import expanduser, isdir, join, pathsep
import datetime
import time
from libqtile.log_utils import logger as log


def adapt_datetime(ts):
    return time.mktime(ts.timetuple())

sqlite3.register_adapter(datetime.datetime, adapt_datetime)


class RecentRunner:
    def __init__(self, dbpath=None):
        #self.conn = sqlite3.connect(":memory:")
        self.conn = sqlite3.connect(expanduser(dbpath or "~/.qtile_run.db"))
        self.conn.isolation_level = None
        c = self.conn.cursor()
        try:
            # Create table
            c.execute('''CREATE TABLE IF NOT EXISTS qtile_run
                (date text, command text UNIQUE, count integer)''')
        except Exception as e:
            log.exception("error creating table")

    def list(self, items, limit=100):
        sql = "SELECT command FROM qtile_run ORDER BY date DESC, count DESC"
        itemslist = {}
        for item in items:
            itemslist[item] = 0
        c = self.conn.cursor()
        results = c.execute(sql)
        res = [x[0] for x in results.fetchall()]
        for i, item in enumerate(res, 1):
            itemslist[item] = i
        return [x[0] for x in sorted(itemslist.items(), key=lambda x: x[1])]

    def recent(self, command=''):
        sql = "SELECT command FROM qtile_run "
        c = self.conn.cursor()
        if command:
            sql += "WHERE command LIKE '%s%%'" % command
        sql += "ORDER BY DATE"
        results = c.execute(sql)
        return [x[0] for x in results.fetchall()]

    def insert(self, command):
        c = self.conn.cursor()
        now = datetime.datetime.now()
        prev = self.recent(command)
        if prev:
            sql = "update qtile_run set date = ?, count = count + 1 where command = ?"
            return c.execute(sql, (now, command))
        else:
            sql = "insert into qtile_run values (?, ?, ?)"
            return c.execute(sql, (now, command, 1))
