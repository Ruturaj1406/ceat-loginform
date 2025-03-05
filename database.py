import sqlite3
import os
import datetime

# Use an absolute path for the database file to ensure consistency
DB_PATH = os.path.join(os.path.dirname(__file__), 'requests.db')

def get_db_connection():
    """Establish a connection to the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database at {DB_PATH}: {e}")
        return None

def initialize_db():
    """Initialize the database with required tables and default items, and migrate if needed."""
    conn = get_db_connection()
    if conn is None:
        print("Failed to initialize database due to connection issue.")
        return

    try:
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                emp_id TEXT UNIQUE NOT NULL
            )
        ''')

        # Items table with quantity
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                particular TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0
            )
        ''')

        # Requests table with delivered_to column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                emp_id TEXT NOT NULL,
                department TEXT NOT NULL,
                description TEXT NOT NULL,
                suggestion TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                delivered_to TEXT
            )
        ''')

        # Migration: Add delivered_to column if it doesn’t exist
        cursor.execute("PRAGMA table_info(requests)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'delivered_to' not in columns:
            print("Adding 'delivered_to' column to existing 'requests' table.")
            cursor.execute('ALTER TABLE requests ADD COLUMN delivered_to TEXT')
            print("'delivered_to' column added successfully.")

        # Request_items table to link requests with items and quantities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (request_id) REFERENCES requests(id),
                FOREIGN KEY (item_id) REFERENCES items(id)
            )
        ''')

        # Insert default items only if the items table is empty
        cursor.execute('SELECT COUNT(*) FROM items')
        if cursor.fetchone()[0] == 0:
            default_items = [
                ("A3 ENVELOPE GREEN", 100), ("A3 PAPER", 100), ("A3 TRANSPARENT FOLDER", 100),
                ("A4 ENVELOPE GREEN", 100), ("A4 LOGO ENVELOPE", 100), ("A4 PAPER", 100),
                ("A4 TRANSPARENT FOLDER", 100), ("BINDER CLIP 19MM", 100), ("BINDER CLIP 25MM", 100),
                ("BINDER CLIP 41MM", 100), ("BOX FILE", 100), ("CD MARKER", 100),
                ("CALCULATOR", 100), ("CARBON PAPERS", 100), ("CELLO TAPE", 100),
                ("CUTTER", 100), ("DUSTER", 100), ("ERASER", 100), ("FEVI STICK", 100),
                ("GEL PEN BLACK", 100), ("HIGH LIGHTER", 100), ("L FOLDER", 100),
                ("LETTER HEAD", 100), ("LOGO ENVELOPE SMALL", 100), ("NOTE PAD", 100),
                ("PEN", 100), ("PENCIL", 100), ("PERMANENT MARKER", 100),
                ("PUNCHING MACHINE", 100), ("PUSH PIN", 100), ("REGISTER", 100),
                ("ROOM SPRAY", 100), ("RUBBER BAND BAG", 100), ("SCALE", 100),
                ("SCISSOR", 100), ("FILE SEPARATOR", 100), ("SHARPENER", 100),
                ("SKETCH PEN", 100), ("SILVER PEN", 100), ("SPRING FILE", 100),
                ("STAMP PAD", 100), ("STAMP PAD INK", 100), ("STAPLER", 100),
                ("STAPLER PIN BIG", 100), ("STAPLER PIN SMALL", 100), ("STICKY NOTE", 100),
                ("TRANSPARENT FILE", 100), ("U PIN", 100), ("VISITING CARD HOLDER", 100),
                ("WHITE BOARD MARKER", 100), ("WHITE INK", 100),
            ]
            cursor.executemany('INSERT INTO items (particular, quantity) VALUES (?, ?)', default_items)
        conn.commit()
        print("Database initialized successfully with all tables and default items.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def register_user(email, password, emp_id):
    """Register a new user."""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password, emp_id) VALUES (?, ?, ?)', 
                       (email, password, emp_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Registration failed: Email or emp_id already exists - {e}")
        return False
    except sqlite3.Error as e:
        print(f"Error registering user: {e}")
        return False
    finally:
        conn.close()

def login_user(email, password):
    """Authenticate a user."""
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                       (email, password))
        user = cursor.fetchone()
        return dict(user) if user else None
    except sqlite3.Error as e:
        print(f"Error during login: {e}")
        return None
    finally:
        conn.close()

def get_all_items():
    """Fetch all items from the database."""
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, particular, quantity FROM items')
        items = [dict(row) for row in cursor.fetchall()]
        return items
    except sqlite3.Error as e:
        print(f"Error fetching items: {e}")
        return []
    finally:
        conn.close()

def update_item_quantity(item_id, quantity):
    """Update item quantity."""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE items SET quantity = ? WHERE id = ?', 
                       (quantity, item_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating item quantity: {e}")
        return False
    finally:
        conn.close()

def insert_request(name, email, emp_id, department, selected_items, description, suggestion=None):
    """Insert a new request with items and quantities."""
    conn = get_db_connection()
    if conn is None:
        print("Database connection failed in insert_request.")
        return False, "Database connection failed"
    try:
        cursor = conn.cursor()
        # Validate quantities
        for item in selected_items:
            cursor.execute('SELECT particular, quantity FROM items WHERE id = ?', (item["item_id"],))
            row = cursor.fetchone()
            if row and item["quantity"] > row["quantity"]:
                return False, f"Currently, only {row['quantity']} quantity is available for {row['particular']}"

        # Insert request
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO requests 
            (name, email, emp_id, department, description, suggestion, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, emp_id, department, description, suggestion, 'Pending', now, now))
        request_id = cursor.lastrowid

        # Insert request items
        for item in selected_items:
            cursor.execute('INSERT INTO request_items (request_id, item_id, quantity) VALUES (?, ?, ?)', 
                           (request_id, item["item_id"], item["quantity"]))
        conn.commit()
        return True, "Request submitted successfully"
    except sqlite3.Error as e:
        print(f"Error inserting request: {e}")
        return False, str(e)
    finally:
        conn.close()

def get_all_requests():
    """Fetch all requests for the admin or store dashboard."""
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requests ORDER BY created_at DESC')
        requests = [dict(req) for req in cursor.fetchall()]
        return requests
    except sqlite3.Error as e:
        print(f"Error fetching all requests: {e}")
        return []
    finally:
        conn.close()

def get_requests_by_emp_id(emp_id):
    """Fetch requests for a specific employee."""
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM requests WHERE emp_id = ? ORDER BY created_at DESC', (emp_id,))
        requests = [dict(req) for req in cursor.fetchall()]
        return requests
    except sqlite3.Error as e:
        print(f"Error fetching requests for emp_id {emp_id}: {e}")
        return []
    finally:
        conn.close()

def get_request_items(request_id):
    """Fetch items associated with a request."""
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ri.request_id, ri.item_id, ri.quantity, i.particular 
            FROM request_items ri 
            JOIN items i ON ri.item_id = i.id 
            WHERE ri.request_id = ?
        ''', (request_id,))
        items = [dict(row) for row in cursor.fetchall()]
        return items
    except sqlite3.Error as e:
        print(f"Error fetching request items: {e}")
        return []
    finally:
        conn.close()

def update_request_status(request_id, status, delivered_to=None):
    """Update the status of a request and optionally set delivered_to."""
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database in update_request_status.")
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if request exists
        cursor.execute('SELECT status FROM requests WHERE id = ?', (request_id,))
        result = cursor.fetchone()
        if not result:
            return False, f"No request found with ID {request_id}"
        
        current_status = result['status']
        
        # Update status and delivered_to if provided
        if status == "Delivered" and delivered_to:
            cursor.execute('''
                UPDATE requests 
                SET status = ?, updated_at = ?, delivered_to = ? 
                WHERE id = ?
            ''', (status, now, delivered_to, request_id))
        else:
            cursor.execute('''
                UPDATE requests 
                SET status = ?, updated_at = ? 
                WHERE id = ?
            ''', (status, now, request_id))
        
        conn.commit()
        rows_affected = cursor.rowcount
        if rows_affected > 0:
            return True, "Status updated successfully"
        else:
            return False, f"Status is already '{current_status}' or no update needed"
    except sqlite3.Error as e:
        print(f"Database error updating request {request_id}: {e}")
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def delete_request(request_id):
    """Delete a request and its associated items."""
    conn = get_db_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM request_items WHERE request_id = ?', (request_id,))
        cursor.execute('DELETE FROM requests WHERE id = ?', (request_id,))
        conn.commit()
        print(f"Request {request_id} deleted")
    except sqlite3.Error as e:
        print(f"Error deleting request: {e}")
    finally:
        conn.close()

def get_all_users():
    """Fetch all user employee IDs and emails from the database."""
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT emp_id, email FROM users')
        users = [(row['emp_id'], row['email']) for row in cursor.fetchall()]
        return users
    except sqlite3.Error as e:
        print(f"Error fetching users: {e}")
        return []
    finally:
        conn.close()

# Call this at startup to ensure DB is initialized and migrated
initialize_db()