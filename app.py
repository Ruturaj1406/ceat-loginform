import streamlit as st
import re
import datetime
import time
import pytz
from mail import send_email  # Assuming this exists from your original code

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
    get_all_users,
    get_requests_by_department,
    delete_user,
    update_user_password,
    add_item,
    remove_item,
    get_all_department_heads,
    add_department_head,
    update_department_head_password,
    update_department_head_email,
    delete_department_head,
    get_admin_credentials,
    update_admin_password,
    get_store_credentials,
    update_store_password,
    get_department_emails,
    update_department_email,
)

# Load external CSS
def load_css(file_path):
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

# Constants and initial session state setup
SUPER_ADMIN_EMAIL = "123@ceat.com"
SUPER_ADMIN_PASSWORD = "Ceat@123"  # Changed to SUPER_ADMIN_PASSWORD for clarity
DISPLAY_TIMEZONE = 'Asia/Kolkata'

if 'DEPARTMENTS' not in st.session_state:
    st.session_state.DEPARTMENTS = [
        "FJS", "MIXTURE", "MIXTURE QLF LAB", "TBR STOCK", "PCR STOCK",
        "TBR STOCK ELECTRICAL MAINTENANCE", "TBR STOCK MECHANICAL MAINTENANCE",
        "PCR STOCK ELECTRICAL MAINTENANCE", "PCR STOCK MECHANICAL MAINTENANCE",
        "ACADEMY", "PM SELL", "PCR BUILDING", "TBR BUILDING",
        "PCR BUILDING ELECTRICAL MAINTENANCE", "TBR CURING/FF", "PCR CURING/FF",
        "HR", "PROJECT", "PURCHASE", "STORE", "FINANCE", "DIGITAL", "IT"
    ]

if 'DEPARTMENT_HEADS' not in st.session_state:
    db_dept_heads = get_all_department_heads()
    if not db_dept_heads:
        initial_dept_heads = {
            dept: {"username": dept.lower().replace(" ", "_"), "password": dept.lower().replace(" ", "_") + "123", "email": ""}
            for dept in st.session_state.DEPARTMENTS
        }
        for dept, creds in initial_dept_heads.items():
            add_department_head(dept, creds["username"], creds["password"], creds["email"])
        st.session_state.DEPARTMENT_HEADS = initial_dept_heads
    else:
        st.session_state.DEPARTMENT_HEADS = db_dept_heads

if 'ADMIN_CREDENTIALS' not in st.session_state:
    st.session_state.ADMIN_CREDENTIALS = get_admin_credentials()

if 'STORE_CREDENTIALS' not in st.session_state:
    st.session_state.STORE_CREDENTIALS = get_store_credentials()

DEPARTMENT_EMAILS = {dept: "" for dept in st.session_state.DEPARTMENTS}

def format_timestamp(timestamp_str, tz_name=DISPLAY_TIMEZONE):
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

if 'page' not in st.session_state:
    st.session_state.clear()
    st.session_state.page = "login"
    st.session_state.is_user_logged_in = False
    st.session_state.is_admin = False
    st.session_state.is_store = False
    st.session_state.is_dept_head = False
    st.session_state.is_super_admin = False
    st.session_state.user_details = {}
    st.session_state.dept_head_department = None
    st.session_state.show_login_success = False
    st.session_state.request_submitted = False

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@(ceat\.com|gmail\.com)$'
    return re.match(email_regex, email) is not None

def authenticate_dept_head(username, password):
    for dept, creds in st.session_state.DEPARTMENT_HEADS.items():
        if creds["username"] == username and creds["password"] == password:
            return dept
    return None

