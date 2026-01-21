import random
import string
import sqlite3
from database import get_db


def generate_credentials():
    username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return username, password


def get_or_create_user_for_ip(ip_address):
    db = get_db()
    cursor = db.cursor()
    
    # Check if this IP already has a user
    cursor.execute('SELECT username FROM ip_mappings WHERE ip = ?', (ip_address,))
    row = cursor.fetchone()
    
    if row:
        username = row['username']
        # Fetch the password for this user
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()
        if user_row:
            return username, user_row['password']
            
    # No user found, create new one
    username, password = generate_credentials()
    
    # Ensure username is unique
    while True:
        try:
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'user'))
            break
        except sqlite3.IntegrityError:
            username, password = generate_credentials()
            
    cursor.execute('INSERT OR REPLACE INTO ip_mappings (ip, username) VALUES (?, ?)', (ip_address, username))
    db.commit()
    
    return username, password
