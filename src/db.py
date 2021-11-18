import sqlite3
import sys

class DB():

    def __init__(self, db_name):
        """
        """
        db_name=self.__init_name(name=db_name)
        try:
            self.conn=sqlite3.connect(db_name)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(1)

    def __init_name(self, name):
        """
        Initialise the database name
        """
        if not(type(name)==str):
            name=str(name)
        if not(name.endswith('.db')):
            name+='.db'
            
        return name
        
    def query(self, query):
        try:
            cursor = self.conn.execute(query)
        except Exception as e:
            print('Could not execute query:', query, file=sys.stderr)
            print('Error:', e, file=sys.stderr)
            sys.exit(1)

        return cursor

    def create_table(self, table, columns):
        pass
