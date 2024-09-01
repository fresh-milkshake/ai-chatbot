import json
from typing import Dict, Optional

from loguru import logger
from telegram import Update

from app.database.utils import gather_user_data

from .abstraction import StorageProvider, Response
import sqlite3


class SqliteDatabase(StorageProvider):
    def on_created(self):
        """Create the users table if it doesn't exist."""
        self.db_path: str = "database.db"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    user_data TEXT
                )
            """
            )
            conn.commit()
        logger.info("Database created successfully")

    def get_data(self):
        """Retrieve all user data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            logger.info("Retrieved all user data successfully")
            return rows

    def update_users(self, users: Dict[str, dict]) -> Response[bool]:
        """Update multiple users."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for user_id, user_data in users.items():
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO users (user_id, user_data) VALUES (?, ?)
                    """,
                        (user_id, str(user_data)),
                    )
                conn.commit()
            logger.info("Updated multiple users successfully")
            return Response(success=True, data=True)
        except Exception as e:
            logger.error(f"Error updating multiple users: {e}")
            return Response(success=False, data=str(e))

    def update_user_by_id(self, user_id: int, user_data: dict) -> Response[bool]:
        """Update a single user by their ID."""
        try:
            if not isinstance(user_id, int):
                logger.error(f"Invalid user ID type: {type(user_id)}")
                raise ValueError("Invalid user ID type")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO users (user_id, user_data) VALUES (?, ?)
                """,
                    (user_id, str(user_data)),
                )
                conn.commit()
            logger.info(f"Updated user with ID {user_id} successfully")
            return Response(success=True, data=True)
        except sqlite3.Error as e:
            logger.error(f"SQLite error updating user with ID {user_id}: {e}")
            return Response(success=False, data=str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating user with ID {user_id}: {e}")
            return Response(success=False, data=str(e))

    def update_user(self, user_data: dict) -> Response[bool]:
        """Update a user using their data. Assumes the data contains 'user_id'."""
        try:
            user_id = user_data.get("user_id")
            if not user_id:
                logger.error("User ID not found in user data")
                return Response(success=False, data="user_id not found in user_data")

            return self.update_user_by_id(user_id, user_data)
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return Response(success=False, data=str(e))

    def _get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Retrieve a user by their ID (internal method)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT user_data FROM users WHERE user_id = ?
            """,
                (user_id,),
            )
            row = cursor.fetchone()
            if row:
                return eval(row[0])
            return None

    def get_user(self, user_id: int) -> Response[dict]:
        """Get a user by their ID."""
        user_data = self._get_user_by_id(user_id)
        if user_data:
            logger.info(f"Retrieved user with ID {user_id} successfully")
            return Response(success=True, data=user_data)
        else:
            logger.error(f"User with ID {user_id} not found")
            return Response(success=False, data="User not found")

    def get_user_by_update(self, update: Update) -> Response[dict]:
        """Get a user by their Telegram Update."""
        logger.debug(f"Getting user with ID {update.effective_user.id}")
        user_id = update.effective_user.id
        user_data = self._get_user_by_id(user_id)
        if not user_data:
            self.create_user_from_update(update)
            user_data = self._get_user_by_id(user_id)
        logger.info(f"Retrieved user with ID {user_id} successfully")
        return Response(success=True, data=user_data)
    
    def create_user_from_update(self, update: Update) -> Response[bool]:
        """Create a user from a Telegram Update."""
        try:
            user_id, user_data = gather_user_data(update)
            return self.update_user_by_id(user_id, user_data)
        except Exception as e:
            return Response(success=False, data=str(e))

    def delete_user(self, user_id: int) -> Response[bool]:
        """Delete a user by their ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    DELETE FROM users WHERE user_id = ?
                """,
                    (user_id,),
                )
                conn.commit()
            return Response(success=True, data=True)
        except Exception as e:
            return Response(success=False, data=str(e))

    def get_users(self) -> Response[Dict[str, Dict]]:
        """Retrieve all users."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, user_data FROM users")
                rows = cursor.fetchall()
                users = {str(row[0]): eval(row[1]) for row in rows}
            return Response(success=True, data=users)
        except Exception as e:
            return Response(success=False, data=str(e))