def display_header(info=None):
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
    st.title("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", key="login_password", type="password")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        login_btn = st.button("Login", key="login_submit_btn")
    with col2:
        go_to_register_btn = st.button("Go to Register", key="go_to_register_btn")
    with col3:
        pass

    if login_btn:
        if not email or not password:
            st.error("All fields are required.")
        else:
            if email == SUPER_ADMIN_EMAIL and password == SUPER_ADMIN_PASSWORD:
                st.session_state.is_super_admin = True
                st.session_state.user_details = {"email": email, "emp_id": "SUPER_ADMIN"}
                st.session_state.page = "super_admin_dashboard"
                st.rerun()
            elif email == st.session_state.ADMIN_CREDENTIALS["username"] and password == st.session_state.ADMIN_CREDENTIALS["password"]:
                st.session_state.is_admin = True
                st.session_state.user_details = {"username": email}
                st.session_state.page = "admin_dashboard"
                st.rerun()
            elif email == st.session_state.STORE_CREDENTIALS["username"] and password == st.session_state.STORE_CREDENTIALS["password"]:
                st.session_state.is_store = True
                st.session_state.user_details = {"username": email}
                st.session_state.page = "store_dashboard"
                st.rerun()
            elif dept := authenticate_dept_head(email, password):
                st.session_state.is_dept_head = True
                st.session_state.dept_head_department = dept
                st.session_state.user_details = {"username": email, "department": dept}
                st.session_state.page = "dept_head_dashboard"
                st.rerun()
            else:
                user = login_user(email, password)
                if user:
                    st.session_state.is_user_logged_in = True
                    st.session_state.user_details = {
                        "email": user["email"],
                        "emp_id": user["emp_id"]
                    }
                    st.session_state.page = "user_dashboard"
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    if go_to_register_btn:
        st.session_state.page = "register"
        st.rerun()

def register():
    st.title("Register")
    email = st.text_input("Email", key="register_email")
    emp_id = st.text_input("Official Employee ID", key="register_emp_id")

    password = st.text_input("Password", key="register_password", type="password")
    confirm_password = st.text_input("Confirm Password", key="confirm_password", type="password")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        register_btn = st.button("Register", key="register_submit_btn")
    with col2:
        go_to_login_btn = st.button("Go to Login", key="go_to_login_btn")
    with col3:
        pass

    if register_btn:
        if not email or not emp_id or not password or not confirm_password:
            st.error("All fields are required.")
        elif password != confirm_password:
            st.error("Password and confirmation do not match.")
        elif not validate_email(email):
            st.error("Invalid email format.")
        else:
            success = register_user(email, emp_id, password)
            if success:
                st.success("Registration successful! Please log in with your email and password.")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Email or Employee ID already registered.")

    if go_to_login_btn:
        st.session_state.page = "login"
        st.rerun()

def user_request_form():
    if st.session_state.get("show_login_success", False):
        st.success("Login successful!")
        st.session_state.show_login_success = False

    st.title("Request Form")
    user_name = st.text_input("Enter your Name", key="request_name")
    user_email = st.session_state.user_details.get("email", "")
    st.text_input("Email", value=user_email, disabled=True, key="request_email")

    st.selectbox(
        "Select Department",
        options=sorted(st.session_state.DEPARTMENTS),
        key="selected_department"
    )
    if "selected_department" in st.session_state:
        st.session_state.user_details["department"] = st.session_state.selected_department

    if "selected_items" not in st.session_state:
        st.session_state.selected_items = {}

    items = get_all_items() or []
    item_map = {item["id"]: {"particular": item["particular"], "quantity": item["quantity"]} for item in items}

    with st.expander("Add Items", expanded=True):
        available_item_ids = [None] + [item["id"] for item in items if item["id"] not in st.session_state.selected_items and item["quantity"] > 0]
        selected_item_id = st.selectbox(
            "Select item to add",
            options=available_item_ids,
            format_func=lambda id: "Select an item" if id is None else item_map[id]["particular"],
            key="add_item_select"
        )
        if selected_item_id is not None:
            max_qty = item_map[selected_item_id]["quantity"]
            qty = st.number_input(
                "Quantity",
                min_value=1,
                max_value=max_qty,
                value=1,
                key=f"add_qty_{selected_item_id}"
            )
            if st.button("Add", key="add_item_submit_btn"):
                if qty > 0 and qty <= max_qty:
                    st.session_state.selected_items[selected_item_id] = qty
                    st.rerun()
                else:
                    st.error(f"Invalid quantity. Maximum available: {max_qty}")
        else:
            st.write("Please select an item to add.")

    if st.session_state.selected_items:
        st.subheader("Selected Items")
        for item_id in list(st.session_state.selected_items.keys()):
            item_name = item_map[item_id]["particular"]
            qty = st.session_state.selected_items[item_id]
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{item_name} (Qty: {qty})")
            with col2:
                if st.button("Remove", key=f"remove_item_{item_id}"):
                    del st.session_state.selected_items[item_id]
                    st.rerun()
    else:
        st.info("No items selected yet.")

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
            show_loading_animation(animation_placeholder, "Processing your request...")
            
            success, message = insert_request(
                user_name,
                user_details["email"],
                user_details["emp_id"],
                user_details["department"],
                selected_items_list,
                formatted_description,
                suggestion if suggestion.strip() else None
            )

            if success:
                requests = get_requests_by_emp_id(user_details["emp_id"])
                latest_request = max(requests, key=lambda x: x["created_at"]) if requests else None
                req_id = latest_request["id"] if latest_request else "Unknown"

                subject = f"Request {req_id} Submitted"
                body = f"Your request has been successfully submitted and is pending department approval.\n\nDetails:\n{formatted_description}"
                try:
                    send_email(
                        to_email=user_details["email"],
                        admin_name="System",
                        subject=subject,
                        body=body,
                        request_details={
                            "id": req_id,
                            "description": formatted_description,
                            "status": "Pending Department Approval",
                            "created_at": format_timestamp(latest_request["created_at"]) if latest_request else "Not available"
                        }
                    )
                    st.success(f"Request submitted successfully! Email sent to {user_details['email']}.")
                except Exception as e:
                    st.warning(f"Request submitted successfully, but email failed: {e}")
                
                st.session_state.selected_items = {}
                st.session_state.request_submitted = True
                st.rerun()
            else:
                st.error(message)
            
            animation_placeholder.empty()

