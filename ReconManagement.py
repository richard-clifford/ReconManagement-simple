import sqlite3
import argparse
import time
import json
# import sqlalchemy

class ReconManagement:

    args = {}
    run_time = 0
    current_project_data = []
    db_conn = None

    def __init__(self, args):
        # Get the current run-time
        self.run_time = int(time.time())
        self.args = args
        self.db = self.get_db_instance(args.database)

    def get_db_instance(self, db_name):        
        self.db_conn = sqlite3.connect(db_name)
        cur = self.db_conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subdomain TEXT NOT NULL UNIQUE,
            project_name TEXT,
            time_created INTEGER NOT NULL,
            time_deleted INTEGER NOT NULL,
            "source" TEXT
        );''')
        return cur

    def add_data(self, project='', domain='', source=''):
        try:
            status = self.db.execute('''
                INSERT INTO projects (subdomain, project_name, time_created, time_deleted, source) 
                VALUES (?, ?, ?, 0, ?);''',
                (domain, project, self.run_time, source)
            )
            self.db_conn.commit()
        except Exception as e:
            with open('errors.txt', 'a') as f:
                f.write(str(e)+"\n")
            pass

    def get_data(self, project=''):
        ret = []
        self.db.execute('SELECT subdomain FROM projects WHERE project_name=?', (project,))        
        data = self.db.fetchall()
        for row in data:
            ret.append(row[0])
        return ret

def main():
    
    parser = argparse.ArgumentParser(description='ReconManagement')
    parser.add_argument('-p', '--project', required=False, help='The project name to add/retrieve data to/from, eg. Yahoo')
    parser.add_argument('-a', '--action', required=True, help='The action to do, "get" or "put"')
    parser.add_argument('-d', '--domain', required=False, help='The subdomain to put or get')
    parser.add_argument('-f', '--database', required=True, help='The database file to store the data in')
    parser.add_argument('-s', '--source', required=False, help='The source of which the subdomain came from')
    parser.add_argument('--format', default='txt', required=False, help='Output format: txt | json')
    args = parser.parse_args()

    # Class Instance
    rm = ReconManagement(args)
    
    if args.action == 'put':
        rm.add_data(project=args.project, domain=args.domain, source=args.source)
    elif args.action == 'get':
        if args.format == 'json':
            print(json.dumps(rm.get_data(project=args.project)))
        else:
            print("\n".join(rm.get_data(project=args.project)))
    else:
        return "Unable to process the action provided {}".format(args.action)
    ### 
    # Todo:
    #   1. Add timeframes for lookups
    #   2. Compare what is new (colour coded?) and old, also what has been deleted (red) and added (green)
    #   3. Produce CLI (json and txt?) and HTML reports 
    #   4. Implent sqlalchemy instead of this shit
    
if __name__ == '__main__':
    main()
