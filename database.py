import sqlite3
import re


def get_db_connection():
    try:
        conn = sqlite3.connect('requests.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def initialize_items():
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return

    try:
        cursor = conn.cursor()


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                emp_id TEXT NOT NULL,
                department TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                particular TEXT UNIQUE NOT NULL,
                available BOOLEAN NOT NULL
            )
        ''')

        default_items = [
            ("A3 ENVELOPE GREEN", True),
            ("A3 PAPER", True),
            ("A3 TRANSPARENT FOLDER", True),
            ("A4 ENVELOPE GREEN", True),
            ("A4 LOGO ENVOLOP", True),
            ("A4 PAPER", True),
            ("A4 TRANSPARENT FOLDER", True),
            ("BINDER CLIP 19MM", True),
            ("BINDER CLIP 25MM", True),
            ("BINDER CLIP 41MM", True),
            ("BOX FILE", True),
            ("C D MARKER", True),
            ("CALCULATOR", True),
            ("CARBON PAPERS", True),
            ("CELLO TAPE", True),
            ("CUTTER", True),
            ("DUSTER", True),
            ("ERASER", True),
            ("FEVI STICK", True),
            ("GEL PEN BLACK", True),
            ("HIGH LIGHTER", True),
            ("L FOLDER", True),
            ("LETTER HEAD", True),
            ("LOGO ENVOLOP SMALL", True),
            ("NOTE PAD", True),
            ("PEN", True),
            ("PENCIL", True),
            ("PERMANENT MARKER", True),
            ("PUNCHING MACHINE", True),
            ("PUSH PIN", True),
            ("REGISTER", True),
            ("ROOM SPRAY", True),
            ("RUBBER BAND BAG", True),
            ("SCALE", True),
            ("SCISSOR", True),
            ("FILE SEPARATOR", True),
            ("SHARPENER", True),
            ("SKETCH PEN", True),
            ("SILVER PEN", True),
            ("SPRING FILE", True),
            ("STAMP PAD", True),
            ("STAMP PAD INK", True),
            ("STAPLER", True),
            ("STAPLER PIN BIG", True),
            ("STAPLER PIN SMALL", True),
            ("STICKY NOTE", True),
            ("TRANSPARENT FILE", True),
            ("U PIN", True),
            ("VISTING CARD HOLDER", True),
            ("WHITE BOARD MARKER", True),
            ("WHITE INK", True),
        ]

        for item in default_items:
            cursor.execute('''
                INSERT OR IGNORE INTO items (particular, available)
                VALUES (?, ?)
            ''', item)

        conn.commit()
        print("Items table initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing items: {e}")
    finally:
        conn.close()


def get_all_items():
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT particular, available FROM items')
        items = [dict(row) for row in cursor.fetchall()]
        return items
    except sqlite3.Error as e:
        print(f"Error fetching items: {e}")
        return []
    finally:
        conn.close()


def update_item_availability(particular, available):
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE items
            SET available = ?
            WHERE particular = ?
        ''', (int(available), particular))
        conn.commit()
        print(f"Item '{particular}' availability updated to {available}.")
    except sqlite3.Error as e:
        print(f"Error updating item availability: {e}")
    finally:
        conn.close()


def insert_user_with_items(emp_id, email, selected_items):
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return

    try:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (emp_id, email)
            VALUES (?, ?)
        ''', (emp_id, email))
        user_id = cursor.lastrowid

        for item in selected_items:
            cursor.execute('''
                INSERT INTO user_items (user_id, item)
                VALUES (?, ?)
            ''', (user_id, item))

        conn.commit()
        print(f"User with Employee ID {emp_id} and items added successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting user with items: {e}")
    finally:
        conn.close()


def is_valid_email(email):
    return email.endswith('@gmail.com') or email.endswith('@ceat.com')


def insert_request(name, email, description, emp_id, department):
    if not is_valid_email(email):
        print("Invalid email address. It must end with '@gmail.com' or '@ceat.com'.")
        return

    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (name, email, description, emp_id, department, status) 
            VALUES (?, ?, ?, ?, ?, ?)''',
            (name, email, description, emp_id, department, 'Pending'))
        conn.commit()
        print(f"Request by {name} inserted successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting request: {e}")
    finally:
        conn.close()


def get_all_requests():
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requests')
        requests = cursor.fetchall()
        return [dict(req) for req in requests]
    except sqlite3.Error as e:
        print(f"Error fetching requests: {e}")
        return []
    finally:
        conn.close()


def update_request_status(request_id, status):
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE requests SET status = ? WHERE id = ?', (status, request_id))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"No request found with ID {request_id}.")
        else:
            print(f"Request ID {request_id} status updated to '{status}'.")
    except sqlite3.Error as e:
        print(f"Error updating request status: {e}")
    finally:
        conn.close()


def reset_request_ids():
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return

    try:
        cursor = conn.cursor()

        cursor.execute('CREATE TEMPORARY TABLE temp_requests AS SELECT * FROM requests')

        cursor.execute('DELETE FROM requests')

        cursor.execute('DELETE FROM sqlite_sequence WHERE name="requests"')

        cursor.execute('''
            INSERT INTO requests (name, email, description, status) 
            SELECT name, email, description, status FROM temp_requests''')

        cursor.execute('DROP TABLE temp_requests')
        conn.commit()
        print("Request IDs reset successfully.")
    except sqlite3.Error as e:
        print(f"Error resetting request IDs: {e}")
    finally:
        conn.close()


def delete_request(request_id):
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM requests WHERE id = ?', (request_id,))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"No request found with ID {request_id}.")
        else:
            reset_request_ids()
            print(f"Request ID {request_id} deleted successfully.")
    except sqlite3.Error as e:
        print(f"Error deleting request: {e}")
    finally:
        conn.close()


initialize_items()
