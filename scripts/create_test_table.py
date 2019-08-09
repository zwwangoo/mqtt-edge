import json
import sqlite3

config = {
    "ml": [{
        "features": [1, 2, 5],
        "ip": "192.168.1.3",
        "ipcs": ["192.168.1.110", "192.168.1.111"]
    }],
    "pusher": [{
        "ip": "192.168.1.2",
        "ipcs": ["192.168.1.110", "192.168.1.111"],
        "status": [1, 0]
    }]
}


def create_db(db_path, term_sn, config):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'create table edge (term_sn varchar(30) primary key, config text)')
    cursor.execute(r"insert into edge values ('{term_sn}', '{config}')"
                   .format(term_sn=term_sn, config=json.dumps(config)))
    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_db('./sqlite.db', 'MG51T-09-S05-1200', config)
