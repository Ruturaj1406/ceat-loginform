# app.py

def load_css(file_path):
    """Loads an external CSS file and applies it to the Streamlit app.

    Args:
        file_path (str): Path to the CSS file.

    Notes:
        If the file is not found, the function silently fails without raising an error.
    """
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def format_timestamp(timestamp_str, tz_name='Asia/Kolkata'):
    """Formats a timestamp string into a human-readable format in the specified timezone.

    Args:
        timestamp_str (str or datetime): The timestamp to format (e.g., "2025-03-12 10:00:00").
        tz_name (str): Timezone name (default: 'Asia/Kolkata').

    Returns:
        str: Formatted timestamp (e.g., "March 12, 2025 10:00:00") or an error message if invalid.

    Raises:
        ValueError: If the timestamp string format is invalid.
        TypeError: If timestamp_str is not a string or datetime object.
    """
    if not timestamp_str:
        return "Not available"
    try:
        if isinstance(timestamp_str, datetime.datetime):
            utc_dt = timestamp_str
        else:
            utc_dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        utc_tz = pytz.utc
        if utc_dt.tzinfo is None:
            utc_dt = utc_tz.localize(utc_dt)
        local_tz = pytz.timezone(tz_name)
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime("%B %d, %Y %H:%M:%S")
    except (ValueError, TypeError) as e:
        print(f"Error parsing timestamp: {timestamp_str} - {e}")
        return f"Invalid date ({timestamp_str})"

def show_loading_animation(placeholder, message="Processing..."):
    """Displays a loading animation in the Streamlit app.

    Args:
        placeholder (streamlit.empty): A Streamlit placeholder object to display the animation.
        message (str): The message to show below the loading GIF (default: "Processing...").

    Notes:
        Pauses execution for 2 seconds to simulate processing time.
    """
    placeholder.markdown(
        """
        <div class="loading-container">
            <img src="https://blogger.googleusercontent.com/img/a/AVvXsEj3RLW4UZW49PBvV7pWj15YHMUuWCy49nXiRXzUuGc73_FBhacqQ6O5DnXRGwoyXAS2ZcEPoECGqVpTF2pqWuvakOEEZhbQ_iRNtQ8oYAMfviKUGhvPB3pCMX7iUnrU4KbNw8Zot0yxAZpztyLyZldljv-XRTJTYGs6xTsd8TSuVPUyrC8qfLab5kTTZQ4" 
                 alt="Loading..." style="width: 100px; height: 100px; display: block; margin: 0 auto;">
            <p style="text-align: center; color: #333;">{}</p>
        </div>
        """.format(message),
        unsafe_allow_html=True
    )
    time.sleep(2)

def validate_email(email):
    """Validates if an email address matches the allowed domains (ceat.com or gmail.com).

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@(ceat\.com|gmail\.com)$'
    return re.match(email_regex, email) is not None

def authenticate_dept_head(username, password):
    """Authenticates a department head based on username and password.

    Args:
        username (str): The department head's username.
        password (str): The department head's password.

    Returns:
        str or None: The department name if authenticated, None otherwise.
    """
    for dept, creds in st.session_state.DEPARTMENT_HEADS.items():
        if creds["username"] == username and creds["password"] == password:
            return dept
    return None

def display_header(info=None):
    """Displays a header with user info and a logout button.

    Args:
        info (dict, optional): Dictionary containing user details (e.g., email, emp_id, username, department).
    """
    cols = st.columns([110, 40])
    with cols[0]:
        if info:
            if 'email' in info:
                st.write(f"Email: {info['email']}")
            if 'emp_id' in info:
                st.write(f"Employee ID: {info['emp_id']}")
            if 'username' in info:
                st.write(f"Username: {info['username']}")
            if 'department' in info:
                st.write(f"Department: {info['department']}")
    with cols[1]:
        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.rerun()

def login():
    """Handles the login page UI and authentication logic."""
    # Implementation omitted for brevity; docstring focuses on purpose
    pass

def register():
    """Handles the registration page UI and user registration logic."""
    # Implementation omitted for brevity
    pass

def user_request_form():
    """Displays and processes the user request form."""
    # Implementation omitted for brevity
    pass

def display_my_orders():
    """Displays the user's order history."""
    # Implementation omitted for brevity
    pass

def user_dashboard():
    """Renders the user dashboard with request form and order history tabs."""
    # Implementation omitted for brevity
    pass

def dept_head_dashboard():
    """Renders the department head dashboard for managing department requests."""
    # Implementation omitted for brevity
    pass

def admin_dashboard():
    """Renders the admin dashboard for managing requests, inventory, and emails."""
    # Implementation omitted for brevity
    pass

def store_dashboard():
    """Renders the store dashboard for processing approved requests."""
    # Implementation omitted for brevity
    pass

def super_admin_dashboard():
    """Renders the super admin dashboard for managing all system entities."""
    # Implementation omitted for brevity
    pass

def main():
    """Main entry point for the Streamlit application."""
    # Implementation omitted for brevity
    pass