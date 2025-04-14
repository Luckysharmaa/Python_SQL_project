import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseManager:
    def __init__(self):
        """Initialize the database connection using environment variables"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "victus"),
                database=os.getenv("DB_NAME", "contact_manager")
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Connected to MySQL database")
                self._create_tables()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def _create_tables(self):
        """Create contacts table if it doesn't exist"""
        try:
            # Create contacts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    address VARCHAR(200),
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()
            print("Tables created successfully")
        except Error as e:
            print(f"Error creating tables: {e}")
            raise

    def close(self):
        """Close the database connection"""
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection closed")

    # Contact CRUD operations
    def create_contact(self, name, email=None, phone=None, address=None, notes=None):
        """Create a new contact"""
        try:
            query = """
                INSERT INTO contacts (name, email, phone, address, notes) 
                VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (name, email, phone, address, notes))
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error creating contact: {e}")
            self.connection.rollback()
            return None

    def get_contact_by_id(self, contact_id):
        """Get a contact by ID"""
        query = "SELECT * FROM contacts WHERE id = %s"
        self.cursor.execute(query, (contact_id,))
        return self.cursor.fetchone()

    def get_all_contacts(self):
        """Get all contacts"""
        query = "SELECT * FROM contacts ORDER BY name"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def search_contacts(self, search_term):
        """Search contacts by name, email, or phone"""
        query = """
            SELECT * FROM contacts 
            WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
            ORDER BY name
        """
        param = f"%{search_term}%"
        self.cursor.execute(query, (param, param, param))
        return self.cursor.fetchall()

    def update_contact(self, contact_id, name=None, email=None, phone=None, address=None, notes=None):
        """Update a contact's information"""
        try:
            # Get the current contact data
            current = self.get_contact_by_id(contact_id)
            if not current:
                return False

            # Update with new values or keep existing ones
            name = name if name is not None else current['name']
            email = email if email is not None else current['email']
            phone = phone if phone is not None else current['phone']
            address = address if address is not None else current['address']
            notes = notes if notes is not None else current['notes']

            query = """
                UPDATE contacts 
                SET name = %s, email = %s, phone = %s, address = %s, notes = %s 
                WHERE id = %s
            """

            self.cursor.execute(query, (name, email, phone, address, notes, contact_id))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"Error updating contact: {e}")
            self.connection.rollback()
            return False

    def delete_contact(self, contact_id):
        """Delete a contact"""
        try:
            query = "DELETE FROM contacts WHERE id = %s"
            self.cursor.execute(query, (contact_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"Error deleting contact: {e}")
            self.connection.rollback()
            return False