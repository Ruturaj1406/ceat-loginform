import streamlit as st
import re
import datetime
from database import (
    get_all_requests,
    update_request_status,
    insert_request,
    delete_request,
    get_all_items,
    update_item_availability,
)
from mail import send_email

bg_image_url = "https://vibesdesign.com/wp-content/uploads/2016/02/ceat-tyres.jpg"
background_style = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(rgba(223, 244, 250, 0.8), rgba(223, 244, 250, 0.8)), url("{bg_image_url}") no-repeat center center fixed;
    background-size: cover;
}}
[data-testid="stSidebar"] {{
   background-color: rgba(211, 211, 211, 0.8);  
}}


@media screen and (max-width: 768px) {{
    /* Adjust form elements */
    .stTextInput input, .stSelectbox select {{
        font-size: 16px !important;  
    }}

    
    div[data-testid="column"] {{
        width: 100% !important;
        padding: 0.2rem !important;
    }}

   
    div[data-testid="stVerticalBlock"] > div {{
        padding: 0.5rem 0;
    }}

    
    div[data-testid="stHorizontalBlock"] {{
        flex-direction: column !important;
    }}

    
    .stButton button {{
        width: 100% !important;
        margin: 5px 0;
    }}

   
    .stApp > header {{
        display: none;
    }}
}}


<meta name="viewport" content="width=device-width, initial-scale=1.0">


.stTextInput, .stSelectbox, .stNumberInput {{
    margin: 8px 0;
}}

.stCheckbox label {{
    font-size: 14px !important;
}}


div[data-testid="stExpander"] {{
    margin: 10px 0;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}}
