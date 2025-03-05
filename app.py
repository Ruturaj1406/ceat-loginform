import streamlit as st
import re
import datetime
import time
import pytz
from database import (
    register_user,
    login_user,
    get_all_items,
    insert_request,
    get_requests_by_emp_id,
    get_all_requests,
    update_request_status,
    delete_request,
    update_item_quantity,
    get_request_items,
    get_all_users
)
from mail import send_email

# Load external CSS
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Constants
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
STORE_USERNAME = "store"
STORE_PASSWORD = "store123"
DEPARTMENTS = ["IT", "Digital", "HR"]
DISPLAY_TIMEZONE = 'Asia/Kolkata'

# Helper function to format timestamps
def format_timestamp(timestamp_str, tz_name=DISPLAY_TIMEZONE):
    try:
        utc_tz = pytz.utc
        local_tz = pytz.timezone(tz_name)
        utc_dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        utc_dt = utc_tz.localize(utc_dt)
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime("%B %d, %Y %H:%M:%S")
    except ValueError as e:
        print(f"Error parsing timestamp: {timestamp_str} - {e}")
        return "Invalid date"

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.clear()
    st.session_state.page = "login"
    st.session_state.is_user_logged_in = False
    st.session_state.is_admin = False
    st.session_state.is_store = False
    st.session_state.user_details = {}
    st.session_state.show_login_success = False
    st.session_state.request_submitted = False

# Validation functions
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@(ceat\.com|gmail\.com)$'
    return re.match(email_regex, email) is not None

# Registration function (Updated)
def register():
    st.title("Register")
    email = st.text_input("Email", key="register_email")
    emp_id = st.text_input("Official Employee ID", key="register_emp_id")
    confirm_emp_id = st.text_input("Confirm Employee ID", key="confirm_emp_id")  # New confirmation field
    
    col1, col2 = st.columns(2)
    with col1:
        register_btn = st.button("Register", key="register_btn")
    with col2:
        go_to_login_btn = st.button("Go to Login", key="go_to_login_btn")

    if register_btn:
        if not email or not emp_id or not confirm_emp_id:
            st.error("All fields are required.")
        elif emp_id != confirm_emp_id:
            st.error("Employee ID and confirmation do not match.")
        elif not validate_email(email):
            st.error("Invalid email format (must end with @ceat.com or @gmail.com).")
        else:
            success = register_user(email, emp_id, emp_id)  # Assuming password is emp_id
            if success:
                st.success(f"Registration successful! Your Employee ID is {emp_id}. Please log in.")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Email or Employee ID already registered. Check server logs for details.")

    if go_to_login_btn:
        st.session_state.page = "login"
        st.rerun()

# User login function
def user_login():
    st.title("User Login")
    email = st.text_input("Email", key="login_email")
    emp_id = st.text_input("Employee ID", key="login_emp_id")
    
    col1, col2 = st.columns(2)
    with col1:
        login_btn = st.button("Login", key="login_btn")
    with col2:
        go_to_register_btn = st.button("Go to Register", key="go_to_register_btn")

    if login_btn:
        if not email or not emp_id:
            st.error("All fields are required.")
        else:
            user = login_user(email, emp_id)
            if user:
                st.session_state.is_user_logged_in = True
                st.session_state.user_details = {
                    "email": user["email"],
                    "emp_id": user["emp_id"]
                }
                st.session_state.show_login_success = True
                st.rerun()
            else:
                st.error("Invalid email or employee ID.")

    if go_to_register_btn:
        st.session_state.page = "register"
        st.rerun()

# Admin login function
def admin_login_main():
    st.title("Admin Login")
    username = st.text_input("Username", key="admin_username_main")
    password = st.text_input("Password", type="password", key="admin_password_main")
    admin_email = st.text_input("Admin Email", key="admin_email_main")
    if st.button("Login", key="admin_login_btn_main"):
        if not username or not password or not admin_email:
            st.error("All fields are required.")
        elif not validate_email(admin_email):
            st.error("Invalid email format (must end with @ceat.com or @gmail.com).")
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.session_state.login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
        else:
            st.error("Invalid credentials.")

