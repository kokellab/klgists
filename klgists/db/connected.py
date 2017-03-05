import pymysql
import contextlib
from typing import Tuple, List, Dict, Iterator

@contextlib.contextmanager
def connected(connection: pymysql.connections.Connection):
    """A context with global convenience functions for MySQL/MariaDB queries. Specifically:
        — select(statement, vals)
        — execute(statement, vals)
    Where cursor.execute(statement, vals) is called.
    """
    
    try:
        
        global select, execute
        def execute(statement: str, vals: Tuple=()) -> None:
            with connection.cursor() as cursor:
                cursor.execute(statement, vals)
                connection.commit()
                
        def select(statement: str, vals: Tuple=()) -> Iterator[Dict]:
            with connection.cursor() as cursor:
                cursor.execute(statement, vals)
                return cursor
        yield
        
    finally:
        connection.close()
