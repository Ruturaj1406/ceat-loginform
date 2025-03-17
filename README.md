Inventory Management System
A Streamlit-based web application designed for CEAT to manage inventory requests, approvals, and fulfillment. This system supports multiple user roles (User, Department Head, Admin, Store, Super Admin) with features like request submission, inventory tracking, email notifications, and a SQLite backend.

Table of Contents
Features
Folder Structure
Prerequisites
Installation
Usage
Roles and Dashboards
Configuration
Running Tests
Contributing
License
Features
Multi-Role Access: Supports Users, Department Heads, Admins, Store personnel, and a Super Admin.
Request Workflow: Users submit requests, which are approved/rejected by Department Heads and Admins, then processed by the Store.
Inventory Management: Tracks item quantities with low-stock alerts.
Email Notifications: Sends HTML emails for request updates (submitted, approved, rejected, delivered).
Custom UI: Styled with CSS for a polished look.
Database: Uses SQLite for persistent storage.
Folder Structure
inventory-management-system/

├── src/                    # Source code

│   ├── app.py             # Main Streamlit app

│   ├── database.py        # SQLite database operations

│   ├── mail.py            # Email sending utilities

│   ├── static/            # CSS and static assets

│   │   └── styles.css

│   └── utils/             # Helper functions

├── tests/                 # Unit tests

├── data/                  # SQLite database file

│   └── inventory.db

├── docs/                  # Documentation

│   ├── README.md          # This file

│   └── architecture.md    # System architecture details

├── requirements.txt       # Python dependencies

├── .env                   # Environment variables

├── .gitignore             # Git ignore rules

└── run.sh                 # Run script

Prerequisites
Python 3.8+
Git (optional, for version control)
A Gmail account with an App Password for email functionality
Installation
Clone the Repository (if using Git):
git clone https://github.com/your-username/inventory-management-system.git
cd inventory-management-system
Or download and extract the project ZIP file.
Install Dependencies:
pip install -r requirements.txt
Set Up Environment Variables:
Create a .env file in the root directory:
touch .env
Add Gmail credentials (replace with your own):
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-16-character-app-password
Generate an App Password in your Google Account settings under "Security > 2-Step Verification > App Passwords".
Initialize the Database:
Run database.py once to create data/inventory.db:
python src/database.py
Usage
Run the Application:
streamlit run src/app.py
Or use the provided script:
chmod +x run.sh
./run.sh
Access the App:
Open your browser to http://localhost:8501.
Login Credentials:
Super Admin: 123@ceat.com / 12
Admin: admin / admin123
Store: store / store123
Department Heads: Use department name (lowercase, no spaces) as username and <department>123 as password (e.g., fjs / fjs123).
Users: Register with a @ceat.com or @gmail.com email.
Roles and Dashboards
User: Submit requests and view order history.
Department Head: Approve/reject requests for their department.
Admin: Manage inventory, approve/reject requests, send emails.
Store: Process approved requests (pack, dispatch, deliver).
Super Admin: Manage users, departments, inventory, and credentials.
Configuration
Email: Update src/mail.py to use .env variables:
import os
from dotenv import load_dotenv
load_dotenv()
from_email = os.getenv("GMAIL_USER")
password = os.getenv("GMAIL_PASSWORD")
Database: Modify DATABASE path in src/database.py if needed:
DATABASE = "data/inventory.db"
CSS: Customize src/static/styles.css for UI changes.
Running Tests
Install Testing Dependencies (if not in requirements.txt):
pip install pytest
Run Tests:
pytest tests/
Note: Tests are not yet implemented; see tests/ for placeholders.
Contributing
Fork the repository.
Create a feature branch:
git checkout -b feature/your-feature
Commit changes:
git commit -m "Add your feature"
Push and create a pull request:
git push origin feature/your-feature
Please include tests and update documentation in docs/ as needed.

License
This project is licensed under the MIT License. See LICENSE for details (to be added).

Created by the Digital Team at CEAT

How to Use
Copy the Text: Select all the text above and copy it (Ctrl+C or Cmd+C).
Create the File:
Open a text editor (e.g., VS Code, Notepad).
Paste the text (Ctrl+V or Cmd+V).
Save as README.md in your docs/ directory (e.g., inventory-management-system/docs/README.md) or the root directory.
Verify: Open the file in a Markdown viewer (e.g., GitHub, VS Code with a Markdown extension) to ensure it renders correctly.