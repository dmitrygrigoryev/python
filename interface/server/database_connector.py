import sqlite3
class DatabaseConnection(object):
    """
        class for working with SQLite database.
        Constructor:
            database name
            db = DatabaseConnection(db_name)

        Methods:
            -db.get_all_table_data('table_name')
            -db.get_data_by_query('table_name','sql_query')
    """
    def __init__(self,db_name): 
        self.db_name = db_name
        self.db_con = sqlite3.connect(self.db_name)
        
    def get_all_table_data(self,table_name):
        cur = self.db_con.cursor()
        if self.table_exists(table_name):
            SQL = "SELECT * from %s"%table_name
            cur.execute(SQL)
            rows = cur.fetchall()
            return rows
        else:
           return 0
    def execute_query(self,sql_query):
        cur = self.db_con.cursor()
        # try:
        cur.execute(sql_query)
        self.db_con.commit()
            # return 1
        # self.db_con.commit()
        # except Exception:
            # return 0
    def get_data_by_query(self,table_name,sql_query):
        cur = self.db_con.cursor()
        if self.table_exists(table_name):
            cur.execute(sql_query)
            rows = cur.fetchall()
            return rows
        else:
            return 0
            
    def table_exists(self,name):
        c = self.db_con.cursor()
        SQL = "SELECT * FROM sqlite_master WHERE type='table' AND name='%s'"%name
        c.execute(SQL)
        if len(c.fetchall()) == 0:
            return False
        else:
            return True
    
    def print_tables(self):
        c = self.db_con.cursor()
        SQL = "SELECT * FROM sqlite_master WHERE type='table'"
        rows = c.execute(SQL)
        for row in rows:
            print row
    def close(self):
        self.db_con.commit()
        self.db_con.close()