def display_my_orders():
    st.subheader("My Orders")
    emp_id = st.session_state.user_details.get("emp_id", "")
    if not emp_id:
        st.error("Employee ID not found. Please log in again.")
        return
    
    requests = get_requests_by_emp_id(emp_id) or []
    if requests:
        sorted_requests = sorted(requests, key=lambda x: x.get("created_at", ""), reverse=True)
        for req in sorted_requests:
            req_id = req["id"]
            created_at = format_timestamp(req.get("created_at"))
            description = req["description"]
            status = req["status"]
            updated_at = format_timestamp(req.get("updated_at", req.get("created_at")))
            
            st.write(f"**Request ID:** {req_id}")
            st.write(f"**Date Submitted:** {created_at}")
            st.write(f"**Description:** {description}")
            if status == "Admin Approved":
                st.markdown(f"**Status:** <span style='color:green'>{status}</span>", unsafe_allow_html=True)
            elif status in ["Department Rejected", "Admin Rejected"]:
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
    
    if st.button("Refresh Orders", key="refresh_orders"):
        st.rerun()

def user_dashboard():
    display_header({'email': st.session_state.user_details['email'], 'emp_id': st.session_state.user_details['emp_id']})
    
    tab1, tab2 = st.tabs(["Request Form", "My Orders"])
    with tab1:
        user_request_form()
    with tab2:
        display_my_orders()
    
    st.markdown('<div class="footer">Created by Digital Team</div>', unsafe_allow_html=True)

def dept_head_dashboard():
    display_header({'department': st.session_state.dept_head_department})
    
    st.title(f"{st.session_state.dept_head_department} Department Dashboard")
    requests = get_requests_by_department(st.session_state.dept_head_department) or []
    if requests:
        st.subheader(f"All Requests for {st.session_state.dept_head_department}")
        for req in requests:
            req_id = req["id"]
            emp_id = req["emp_id"]
            name = req["name"]
            email = req["email"]
            description = req["description"]
            status = req["status"]
            created_at = format_timestamp(req.get("created_at"))
            updated_at = format_timestamp(req.get("updated_at", req.get("created_at")))
            with st.expander(f"Request ID: {req_id} - {status}"):
                st.write(f"**Employee ID:** {emp_id}")
                st.write(f"**Name:** {name}")
                st.write(f"**Email:** {email}")
                st.write(f"**Description:** {description}")
                st.write(f"**Status:** {status}")
                st.write(f"**Created At:** {created_at}")
                st.write(f"**Last Updated:** {updated_at}")
                if status == "Pending Department Approval":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Approve", key=f"dept_approve_{req_id}"):
                            success, _ = update_request_status(req_id, "Department Approved")
                            if success:
                                try:
                                    send_email(
                                        to_email=email,
                                        admin_name=f"{st.session_state.dept_head_department} Head",
                                        subject=f"Request {req_id} Approved by Department",
                                        body="Your request has been approved by the department head.",
                                        request_details=req
                                    )
                                    st.success(f"Approved request {req_id} and email sent to {email}")
                                except Exception as e:
                                    st.warning(f"Approved request {req_id}, but email failed: {e}")
                                st.rerun()
                            else:
                                st.error(f"Failed to approve request {req_id}")
                    with col2:
                        if st.button("Reject", key=f"dept_reject_{req_id}"):
                            success, _ = update_request_status(req_id, "Department Rejected")
                            if success:
                                try:
                                    send_email(
                                        to_email=email,
                                        admin_name=f"{st.session_state.dept_head_department} Head",
                                        subject=f"Request {req_id} Rejected by Department",
                                        body="Your request has been rejected by the department head.",
                                        request_details=req
                                    )
                                    st.success(f"Rejected request {req_id} and email sent to {email}")
                                except Exception as e:
                                    st.warning(f"Rejected request {req_id}, but email failed: {e}")
                                st.rerun()
                            else:
                                st.error(f"Failed to reject request {req_id}")
    else:
        st.info(f"No requests found for {st.session_state.dept_head_department}.")
    
    st.markdown('<div class="footer">Created by Digital Team</div>', unsafe_allow_html=True)

