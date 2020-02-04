import sqlite3
from os.path import expanduser, isdir, join, pathsep
import datetime
import time
from log import logger


def adapt_datetime(ts):
    return time.mktime(ts.timetuple())

sqlite3.register_adapter(datetime.datetime, adapt_datetime)


class RecentRunner:
    def __init__(self, dbname, dbpath=None):
        self.dbname = dbname
        #self.conn = sqlite3.connect(":memory:")
        self.conn = sqlite3.connect(expanduser(dbpath or "~/.qtile_run.db"))
        self.conn.isolation_level = None
        c = self.conn.cursor()
        try:
            # Create table
            c.execute(
                """CREATE TABLE IF NOT EXISTS %s
                (date text, command text UNIQUE, count integer)""" %
                self.dbname
            )
        except Exception as e:
            logger.exception("error creating table")

    def list(self, items, limit=100):
        sql = (
            "SELECT command FROM %s ORDER BY date, count" %
            self.dbname
        )
        itemslist = {}
        for item in items:
            itemslist[item] = 0
        c = self.conn.cursor()
        results = c.execute(sql)
        res = [x[0] for x in results.fetchall()]
        for i, item in enumerate(res, 1):
            itemslist[item] = i
        ret = [x[0] for x in sorted(itemslist.items(), key=lambda x: x[1])]
        #logger.error(ret)
        return reversed(ret)

    def recent(self, command=''):
        sql = "SELECT command FROM %s " % self.dbname
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
            sql = (
                "update %s set date = ?, count = count + 1 where command = ?" %
                self.dbname
            )
            return c.execute(sql, (now, command))
        else:
            sql = "insert into %s values (?, ?, ?)" % self.dbname
            return c.execute(sql, (now, command, 1))


if __name__ == '__main__':
    import sys
    recent_runner = RecentRunner(sys.argv[0])
    import ipdb; ipdb.set_trace() ######## FIXME:REMOVE ME steven.joseph ################
