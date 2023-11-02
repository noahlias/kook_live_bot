# db_handler.py
import sqlite3
from typing import List


class DBHandler:
    def __init__(self, db_name: str):
        """
        Initialize a new DBHandler instance.

        Args:
            db_name: The name of the SQLite database file.
        """
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        # Create the table if it doesn't exist
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS user_ids
                     (id INTEGER PRIMARY KEY, user_id TEXT)"""
        )

    def insert_user_id(self, user_id: str):
        """
        Insert a new user ID into the database.

        Args:
            user_id: The user ID to insert.
        """
        self.c.execute("INSERT INTO user_ids (user_id) VALUES (?)", (user_id,))
        self.conn.commit()

    def close_connection(self):
        """
        Close the connection to the database.
        """
        self.conn.close()

    def get_all_user_ids(self) -> List[str]:
        """
        Get all user IDs from the database.

        Returns:
            A list of all user IDs.
        """
        self.c.execute("SELECT user_id FROM user_ids")
        return [row[0] for row in self.c.fetchall()]

    def check_user_id_exists(self, user_id: str) -> bool:
        """
        Check if a user ID exists in the database.

        Args:
            user_id: The user ID to check.

        Returns:
            True if the user ID exists, False otherwise.
        """
        self.c.execute("SELECT 1 FROM user_ids WHERE user_id = ?", (user_id,))
        return self.c.fetchone() is not None

    def delete_user_id(self, user_id: str) -> None:
        """
        Deletes a user ID from the database.

        Args:
            user_id: The user ID to delete.

        Returns:
            None
        """
        self.c.execute("DELETE FROM user_ids WHERE user_id = ?", (user_id,))
        self.conn.commit()