def admin_dashboard():
    display_header({'username': st.session_state.ADMIN_CREDENTIALS['username']})
    
    st.title("Admin Dashboard")

    items = get_all_items()
    low_stock_items = [item for item in items if item["quantity"] <= 10]
    if low_stock_items:
        st.subheader("Low Stock Alerts")
        st.write(f"There are {len(low_stock_items)} items with low stock:")
        for item in low_stock_items:
            st.markdown(f"- **{item['particular']}**: {item['quantity']} left", unsafe_allow_html=True)
    else:
        st.info("All items are sufficiently stocked.")

    all_requests = get_all_requests()
    requests = [req for req in all_requests if req["status"] not in ["Pending Department Approval"]]
    if requests:
        st.subheader("All Requests Post-Department Review")
        for req in requests:
            req_id = req["id"]
            emp_id = req["emp_id"]
            name = req["name"]
            department = req["department"]
            email = req["email"]
            description = req["description"]
            suggestion = req["suggestion"] or "None"
            status = req["status"]
            updated_at = format_timestamp(req.get("updated_at", req.get("created_at")))

            with st.expander(f"Request ID: {req_id} - {status}", expanded=False):
                st.write(f"**Employee ID:** {emp_id}")
                st.write(f"**Name:** {name}")
                st.write(f"**Department:** {department}")
                st.write(f"**Email:** {email}")
                st.write(f"**Description:** {description}")
                st.write(f"**Suggestion:** {suggestion}")
                st.write(f"**Current Status:** {status}")
                st.write(f"**Last Updated:** {updated_at}")

                animation_placeholder = st.empty()

                if status == "Department Approved":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Approve ", key=f"admin_approve_{req_id}"):
                            show_loading_animation(animation_placeholder, "Approving request...")
                            success, message = update_request_status(req_id, "Admin Approved")
                            if success:
                                request_items = get_request_items(req_id)
                                items_updated = True
                                for item in request_items:
                                    item_id = item["item_id"]
                                    requested_qty = item["quantity"]
                                    current_items = get_all_items()
                                    current_item = next((i for i in current_items if i["id"] == item_id), None)
                                    if current_item:
                                        new_quantity = max(0, current_item["quantity"] - requested_qty)
                                        if not update_item_quantity(item_id, new_quantity):
                                            items_updated = False
                                            st.error(f"Failed to update quantity for item ID {item_id}")
                                            break
                                    else:
                                        items_updated = False
                                        st.error(f"Item ID {item_id} not found in inventory")
                                        break

                                if items_updated:
                                    subject = "Request Approved by Admin"
                                    body = f"Your request {req_id} has been approved by the admin. Item quantities have been updated."
                                    try:
                                        send_email(email, "Admin", subject, body, request_details=req)
                                        st.success(f"Updated request {req_id} to Admin Approved and reduced item quantities")
                                    except Exception as e:
                                        st.warning(f"Updated request {req_id} to Admin Approved, but email failed: {e}")
                                else:
                                    st.warning(f"Updated request {req_id} to Admin Approved, but item quantities update failed")
                            else:
                                st.error(f"Failed to update request {req_id}: {message}")
                            animation_placeholder.empty()
                            st.rerun()
                    with col2:
                        if st.button(f"Reject ", key=f"admin_reject_{req_id}"):
                            show_loading_animation(animation_placeholder, "Rejecting request...")
                            success, message = update_request_status(req_id, "Admin Rejected")
                            animation_placeholder.empty()
                            if success:
                                subject = "Request Rejected by Admin"
                                body = f"Your request {req_id} has been rejected by the admin."
                                try:
                                    send_email(email, "Admin", subject, body, request_details=req)
                                    st.success(f"Updated request {req_id} to Admin Rejected")
                                except Exception as e:
                                    st.warning(f"Updated request {req_id} to Admin Rejected, but email failed: {e}")
                            else:
                                st.error(f"Failed to update request {req_id}: {message}")
                            st.rerun()

                if st.button(f"Delete Request ", key=f"delete_{req_id}"):
                    show_loading_animation(animation_placeholder, "Deleting request...")
                    try:
                        success = delete_request(req_id)
                        animation_placeholder.empty()
                        if success:
                            st.success(f"Deleted request {req_id}")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete request {req_id}. Check server logs or database for details.")
                    except Exception as e:
                        animation_placeholder.empty()
                        st.error(f"Error deleting request {req_id}: {str(e)}. Please check database connection or constraints.")
    else:
        st.info("No requests have reached Department Approved status yet.")

    with st.expander("Manage Item Availability", expanded=False):
        search_query = st.text_input("Search Items", key="admin_item_search")
        filtered_items = [item for item in items if search_query.lower() in item["particular"].lower()]
        animation_placeholder = st.empty()
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
                    show_loading_animation(animation_placeholder, f"Updating {item['particular']} quantity...")
                    if update_item_quantity(item["id"], new_quantity):
                        animation_placeholder.empty()
                        st.success(f"Updated {item['particular']} quantity to {new_quantity}")
                        st.rerun()
                    else:
                        animation_placeholder.empty()
                        st.error(f"Failed to update {item['particular']} quantity")

    st.subheader("Send Email to User")
    users = get_all_users()
    if users:
        user_options = [f"{emp_id} - {email}" for emp_id, email in users]
        selected_user = st.selectbox(
            "Select User",
            options=range(len(users)),
            format_func=lambda i: user_options[i]
        )
        selected_email = users[selected_user][1]
        email_subject = st.text_input("Email Subject")
        email_body = st.text_area("Email Body")
        animation_placeholder = st.empty()
        if st.button("Send Email"):
            if selected_email and email_subject and email_body:
                show_loading_animation(animation_placeholder, "Sending email...")
                try:
                    send_email(
                        to_email=selected_email,
                        admin_name="Admin",
                        subject=email_subject,
                        body=email_body,
                        request_details=None
                    )
                    animation_placeholder.empty()
                    st.success(f"Email sent to {selected_email}")
                except Exception as e:
                    animation_placeholder.empty()
                    st.error(f"Failed to send email: {e}")
            else:
                st.warning("Please fill in all fields.")
    else:
        st.info("No users found.")

    st.subheader("Send Email to Department")
    department_options = st.session_state.DEPARTMENTS
    selected_department = st.selectbox(
        "Select Department",
        options=department_options,
        key="dept_email_select"
    )
    dept_email_subject = st.text_input("Department Email Subject", key="dept_email_subject")
    dept_email_body = st.text_area("Department Email Body", key="dept_email_body")
    send_to_all_users = st.checkbox(
        "Send to all users who have made requests in this department",
        key="send_to_all_users"
    )
    animation_placeholder = st.empty()
    if st.button("Send Department Email", key="send_dept_email_btn"):
        if not selected_department or not dept_email_subject or not dept_email_body:
            st.warning("Please fill in all fields.")
        else:
            show_loading_animation(animation_placeholder, "Sending department email...")
            if send_to_all_users:
                requests = get_requests_by_department(selected_department)
                if requests:
                    emails = list(set(req["email"] for req in requests))
                    for email in emails:
                        try:
                            send_email(
                                to_email=email,
                                admin_name="Admin",
                                subject=dept_email_subject,
                                body=dept_email_body,
                                request_details=None
                            )
                            st.success(f"Email sent to {email}")
                        except Exception as e:
                            st.error(f"Failed to send email to {email}: {e}")
                    animation_placeholder.empty()
                    st.success(f"Emails sent to {len(emails)} users in {selected_department}")
                else:
                    animation_placeholder.empty()
                    st.info(f"No requests found for {selected_department}")
            else:
                dept_heads = get_all_department_heads()
                dept_email = dept_heads.get(selected_department, {}).get("email", "")
                if dept_email:
                    try:
                        send_email(
                            to_email=dept_email,
                            admin_name="Admin",
                            subject=dept_email_subject,
                            body=dept_email_body,
                            request_details=None
                        )
                        animation_placeholder.empty()
                        st.success(f"Email sent to {dept_email}")
                    except Exception as e:
                        animation_placeholder.empty()
                        st.error(f"Failed to send email to {dept_email}: {e}")
                else:
                    animation_placeholder.empty()
                    st.error(f"No email defined for the head of {selected_department}")
    
    st.markdown('<div class="footer">Created by Digital Team</div>', unsafe_allow_html=True)

