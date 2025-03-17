import sqlite3
from datetime import datetime
import pytz

# Database file
DATABASE = "requests.db"

# Initialize database and create tables if they don't exist
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            emp_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Department Heads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS department_heads (
            department TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    """)

    # Admin table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO admin (username, password) VALUES ('admin', 'admin123')")

    # Store table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS store (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO store (username, password) VALUES ('store', 'store123')")

    # Items table with UNIQUE constraint on 'particular' to avoid duplicates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            particular TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL
        )
    """)
    # Insert default items with an initial quantity of 100 for each
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
    cursor.executemany("INSERT OR IGNORE INTO items (particular, quantity) VALUES (?, ?)", default_items)

    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM items")
    item_count = cursor.fetchone()[0]
    print(f"Initialized {item_count} items in the database.")

    # Requests table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            emp_id TEXT NOT NULL,
            department TEXT NOT NULL,
            description TEXT NOT NULL,
            suggestion TEXT,
            status TEXT DEFAULT 'Pending Department Approval',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            delivered_to TEXT,
            FOREIGN KEY (emp_id) REFERENCES users(emp_id)
        )
    """)

    # Request Items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_items (
            request_id INTEGER,
            item_id INTEGER,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (request_id) REFERENCES request(id),
            FOREIGN KEY (item_id) REFERENCES items(id),
            PRIMARY KEY (request_id, item_id)
        )
    """)

    conn.commit()
    conn.close()

# User functions
def register_user(email, emp_id, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, emp_id, password) VALUES (?, ?, ?)", (email, emp_id, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT email, emp_id FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return {"email": user[0], "emp_id": user[1]} if user else None

def get_all_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user(emp_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE emp_id = ?", (emp_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def update_user_password(emp_id, new_password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE emp_id = ?", (new_password, emp_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Department Head functions
def get_all_department_heads():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT department, username, password, email FROM department_heads")
    heads = {row[0]: {"username": row[1], "password": row[2], "email": row[3]} for row in cursor.fetchall()}
    conn.close()
    return heads

def add_department_head(department, username, password, email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO department_heads (department, username, password, email) VALUES (?, ?, ?, ?)",
                       (department, username, password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_department_head_password(department, new_password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE department_heads SET password = ? WHERE department = ?", (new_password, department))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def update_department_head_email(department, new_email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE department_heads SET email = ? WHERE department = ?", (new_email, department))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def delete_department_head(department):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM department_heads WHERE department = ?", (department,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Admin functions
def get_admin_credentials():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM admin LIMIT 1")
    admin = cursor.fetchone()
    conn.close()
    return {"username": admin[0], "password": admin[1]} if admin else {"username": "admin", "password": "admin123"}

def update_admin_password(new_password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE admin SET password = ? WHERE username = 'admin'", (new_password,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Store functions
def get_store_credentials():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM store LIMIT 1")
    store = cursor.fetchone()
    conn.close()
    return {"username": store[0], "password": store[1]} if store else {"username": "store", "password": "store123"}

def update_store_password(new_password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE store SET password = ? WHERE username = 'store'", (new_password,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Item functions
def get_all_items():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, particular, quantity FROM items WHERE quantity > 0")
    items = [{"id": row[0], "particular": row[1], "quantity": row[2]} for row in cursor.fetchall()]
    conn.close()
    return items

def add_item(particular, quantity):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO items (particular, quantity) VALUES (?, ?)", (particular, quantity))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remove_item(item_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def update_item_quantity(item_id, new_quantity):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE items SET quantity = ? WHERE id = ?", (new_quantity, item_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

# Request functions
def insert_request(name, email, emp_id, department, items, description, suggestion):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO request (name, email, emp_id, department, description, suggestion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, emp_id, department, description, suggestion))
        
        request_id = cursor.lastrowid
        
        for item in items:
            cursor.execute("INSERT INTO request_items (request_id, item_id, quantity) VALUES (?, ?, ?)",
                           (request_id, item["item_id"], item["quantity"]))
        
        conn.commit()
        return True, "Request inserted successfully"
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {str(e)}")
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def get_requests_by_emp_id(emp_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, description, status, updated_at, delivered_to 
        FROM request 
        WHERE emp_id = ?
    """, (emp_id,))
    requests = [{"id": row[0], "created_at": row[1], "description": row[2], "status": row[3], 
                 "updated_at": row[4], "delivered_to": row[5]} for row in cursor.fetchall()]
    conn.close()
    return requests

def get_all_requests():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, emp_id, name, department, email, description, suggestion, status, created_at, updated_at, delivered_to 
        FROM request
    """)
    requests = [{"id": row[0], "emp_id": row[1], "name": row[2], "department": row[3], "email": row[4], 
                 "description": row[5], "suggestion": row[6], "status": row[7], "created_at": row[8], 
                 "updated_at": row[9], "delivered_to": row[10]} for row in cursor.fetchall()]
    conn.close()
    return requests

def get_requests_by_department(department):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, emp_id, name, email, description, status, created_at, updated_at 
        FROM request 
        WHERE department = ?
    """, (department,))
    requests = [{"id": row[0], "emp_id": row[1], "name": row[2], "email": row[3], "description": row[4], 
                 "status": row[5], "created_at": row[6], "updated_at": row[7]} for row in cursor.fetchall()]
    conn.close()
    return requests

def update_request_status(request_id, status, delivered_to=None):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        if delivered_to:
            cursor.execute("""
                UPDATE request 
                SET status = ?, updated_at = CURRENT_TIMESTAMP, delivered_to = ? 
                WHERE id = ?
            """, (status, delivered_to, request_id))
        else:
            cursor.execute("""
                UPDATE request 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (status, request_id))
        conn.commit()
        return True, "Status updated"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()

def delete_request(request_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM request_items WHERE request_id = ?", (request_id,))
        cursor.execute("DELETE FROM request WHERE id = ?", (request_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_request_items(request_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, quantity FROM request_items WHERE request_id = ?", (request_id,))
    items = [{"item_id": row[0], "quantity": row[1]} for row in cursor.fetchall()]
    conn.close()
    return items

# Placeholder for department emails
def get_department_emails():
    return {}

def update_department_email(department, email):
    return True

# Initialize database
init_db()

if __name__ == "__main__":
    print("Database initialized.")
    # Test item retrieval
    items = get_all_items()
    print(f"Retrieved {len(items)} items: {items}")