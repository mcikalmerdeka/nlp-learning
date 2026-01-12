"""Database connection and query execution"""

import psycopg2
import streamlit as st
from typing import Optional, List, Tuple


class DatabaseConnection:
    """Manage database connections and operations"""
    
    def __init__(self, host: str, database: str, user: str, password: str, port: str = "5432"):
        """
        Initialize database connection parameters
        
        Args:
            host: Database host
            database: Database name
            user: Database user
            password: Database password
            port: Database port (default: 5432)
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
    
    def connect(self) -> Optional[psycopg2.extensions.connection]:
        """
        Establish connection to the database
        
        Returns:
            Database connection object or None if connection fails
        """
        try:
            connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            return connection
        except Exception as e:
            st.error(f"Error with database connection: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        connection = self.connect()
        if connection:
            connection.close()
            st.success(f"Connected to the database {self.database} successfully!")
            return True
        return False


def execute_sql_query(db_connection: DatabaseConnection, query: str) -> Optional[List[Tuple]]:
    """
    Execute an SQL query and return the result
    
    Args:
        db_connection: DatabaseConnection instance
        query: SQL query string
        
    Returns:
        List of tuples containing query results, or None if error
    """
    connection = db_connection.connect()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None
