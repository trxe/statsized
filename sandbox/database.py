import psycopg
import polars as pl
from typing import Mapping

class PostgreSQLDB:
    @classmethod
    def create_table(cls, table_name: str, varlist: list[list[str]]):
        fields = ',\n'.join([' '.join(x) for x in varlist])
        cmd = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields});"
        # print(cmd)
        return cls.conn.execute(cmd)
    
    @classmethod
    def _insert_cmd(cls, table_name: str, datamap: Mapping[str, any], conflict_keys: list[str]):
        data = list(datamap.items())
        keys = [x[0] for x in data]
        placeholders =', '.join(["%s"] * len(keys))
        keystr = ', '.join(keys)
        cmd = f"""INSERT INTO {table_name} ({keystr}) 
                VALUES ({placeholders})
                ON CONFLICT ({', '.join(conflict_keys)}) DO NOTHING
                RETURNING {keystr};"""
        return cmd

    @classmethod
    def insert_many(cls, table_name: str, datamaplist: list[Mapping[str, any]], conflict_keys: list[str]):
        if not datamaplist:
            return None
        cmd = cls._insert_cmd(table_name, datamaplist[0], conflict_keys)
        values = list(tuple(datamap.values()) for datamap in datamaplist)
        print(cmd)
        print(values[0])
        # print(values)
        with cls.conn.cursor() as cur:
            cur.executemany(cmd, values)

    @classmethod
    def insert(cls, table_name: str, datamap: Mapping[str, any], conflict_keys: list[str]):
        cmd = cls._insert_cmd(cls, table_name, datamap, conflict_keys)
        values = tuple(datamap.values())
        return cls.conn.execute(cmd, values)

    @classmethod
    def select(cls, table_name: str, keylist: list[str], additional: str):
        cmd = f"SELECT {', '.join(keylist)} FROM {table_name} {additional};"
        return cls.conn.execute(cmd)

    @classmethod
    def create_enum(cls, typename, enum_values):
        enum_str = "\', \'".join(enum_values)
        cmd = f"""
DO $$ BEGIN
    CREATE TYPE {typename} AS ('{enum_str}');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
        """
        return cls.conn.execute(cmd)
    
    @classmethod
    def execute(cls, cmd):
        return cls.conn.execute(cmd)
    
    @classmethod
    def commit(cls):
        cls.conn.commit()

    @classmethod
    def start(cls, dbname, user):
        # Service name is required for most backends
        cls.conn = psycopg.connect(f"dbname={dbname} user={user}")

        