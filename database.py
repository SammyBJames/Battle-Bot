import sqlite3
import json
import os
from flask import g


DATABASE = 'battlebot.db'
ADMIN_PASSWORD = 'admin_super_secret_password_123'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create Users table (4 columns needed for SQLi parity with Items)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        # Create Items table for search (4 columns to match Users)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')
        
        # Check if admin exists
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                           ('admin', ADMIN_PASSWORD, 'admin'))
            
        # Add some initial items (Load from JSON if empty)
        cursor.execute('SELECT count(*) FROM items')
        if cursor.fetchone()[0] == 0:
            if os.path.exists('items.json'):
                with open('items.json', 'r') as f:
                    items_data = json.load(f)
                    items_tuple = [(item['name'], item['description'], item['category']) for item in items_data]
                    cursor.executemany('INSERT INTO items (name, description, category) VALUES (?, ?, ?)', items_tuple)
                    print(f'Loaded {len(items_tuple)} items from items.json')
            else:
                raise FileNotFoundError('items.json not found')
            
        # Create IP Map table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_mappings (
                ip TEXT PRIMARY KEY,
                username TEXT NOT NULL
            )
        ''')

        db.commit()