def store_dashboard():
    display_header({'username': st.session_state.STORE_CREDENTIALS['username']})
    
    st.title("Store Dashboard")
    valid_statuses = ["Admin Approved", "Packing", "Dispatched", "Delivered"]
    approved_requests = [req for req in (get_all_requests() or []) if req["status"] in valid_statuses]
    if approved_requests:
        st.subheader("Requests Ready for Processing")
        for req in approved_requests:
            req_id = req["id"]
            emp_id = req["emp_id"]
            name = req["name"]
            department = req["department"]
            email = req["email"]
            description = req["description"]
            status = req["status"]
            updated_at = format_timestamp(req.get("updated_at", req.get("created_at")))

            with st.expander(f"Request ID: {req_id} - {status}"):
                st.write(f"**Employee ID:** {emp_id}")
                st.write(f"**Name:** {name}")
                st.write(f"**Department:** {department}")
                st.write(f"**Email:** {email}")
                st.write(f"**Description:** {description}")
                st.write(f"**Current Status:** {status}")
                st.write(f"**Last Updated:** {updated_at}")

                animation_placeholder = st.empty()

                if status == "Admin Approved":
                    if st.button("Start Packing", key=f"start_packing_{req_id}"):
                        show_loading_animation(animation_placeholder, "Starting packing...")
                        success, _ = update_request_status(req_id, "Packing")
                        animation_placeholder.empty()
                        if success:
                            st.success(f"Started packing for request {req_id}")
                            st.rerun()
                        else:
                            st.error(f"Failed to start packing for request {req_id}")
                elif status == "Packing":
                    if st.button("Mark as Dispatched", key=f"dispatch_{req_id}"):
                        show_loading_animation(animation_placeholder, "Marking as dispatched...")
                        success, _ = update_request_status(req_id, "Dispatched")
                        animation_placeholder.empty()
                        if success:
                            st.success(f"Marked as dispatched for request {req_id}")
                            st.rerun()
                        else:
                            st.error(f"Failed to dispatch request {req_id}")
                elif status == "Dispatched":
                    delivered_to = st.text_input(f"Enter receiver name for Request {req_id}", key=f"delivered_to_{req_id}")
                    if st.button("Mark as Delivered", key=f"deliver_{req_id}"):
                        if delivered_to.strip():
                            show_loading_animation(animation_placeholder, "Marking as delivered...")
                            success, _ = update_request_status(req_id, "Delivered", delivered_to=delivered_to.strip())
                            animation_placeholder.empty()
                            if success:
                                try:
                                    current_time = datetime.datetime.now(pytz.timezone(DISPLAY_TIMEZONE)).strftime("%B %d, %Y %H:%M:%S")
                                    send_email(
                                        to_email=email,
                                        admin_name="Store Manager",
                                        subject=f"Request {req_id} Delivered",
                                        body=f"Your request has been delivered to {delivered_to}.",
                                        request_details=req,
                                        delivered_to=delivered_to,
                                        delivery_time=current_time
                                    )
                                    st.success(f"Marked as delivered for request {req_id} to {delivered_to} and email sent")
                                except Exception as e:
                                    st.warning(f"Marked as delivered for request {req_id}, but email failed: {e}")
                                st.rerun()
                            else:
                                st.error(f"Failed to deliver request {req_id}")
                        else:
                            st.warning("Enter the receiver's name")
                elif status == "Delivered":
                    delivered_to = req.get("delivered_to", "N/A")
                    st.write(f"**Delivered to:** {delivered_to}")
    else:
        st.info("No requests ready for processing.")
    
    st.markdown('<div class="footer">Created by Digital Team</div>', unsafe_allow_html=True)