</style>
"""
st.markdown(background_style, unsafe_allow_html=True)


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
DEPARTMENTS = ["Digital", "IT", "HR", "Finance", "Operations"]


if 'is_user_logged_in' not in st.session_state:
    st.session_state.is_user_logged_in = False
    st.session_state.user_details = {}
    st.session_state.show_login_success = False

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
    st.session_state.login_time = None


def validate_email(email):

    email_regex = r'^[a-zA-Z0-9_.+-]+@(gmail\.com|ceat\.com)$'
    return re.match(email_regex, email) is not None


def user_login():

    st.title("User Login")
    emp_id = st.text_input("Employee ID", key="user_emp_id")
    email = st.text_input("Email", key="user_email")
    department = st.selectbox("Department", [""] + DEPARTMENTS, key="user_department")

    if st.button("Login", key="user_login_btn"):
        if not validate_email(email):
            st.error("Please enter a valid email id")
        elif emp_id.strip() and email.strip() and department.strip():
            st.session_state.is_user_logged_in = True
            st.session_state.user_details = {
                "emp_id": emp_id,
                "email": email,
                "department": department
            }
            st.session_state.show_login_success = True
            st.rerun()
        else:
            st.error("Please fill out all fields to log in.")


def user_request_form():

    if st.session_state.show_login_success:
        st.success("Login successful!")
        st.session_state.show_login_success = False

    st.title("Request Form")
    user_name = st.text_input("Enter your Name", key="request_name")
    user_email = st.session_state.user_details.get("email", "")

    if "selected_items" not in st.session_state:
        st.session_state.selected_items = {}


    items = get_all_items()


    search_query = st.text_input("Search Items", key="item_search")
    filtered_items = [item for item in items if search_query.lower() in item["particular"].lower()]

    st.subheader("Add Items")
    for idx, item in enumerate(filtered_items):
        item_name = item["particular"]
        item_available = item["available"]
        item_key = f"item_{item_name}_{idx}"

        if item_name not in st.session_state.selected_items:
            st.session_state.selected_items[item_name] = {"selected": False, "quantity": 1}


        col1, col2 = st.columns([3, 1])

        with col1:
            if item_available:

                if st.checkbox(
                        item_name,
                        value=st.session_state.selected_items[item_name]["selected"],
                        key=f"chk_{item_key}"
                ):
                    st.session_state.selected_items[item_name]["selected"] = True
                else:
                    st.session_state.selected_items[item_name]["selected"] = False
                    st.session_state.selected_items[item_name]["quantity"] = 1
            else:

                st.markdown(f"~~{item_name}~~ *(Currently Unavailable)*")

        if item_available and st.session_state.selected_items[item_name]["selected"]:
            with col2:
                quantity = st.number_input(
                    f"Qty for {item_name}",
                    min_value=1,
                    value=st.session_state.selected_items[item_name]["quantity"],
                    key=f"qty_{item_key}",
                )
                st.session_state.selected_items[item_name]["quantity"] = quantity
        else:
            with col2:
                st.empty()


    available_items = [item["particular"] for item in items if item["available"]]
    selected_items = {
        item: details
        for item, details in st.session_state.selected_items.items()
        if details["selected"] and item in available_items
    }

    if selected_items:
        st.subheader("Selected Items")
        for item_name, details in selected_items.items():
            st.write(f"Item: {item_name}, Quantity: {details['quantity']}")


    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Submit Request", key="submit_request_btn"):
            if not user_name.strip():
                st.error("Please enter your name.")
            elif not selected_items:
                st.error("Please select at least one item.")
            else:
                formatted_description = ", ".join(
                    [f"{item_name} (Qty: {details['quantity']})" for item_name, details in selected_items.items()]
                )

                insert_request(user_name, user_email, formatted_description)

                request_details = {
                    "name": user_name,
                    "email": user_email,
                    "description": formatted_description,
                }
                subject = "Request Submission"
                body = f"Request details:\nName: {user_name}\nItems: {formatted_description}"
                send_email(user_email, "System", request_details, subject, body)

                st.success("Request submitted successfully!")
                st.session_state.selected_items = {}

    with col2:
        if st.button("Back to Login", key="user_back_btn"):
            st.session_state.is_user_logged_in = False
            st.session_state.show_login_success = False
            st.rerun()


def admin_login():

    with st.sidebar:
        st.title("Admin Login")
        username = st.text_input("Username", key="admin_username_input")
        password = st.text_input("Password", type="password", key="admin_password_input")
        admin_email = st.text_input("Admin Email", key="admin_email_input")

        if st.button("Login", key="admin_login_btn"):
            if not validate_email(admin_email):
                st.error("Invalid email format")
            elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.session_state.login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.rerun()
            else:
                st.error("Invalid credentials")


def admin_dashboard():

    with st.sidebar:
        st.title("Admin Panel")
        st.subheader("Login Information")
        st.write(f"Username: {ADMIN_USERNAME}")

        if st.button("Logout", key="admin_logout_btn"):
            st.session_state.is_admin = False
            st.session_state.login_time = None
            st.rerun()

    st.title("Admin Dashboard")
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


            with st.expander(f"Request ID: {req_id}", expanded=False):

                st.write(f"**Employee**: {emp_id} - {name} ({department})")
                st.write(f"**Email**: {email}")
                st.write(f"**Description**:\n{description}")
                st.write(f"**Status**: {status}")


                status_update = st.radio(
                    f"Status for {req_id}",
                    ["Pending", "Approved", "Rejected"],
                    index=["Pending", "Approved", "Rejected"].index(status),
                    key=f"status_radio_{req_id}",
                )


                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Update {req_id}", key=f"update_btn_{req_id}"):
                        update_request_status(req_id, status_update)
                        subject = f"Request {status_update}"
                        body = f"Your request {req_id} has been {status_update.lower()}\n\nDetails:\n{description}"
                        send_email(email, "Admin", req, subject, body)
                        st.success(f"Updated request {req_id}")
                with col2:
                    if st.button(f"Delete {req_id}", key=f"delete_btn_{req_id}"):
                        delete_request(req_id)
                        st.success(f"Deleted request {req_id}")

    else:
        st.info("No requests available")


    st.subheader("Manage Item Availability")
    items = get_all_items()
    for item in items:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(item["particular"])
        with col2:
            current_availability = item["available"]
            new_availability = st.checkbox(
                f"Available {item['particular']}",
                value=current_availability,
                key=f"available_{item['particular']}"
            )
            if new_availability != current_availability:
                update_item_availability(item["particular"], new_availability)
                st.rerun()


    st.subheader("Send Message to Users")
    user_emails = list(set(req["email"] for req in requests if req.get("email")))
    selected_email = st.selectbox("Select Email", [""] + user_emails, key="msg_email_select")
    message_content = st.text_area("Message Content", height=150, key="msg_content")

    if st.button("Send Message", key="send_msg_btn"):
        if selected_email and message_content.strip():
            subject = "Message from Admin"
            body = f"{message_content}"
            request_details = {"name": "User", "email": selected_email, "description": "Admin Message"}
            send_email(selected_email, "Admin", request_details, subject, body)
            st.success(f"Message sent to {selected_email}")
        else:
            st.error("Please select an email and enter a message")


def main():

    if st.session_state.is_user_logged_in:
        user_request_form()
    elif st.session_state.is_admin:
        admin_dashboard()
    else:
        admin_login()
        user_login()


if __name__ == "__main__":
    main()