# Store login function
def store_login():
    st.title("Store Login")
    username = st.text_input("Username", key="store_username")
    password = st.text_input("Password", type="password", key="store_password")
    if st.button("Login", key="store_login_btn"):
        if not username or not password:
            st.error("All fields are required.")
        elif username == STORE_USERNAME and password == STORE_PASSWORD:
            st.session_state.is_store = True
            st.session_state.login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()
        else:
            st.error("Invalid credentials.")

# User request form
def user_request_form():
    if st.session_state.get("show_login_success", False):
        st.success("Login successful!")
        st.session_state.show_login_success = False

    st.title("Request Form")
    user_name = st.text_input("Enter your Name", key="request_name")
    user_email = st.session_state.user_details.get("email", "")
    st.text_input("Email", value=user_email, disabled=True, key="request_email")

    # Department selection
    st.selectbox(
        "Select Department",
        options=DEPARTMENTS,
        key="selected_department"
    )
    if "selected_department" in st.session_state:
        st.session_state.user_details["department"] = st.session_state.selected_department

    # Initialize selected_items if not present
    if "selected_items" not in st.session_state:
        st.session_state.selected_items = {}

    # Fetch items and create item map
    items = get_all_items()
    item_map = {item["id"]: {"particular": item["particular"], "quantity": item["quantity"]} for item in items}

    # Add Items section with quantity selection
    with st.expander("Add Items", expanded=True):
        # List available items (not selected and quantity > 0) with None as default
        available_item_ids = [None] + [item["id"] for item in items if item["id"] not in st.session_state.selected_items and item["quantity"] > 0]
        selected_item_id = st.selectbox(
            "Select item to add",
            options=available_item_ids,
            format_func=lambda id: "Select an item" if id is None else item_map[id]["particular"],
            key="add_item_select"
        )
        if selected_item_id is not None:
            # Show quantity input if an item is selected
            max_qty = item_map[selected_item_id]["quantity"]
            qty = st.number_input(
                "Quantity",
                min_value=1,
                max_value=max_qty,
                value=1,
                key=f"add_qty_{selected_item_id}"
            )
            if st.button("Add", key="add_item_btn"):
                if qty > 0 and qty <= max_qty:
                    st.session_state.selected_items[selected_item_id] = qty
                    st.rerun()
                else:
                    st.error(f"Invalid quantity. Maximum available: {max_qty}")
        else:
            st.write("Please select an item to add.")

    # Display selected items without quantity edit option
    if st.session_state.selected_items:
        st.subheader("Selected Items")
        for item_id in list(st.session_state.selected_items.keys()):
            item_name = item_map[item_id]["particular"]
            qty = st.session_state.selected_items[item_id]
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{item_name} (Qty: {qty})")
            with col2:
                if st.button("Remove", key=f"remove_{item_id}"):
                    del st.session_state.selected_items[item_id]
                    st.rerun()
    else:
        st.info("No items selected yet.")

    # Suggestion and submit
    suggestion = st.text_area("Suggestion for Admin (optional)", key="suggestion_input")
    submit_button = st.button("Submit Request", key="submit_request_btn")

    if submit_button:
        if not user_name.strip():
            st.error("Please enter your name.")
        elif "department" not in st.session_state.user_details:
            st.error("Please select a department.")
        elif not st.session_state.selected_items:
            st.error("Please select at least one available item.")
        else:
            formatted_description = ", ".join(
                [f"{item_map[item_id]['particular']} (Qty: {qty})" for item_id, qty in st.session_state.selected_items.items()]
            )
            selected_items_list = [{"item_id": k, "quantity": v} for k, v in st.session_state.selected_items.items()]
            user_details = st.session_state.user_details

            animation_placeholder = st.empty()
            animation_placeholder.markdown(
                """
                <div class="loading-container">
                    <img src="https://blogger.googleusercontent.com/img/a/AVvXsEj3RLW4UZW49PBvV7pWj15YHMUuWCy49nXiRXzUuGc73_FBhacqQ6O5DnXRGwoyXAS2ZcEPoECGqVpTF2pqWuvakOEEZhbQ_iRNtQ8oYAMfviKUGhvPB3pCMX7iUnrU4KbNw8Zot0yxAZpztyLyZldljv-XRTJTYGs6xTsd8TSuVPUyrC8qfLab5kTTZQ4" 
                         alt="Loading..." style="width: 100px; height: 100px; display: block; margin: 0 auto;">
                    <p style="text-align: center; color: #333;">Processing your request...</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(2)

            success, message = insert_request(
                user_name,
                user_details["email"],
                user_details["emp_id"],
                user_details["department"],
                selected_items_list,
                formatted_description,
                suggestion if suggestion.strip() else None
            )

            animation_placeholder.empty()

            if success:
                try:
                    subject = "Request Submission Confirmation"
                    body = f"Dear {user_name},\nYour request has been successfully submitted.\nThank you for using our service!"
                    send_email(
                        to_email=user_email,
                        admin_name="Admin",
                        subject=subject,
                        body=body,
                        request_details={"name": user_name, "email": user_email, "description": formatted_description}
                    )
                    st.success("Request submitted successfully! Check 'My Orders' to view it.")
                except Exception as e:
                    st.warning(f"Request submitted, but email failed: {e}")
                st.session_state.selected_items = {}
                st.session_state.request_submitted = True
            else:
                st.error(message)

# Display user's orders
def display_my_orders():
    st.subheader("My Orders")
    emp_id = st.session_state.user_details.get("emp_id", "")
    if not emp_id:
        st.error("Employee ID not found. Please log in again.")
        return
    
    requests = get_requests_by_emp_id(emp_id)
    if requests:
        for req in requests:
            req_id = req["id"]
            created_at = format_timestamp(req["created_at"])
            description = req["description"]
            status = req["status"]
            updated_at = format_timestamp(req.get("updated_at", req["created_at"]))
            
            st.write(f"**Request ID:** {req_id}")
            st.write(f"**Date Submitted:** {created_at}")
            st.write(f"**Description:** {description}")
            if status == "Approved":
                st.markdown(f"**Status:** <span style='color:green'>{status}</span>", unsafe_allow_html=True)
            elif status == "Rejected":
                st.markdown(f"**Status:** <span style='color:red'>{status}</span>", unsafe_allow_html=True)
            elif status == "Delivered":
                st.markdown(f"**Status:** <span style='color:green'>{status}</span>", unsafe_allow_html=True)
                delivered_to = req.get("delivered_to", "N/A")
                st.write(f"**Delivered to:** {delivered_to}")
            else:
                st.write(f"**Status:** {status}")
            st.write(f"**Last Updated:** {updated_at}")
            st.write("---")
    else:
        st.info("You have no orders yet.")

# User dashboard
def user_dashboard():
    with st.sidebar:
        st.header("User Panel")
        st.write(f"Logged in as: {st.session_state.user_details.get('email', 'N/A')}")
        st.write(f"Employee ID: {st.session_state.user_details.get('emp_id', 'N/A')}")
        if st.button("Logout"):
            st.session_state.is_user_logged_in = False
            st.session_state.user_details = {}
            st.session_state.show_login_success = False
            st.session_state.request_submitted = False
            st.rerun()

    tab1, tab2 = st.tabs(["Request Form", "My Orders"])
    with tab1:
        user_request_form()
    with tab2:
        display_my_orders()

# Admin dashboard
def admin_dashboard():
    with st.sidebar:
        st.header("Admin Panel")
        st.write(f"Username: {ADMIN_USERNAME}")
        if st.button("Logout", key="admin_logout_btn"):
            st.session_state.is_admin = False
            st.session_state.login_time = None
            st.rerun()

    st.title("Admin Dashboard")

    # Fetch items once
    items = get_all_items()

    # Low Stock Alerts section
    low_stock_items = [item for item in items if item["quantity"] <= 10]
    if low_stock_items:
        st.subheader("Low Stock Alerts")
        st.write(f"There are {len(low_stock_items)} items with low stock:")
        for item in low_stock_items:
            st.markdown(f"- **{item['particular']}**: {item['quantity']} left", unsafe_allow_html=True)
    else:
        st.info("All items are sufficiently stocked.")

    requests = get_all_requests()
    if requests:
        for req in requests:
            req_id = req.get("id", "N/A")
            emp_id = req.get("emp_id", "N/A")
            name = req.get("name", "N/A")
            department = req.get("department", "N/A")
            email = req.get("email", "N/A")
            status = req.get("status", "Pending")
            description = req.get("description", "N/A")
            suggestion = req.get("suggestion", "N/A")

            with st.expander(f"Request ID: {req_id}", expanded=False):
                st.write(f"**Employee ID:** {emp_id}")
                st.write(f"**Name:** {name}")
                st.write(f"**Department:** {department}")
                st.write(f"**Email:** {email}")
                st.write(f"**Description:** {description}")
                st.write(f"**Suggestion:** {suggestion}")
                st.write(f"**Status:** {status}")
                st.write(f"**Created At:** {format_timestamp(req['created_at'])}")
                st.write(f"**Updated At:** {format_timestamp(req['updated_at'])}")

                status_update = st.radio(
                    f"Status for {req_id}",
                    ["Pending", "Approved", "Rejected", "Packing", "Dispatched", "Delivered"],
                    index=["Pending", "Approved", "Rejected", "Packing", "Dispatched", "Delivered"].index(status),
                    key=f"status_radio_{req_id}"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Update {req_id}", key=f"update_btn_{req_id}"):
                        success, message = update_request_status(req_id, status_update)
                        if success:
                            subject = f"Request {status_update}"
                            body = f"Your request {req_id} has been {status_update.lower()}.\n\nDetails:\n{description}"
                            send_email(email, "Admin", subject, body, request_details=req)
                            st.success(f"Updated request {req_id}")
                        else:
                            st.error(f"Failed to update request {req_id}: {message}")
                        st.rerun()
                with col2:
                    if st.button(f"Delete {req_id}", key=f"delete_btn_{req_id}"):
                        delete_request(req_id)
                        st.success(f"Deleted request {req_id}")
                        st.rerun()
    else:
        st.info("No requests available")

    with st.expander("Manage Item Availability", expanded=False):
        search_query = st.text_input("Search Items", key="admin_item_search")
        filtered_items = [item for item in items if search_query.lower() in item["particular"].lower()]
        for item in filtered_items:
            col1, col2 = st.columns([4, 1])
            with col1:
                if item["quantity"] <= 10:
                    st.markdown(f"<span style='color:red'>{item['particular']}</span> (Qty: {item['quantity']})", unsafe_allow_html=True)
                else:
                    st.write(f"{item['particular']} (Qty: {item['quantity']})")
            with col2:
                new_quantity = st.number_input(
                    f"Set Qty for {item['particular']}",
                    min_value=0,
                    value=item["quantity"],
                    key=f"qty_{item['id']}"
                )
                if st.button(f"Update {item['particular']}", key=f"update_qty_{item['id']}"):
                    if update_item_quantity(item["id"], new_quantity):
                        st.success(f"Updated {item['particular']} quantity to {new_quantity}")
                        st.rerun()
                    else:
                        st.error(f"Failed to update {item['particular']} quantity")

    # Send Email to User section
    st.subheader("Send Email to User")
    users = get_all_users()
    if users:
        # Format dropdown options as "emp_id - email"
        user_options = [f"{emp_id} - {email}" for emp_id, email in users]
        selected_user = st.selectbox(
            "Select User",
            options=range(len(users)),  # Use indices as options
            format_func=lambda i: user_options[i]  # Display "emp_id - email"
        )
        selected_email = users[selected_user][1]  # Extract email from selected tuple
        email_subject = st.text_input("Email Subject")
        email_body = st.text_area("Email Body")
        if st.button("Send Email"):
            if selected_email and email_subject and email_body:
                try:
                    send_email(
                        to_email=selected_email,
                        admin_name="Admin",
                        subject=email_subject,
                        body=email_body,
                        request_details=None
                    )
                    st.success(f"Email sent to {selected_email}")
                except Exception as e:
                    st.error(f"Failed to send email: {e}")
            else:
                st.warning("Please fill in all fields.")
    else:
        st.info("No users found.")

# Store dashboard
def store_dashboard():
    with st.sidebar:
        st.header("Store Panel")
        st.write(f"Username: {STORE_USERNAME}")
        if st.button("Logout", key="store_logout_btn"):
            st.session_state.is_store = False
            st.session_state.login_time = None
            st.rerun()
    st.title("Store Dashboard")
    requests = get_all_requests()
    approved_requests = [req for req in requests if req["status"] in ["Approved", "Packing", "Dispatched", "Delivered"]]
    if approved_requests:
        for req in approved_requests:
            req_id = req["id"]
            emp_id = req["emp_id"]
            name = req["name"]
            department = req["department"]
            email = req["email"]
            status = req["status"]
            description = req["description"]
            updated_at = format_timestamp(req.get("updated_at", req["created_at"]))

            with st.expander(f"Request ID: {req_id} - {status}", expanded=False):
                st.write(f"**Employee ID:** {emp_id}")
                st.write(f"**Name:** {name}")
                st.write(f"**Department:** {department}")
                st.write(f"**Email:** {email}")
                st.write(f"**Description:** {description}")
                st.write(f"**Current Status:** {status}")
                st.write(f"**Last Updated:** {updated_at}")

                if status == "Approved":
                    if st.button(f"Start Packing for {req_id}", key=f"start_packing_{req_id}"):
                        success, message = update_request_status(req_id, "Packing")
                        if success:
                            st.success(f"Started packing for request {req_id}")
                            st.rerun()
                        else:
                            st.error(f"Failed to update status to 'Packing' for request {req_id}: {message}")
                elif status == "Packing":
                    if st.button(f"Mark as Dispatched for {req_id}", key=f"dispatch_{req_id}"):
                        success, message = update_request_status(req_id, "Dispatched")
                        if success:
                            st.success(f"Marked as dispatched for request {req_id}")
                            st.rerun()
                        else:
                            st.error(f"Failed to update status to 'Dispatched' for request {req_id}: {message}")
                elif status == "Dispatched":
                    delivered_to = st.text_input(f"Enter the name of the person who received the item for Request {req_id}", 
                                                key=f"delivered_to_{req_id}")
                    if st.button(f"Mark as Delivered for {req_id}", key=f"deliver_{req_id}"):
                        if delivered_to.strip():
                            success, message = update_request_status(req_id, "Delivered", delivered_to=delivered_to.strip())
                            if success:
                                delivery_time = format_timestamp(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
                                subject = "Request Delivered"
                                body = f"Your requested item has been delivered to {delivered_to}."
                                try:
                                    send_email(
                                        to_email=email,
                                        admin_name="Store Team",
                                        subject=subject,
                                        body=body,
                                        request_details=req,
                                        delivered_to=delivered_to,
                                        delivery_time=delivery_time
                                    )
                                    st.success(f"Marked as delivered for request {req_id} to {delivered_to}. Email sent to {email}.")
                                except Exception as e:
                                    st.error(f"Marked as delivered for request {req_id} to {delivered_to}, but email failed: {e}")
                                    print(f"Email sending error: {e}")
                                st.rerun()
                            else:
                                st.error(f"Failed to update status to 'Delivered' for request {req_id}: {message}")
                        else:
                            st.warning("Please enter the name of the person who received the item.")
                elif status == "Delivered":
                    delivered_to = req.get("delivered_to", "N/A")
                    st.write(f"**Delivered to:** {delivered_to}")
    else:
        st.info("No approved requests to handle.")

# Main function
def main():
    load_css()
    st.markdown(
        """
        <img src="https://www.itvoice.in/wp-content/uploads/2023/01/CEAT-Tyre-logo-2000x1000-1.png" class="logo">
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown('<div class="sidebar-bottom"><span>created by digital team</span></div>', unsafe_allow_html=True)

    if st.session_state.is_user_logged_in:
        user_dashboard()
    elif st.session_state.is_admin:
        admin_dashboard()
    elif st.session_state.is_store:
        store_dashboard()
    elif st.session_state.page == "register":
        register()
    else:
        with st.sidebar:
            login_type = st.radio("Login Type", ["User", "Admin", "Store"])
        if login_type == "User":
            user_login()
        elif login_type == "Admin":
            admin_login_main()
        elif login_type == "Store":
            store_login()

if __name__ == "__main__":
    main()