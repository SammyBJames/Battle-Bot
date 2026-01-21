import os
from json import load
import sqlite3
from flask import g


DATABASE = 'battlebot.db'
ADMIN_PASSWORD = 'admin_super_secret_password_123'


class Database:
    '''
    Database management class.
    '''

    @staticmethod
    def initialize() -> None:
        '''
        Initialize the Database and load schema and default data.

        Raises:
            FileNotFoundError: If items.json is not found when populating items.
        '''

        db: sqlite3.Connection = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        
        # Create users table
        cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL)')

        # Create items table for search (4 columns to match users)
        cursor.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL)')
        
        # Add admin user
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', ADMIN_PASSWORD, 'admin'))
            
        # Add items
        cursor.execute('SELECT count(*) FROM items')
        if cursor.fetchone()[0] == 0:
            if not os.path.exists('items.json'):
                raise FileNotFoundError('items.json not found')
            with open('items.json', 'r') as f:
                items_data = load(f)
                items_tuple = [(item['name'], item['description'], item['category']) for item in items_data]
                cursor.executemany('INSERT INTO items (name, description, category) VALUES (?, ?, ?)', items_tuple)
            
        # Create IP mapping table
        cursor.execute('CREATE TABLE IF NOT EXISTS ip_mappings (ip TEXT PRIMARY KEY, username TEXT NOT NULL)')

        db.commit()
        db.close()

    @staticmethod
    def get_connection() -> sqlite3.Connection:
        '''
        Get a database connection.

        Returns:
            sqlite3.Connection: The database connection.
        '''

        db: sqlite3.Connection | None = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
            db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def close_connection(exception: BaseException | None = None) -> None:
        '''
        Close the database connection for the current application context.

        Args:
            exception (Exception): The exception that caused the teardown, if any.
        '''

        db = getattr(g, '_database', None)
        if db is not None:
            db.close()