def super_admin_dashboard():
    display_header({'email': st.session_state.user_details['email']})
    
    st.title("Super Admin Dashboard")
    st.write(f"Welcome, Super Admin ({st.session_state.user_details['email']})!")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Manage Users",
        "Manage Department Heads",
        "Manage Admin",
        "Manage Store",
        "Manage Inventory",
        "Manage Departments",
        "Manage Department Head Emails"
    ])

    with tab1:
        st.subheader("Manage Users")
        users = get_all_users() or []
        if users:
            for emp_id, email in users:
                with st.expander(f"User: {email} (Emp ID: {emp_id})"):
                    new_password = st.text_input(
                        "New Password",
                        type="password",
                        key=f"pw_{emp_id}",
                        placeholder="Enter new password"
                    )
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Update Password", key=f"update_password_{emp_id}"):
                            if new_password:
                                if update_user_password(emp_id, new_password):
                                    st.success(f"Password updated for {email}")
                                else:
                                    st.error("Failed to update password")
                            else:
                                st.warning("Enter a new password")
                    with col2:
                        if st.button("Delete User", key=f"delete_user_{emp_id}"):
                            if delete_user(emp_id):
                                st.success(f"Deleted user {email}")
                                st.rerun()
                            else:
                                st.error("Failed to delete user")
        else:
            st.info("No users found.")

    with tab2:
        st.subheader("Manage Department Heads")
        st.session_state.DEPARTMENT_HEADS = get_all_department_heads()
        for dept in sorted(st.session_state.DEPARTMENT_HEADS.keys()):
            with st.expander(f"Department: {dept}"):
                st.write(f"Username: {st.session_state.DEPARTMENT_HEADS[dept]['username']}")
                new_dept_password = st.text_input(f"New Password for {dept}", type="password", key=f"dept_pw_{dept}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update Password", key=f"update_dept_pw_{dept}"):
                        if new_dept_password:
                            if update_department_head_password(dept, new_dept_password):
                                st.session_state.DEPARTMENT_HEADS[dept]["password"] = new_dept_password
                                st.success(f"Password updated for {dept}")
                            else:
                                st.error(f"Failed to update password for {dept}")
                        else:
                            st.warning("Enter a new password")
                with col2:
                    if st.button("Delete Department", key=f"delete_dept_{dept}"):
                        if delete_department_head(dept):
                            del st.session_state.DEPARTMENT_HEADS[dept]
                            st.session_state.DEPARTMENTS.remove(dept)
                            st.success(f"Deleted department {dept}")
                            st.rerun()
                        else:
                            st.error(f"Failed to delete department {dept}")

    with tab3:
        st.subheader("Manage Admin")
        st.session_state.ADMIN_CREDENTIALS = get_admin_credentials()
        st.write(f"Current Username: {st.session_state.ADMIN_CREDENTIALS['username']}")
        new_admin_password = st.text_input("New Password for Admin", type="password", key="admin_new_pw")
        if st.button("Update Admin Password", key="update_admin_pw_btn"):
            if new_admin_password:
                if update_admin_password(new_admin_password):
                    st.session_state.ADMIN_CREDENTIALS["password"] = new_admin_password
                    st.success("Admin password updated successfully")
                else:
                    st.error("Failed to update admin password")
            else:
                st.warning("Enter a new password")

    with tab4:
        st.subheader("Manage Store")
        st.session_state.STORE_CREDENTIALS = get_store_credentials()
        st.write(f"Current Username: {st.session_state.STORE_CREDENTIALS['username']}")
        new_store_password = st.text_input("New Password for Store", type="password", key="store_new_pw")
        if st.button("Update Store Password", key="update_store_pw_btn"):
            if new_store_password:
                if update_store_password(new_store_password):
                    st.session_state.STORE_CREDENTIALS["password"] = new_store_password
                    st.success("Store password updated successfully")
                else:
                    st.error("Failed to update store password")
            else:
                st.warning("Enter a new password")

    with tab5:
        st.subheader("Manage Inventory")
        items = get_all_items() or []
        if items:
            for item in items:
                with st.expander(f"{item['particular']} (Qty: {item['quantity']})"):
                    qty = st.number_input("Set Quantity", min_value=0, value=item["quantity"], key=f"qty_{item['id']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Update", key=f"update_qty_{item['id']}"):
                            if update_item_quantity(item["id"], qty):
                                st.success("Quantity updated")
                                st.rerun()
                            else:
                                st.error("Failed to update quantity")
                    with col2:
                        if st.button("Remove", key=f"remove_item_{item['id']}"):
                            if remove_item(item["id"]):
                                st.success("Item removed")
                                st.rerun()
                            else:
                                st.error("Failed to remove item")
        else:
            st.info("No items in inventory.")

        st.subheader("Add New Item")
        new_item_name = st.text_input("Item Name", key="new_item_name")
        new_item_qty = st.number_input("Initial Quantity", min_value=0, value=0, key="new_item_qty")
        if st.button("Add Item", key="add_item_btn"):
            if new_item_name:
                animation_placeholder = st.empty()
                show_loading_animation(animation_placeholder, "Adding item...")
                if add_item(new_item_name, new_item_qty):
                    animation_placeholder.empty()
                    st.success(f"Item '{new_item_name}' added successfully")
                    st.session_state.pop("new_item_name", None)
                    st.session_state.pop("new_item_qty", None)
                    st.rerun()
                else:
                    animation_placeholder.empty()
                    st.error("Item already exists or failed to add")
            else:
                st.error("Enter an item name")

    with tab6:
        st.subheader("Manage Departments")
        st.write("Current Departments:")
        for dept in sorted(st.session_state.DEPARTMENTS):
            st.write(f"- {dept}")

        st.subheader("Add New Department")
        new_dept_name = st.text_input("Department Name", key="new_dept_name")
        new_dept_username = st.text_input("Username for Department Head", key="new_dept_username")
        new_dept_password = st.text_input("Password for Department Head", type="password", key="new_dept_password")
        new_dept_email = st.text_input("Department Head Email (optional)", key="new_dept_email")
        if st.button("Add Department", key="add_dept_btn"):
            if new_dept_name and new_dept_username and new_dept_password:
                if new_dept_name not in st.session_state.DEPARTMENTS:
                    animation_placeholder = st.empty()
                    show_loading_animation(animation_placeholder, "Adding department...")
                    if add_department_head(new_dept_name, new_dept_username, new_dept_password, new_dept_email):
                        st.session_state.DEPARTMENTS.append(new_dept_name)
                        st.session_state.DEPARTMENT_HEADS[new_dept_name] = {
                            "username": new_dept_username,
                            "password": new_dept_password,
                            "email": new_dept_email
                        }
                        animation_placeholder.empty()
                        st.success(f"Department '{new_dept_name}' added successfully")
                        st.session_state.pop("new_dept_name", None)
                        st.session_state.pop("new_dept_username", None)
                        st.session_state.pop("new_dept_password", None)
                        st.session_state.pop("new_dept_email", None)
                        st.rerun()
                    else:
                        animation_placeholder.empty()
                        st.error("Failed to add department (possibly duplicate in database)")
                else:
                    st.error("Department already exists")
            else:
                st.error("All fields except email are required")

    with tab7:
        st.subheader("Manage Department Head Emails")
        st.session_state.DEPARTMENT_HEADS = get_all_department_heads()
        for dept in sorted(st.session_state.DEPARTMENTS):
            current_email = st.session_state.DEPARTMENT_HEADS.get(dept, {}).get("email", "")
            with st.expander(f"Department: {dept}"):
                st.write(f"Current Email: {current_email if current_email else 'No email set'}")
                new_email = st.text_input(
                    "New Department Head Email",
                    value=current_email,
                    key=f"head_email_{dept}"
                )
                if st.button("Update Head Email", key=f"update_head_email_{dept}"):
                    if new_email == "" or validate_email(new_email):
                        if update_department_head_email(dept, new_email):
                            st.session_state.DEPARTMENT_HEADS[dept]["email"] = new_email
                            st.success(f"Department head email updated for {dept}")
                        else:
                            st.error("Failed to update department head email")
                    else:
                        st.error("Invalid email format")
    
    st.markdown('<div class="footer">Created by Digital Team</div>', unsafe_allow_html=True)

def main():
    load_css("styles.css")
    st.markdown(
        """
        <img src="https://www.itvoice.in/wp-content/uploads/2023/01/CEAT-Tyre-logo-2000x1000-1.png" class="logo">
        """,
        unsafe_allow_html=True
    )

    if st.session_state.page == "login":
        login()
    elif st.session_state.page == "register":
        register()
    elif st.session_state.page == "super_admin_dashboard":
        super_admin_dashboard()
    elif st.session_state.page == "user_dashboard":
        user_dashboard()
    elif st.session_state.page == "dept_head_dashboard":
        dept_head_dashboard()
    elif st.session_state.page == "admin_dashboard":
        admin_dashboard()
    elif st.session_state.page == "store_dashboard":
        store_dashboard()

if __name__ == "__main__":
    main()
  