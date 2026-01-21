import random
import string
from sqlite3 import IntegrityError
from database import Database


class Auth:
    '''
    Authentication helper class.
    '''

    @staticmethod
    def generate_credentials() -> tuple[str, str]:
        '''
        Generate a random username and password.

        Returns:
            tuple[str, str]: A tuple containing the generated username and password.
        ''' 

        username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return username, password

    @staticmethod
    def get_user_from_ip(ip_address: str) -> tuple[str, str]:
        '''
        Get or create a user associated with the given IP address.

        Args:
            ip_address (str): The IP address to get or create a user for.

        Returns:
            tuple[str, str]: A tuple containing the username and password associated with the IP address.
        '''

        db = Database.get_connection()
        cursor = db.cursor()
        
        # Check if this IP already has a user
        cursor.execute('SELECT username FROM ip_mappings WHERE ip = ?', (ip_address,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute('SELECT username, password FROM users WHERE username = ?', (row['username'],))
            row = cursor.fetchone()
            return row['username'], row['password']
                
        # No user found, create new one
        username, password = Auth.generate_credentials()
        while True:
            try:
                cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'user'))
                break
            except IntegrityError:
                username, password = Auth.generate_credentials()
                
        cursor.execute('INSERT OR REPLACE INTO ip_mappings (ip, username) VALUES (?, ?)', (ip_address, username))
        db.commit()
        
        return username, password
