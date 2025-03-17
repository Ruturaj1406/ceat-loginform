# Inventory Management System - Functional Document

## Overview
The Inventory Management System is a Streamlit-based web application developed for CEAT to streamline the process of requesting, approving, and fulfilling inventory items. It leverages a SQLite database for data persistence, Gmail SMTP for email notifications, and a custom-styled UI to enhance user experience. The system supports multiple user roles with distinct responsibilities, ensuring a structured workflow from request submission to delivery.

**Document Purpose**: This functional document details the system's capabilities, user roles, workflows, and technical requirements to guide development, usage, and maintenance.

**Date**: March 12, 2025

---

## Functional Requirements

### General Requirements
1. **User Authentication**: Secure login and registration for all users with role-based access control.
2. **Request Management**: Ability to submit, track, approve, reject, and process inventory requests.
3. **Inventory Tracking**: Maintain real-time item quantities with low-stock alerts.
4. **Email Notifications**: Automated HTML emails for request status updates.
5. **Customizable UI**: Responsive design with custom CSS for branding and usability.
6. **Data Persistence**: SQLite database to store users, requests, items, and statuses.

### User-Specific Requirements
#### 1. User
- Submit requests with item selections, descriptions, and suggestions.
- View personal request history with statuses and timestamps.
- Receive email notifications for request updates.

#### 2. Department Head
- View and approve/reject requests specific to their department.
- Receive email notifications for new requests (optional, configurable).
- Access limited to department-specific data.

#### 3. Admin
- Approve/reject requests post-department approval.
- Manage inventory (add, remove, update items and quantities).
- Send custom emails to users or departments.
- View all requests across departments.

#### 4. Store
- Process approved requests through stages: Packing, Dispatched, Delivered.
- Update request statuses and record delivery details (e.g., recipient name).
- Send delivery confirmation emails.

#### 5. Super Admin
- Manage all users (add, update, delete credentials).
- Configure department heads, admin, and store accounts.
- Add/remove departments and manage department emails.
- Full access to inventory and request data.

---

## System Architecture

### Components
- **Frontend**: Streamlit with custom CSS (`src/static/styles.css`).
- **Backend**: Python scripts (`src/app.py`, `src/database.py`, `src/mail.py`).
- **Database**: SQLite (`data/inventory.db`).
- **Email Service**: Gmail SMTP via `src/mail.py`.

### Data Flow
1. **Request Submission**: User → Database → Email Notification.
2. **Department Approval**: Department Head → Database → Email Notification.
3. **Admin Approval**: Admin → Database (update inventory) → Email Notification.
4. **Store Processing**: Store → Database (status updates) → Email Notification.
5. **Super Admin Management**: Super Admin → Database (CRUD operations).

See `docs/architecture.md` for detailed flowcharts and sequence diagrams.

---

## User Roles and Responsibilities

### 1. User
- **Description**: Employees needing inventory items.
- **Actions**:
  - Register with email (`@ceat.com` or `@gmail.com`), employee ID, and password.
  - Log in to access the dashboard.
  - Submit requests via a form (item selection, description, suggestion).
  - View "My Orders" with status and timestamps.

### 2. Department Head
- **Description**: Managers overseeing department-specific requests.
- **Actions**:
  - Log in with predefined credentials (e.g., username: department name, password: `<department>123`).
  - Approve or reject requests for their department.
  - View request details (name, email, items, description).

### 3. Admin
- **Description**: Inventory and request overseers.
- **Actions**:
  - Log in with default credentials (`admin` / `admin123`).
  - Approve/reject requests post-department approval.
  - Manage item availability (add, update, remove items).
  - Send emails to users or departments.

### 4. Store
- **Description**: Personnel handling physical inventory fulfillment.
- **Actions**:
  - Log in with default credentials (`store` / `store123`).
  - Process approved requests (Packing → Dispatched → Delivered).
  - Update delivery details (e.g., recipient name).

### 5. Super Admin
- **Description**: System administrator with full control.
- **Actions**:
  - Log in with hardcoded credentials (`123@ceat.com` / `12`).
  - Manage users, department heads, admin, and store accounts.
  - Add/remove departments and update department emails.
  - Oversee all requests and inventory.

---

## Workflows

### Request Lifecycle
1. **Submission**:
   - User submits a request via the "Request Form" tab.
   - Data saved to `requests` and `request_items` tables.
   - Email sent: "Request Submitted".

2. **Department Approval**:
   - Department Head reviews requests in their dashboard.
   - Approves ("Department Approved") or rejects ("Department Rejected").
   - Status updated in database; email sent to user.

3. **Admin Approval**:
   - Admin reviews "Department Approved" requests.
   - Approves ("Admin Approved", reduces item quantities) or rejects ("Admin Rejected").
   - Status updated; email sent to user.

4. **Store Processing**:
   - Store views "Admin Approved" requests.
   - Updates status: "Packing" → "Dispatched" → "Delivered" (with recipient name).
   - Final email sent: "Request Delivered".

5. **Tracking**:
   - User checks status in "My Orders" tab.

### Inventory Management
- **Add Item**: Super Admin/Admin adds new items (particular, quantity).
- **Update Quantity**: Admin adjusts quantities; low-stock alert at <10 units.
- **Remove Item**: Super Admin/Admin deletes items.

---

## Key Features

### 1. Request Form
- Multi-select dropdown for items from inventory.
- Text inputs for description and suggestion.
- Validation: Name required, items must be selected.

### 2. Order History
- Table displaying request ID, items, status, and timestamp.
- Filterable by employee ID for users.

### 3. Approval Process
- Expandable request details with Approve/Reject buttons.
- Status transitions logged with timestamps.

### 4. Email Notifications
- HTML emails with tables for request details and items.
- Templates for submission, approval, rejection, and delivery.

### 5. Inventory Dashboard
- Table of items with quantities and low-stock warnings.
- CRUD operations for item management.

---

## Technical Specifications

### Database Schema
- **users**: `(emp_id, email, password)`
- **department_heads**: `(department, username, password, email)`
- **admin**: `(username, password)`
- **store**: `(username, password)`
- **items**: `(id, particular, quantity)`
- **requests**: `(id, name, email, emp_id, department, description, suggestion, status, timestamp)`
- **request_items**: `(request_id, item_id, quantity)`

### Email Configuration
- SMTP Server: `smtp.gmail.com:587`
- Credentials: Stored in `.env` (GMAIL_USER, GMAIL_PASSWORD).
- HTML templates dynamically generated in `mail.py`.

### UI Styling
- Custom CSS in `src/static/styles.css` for buttons, tabs, and layout.
- Responsive design with CEAT branding.

---

## Assumptions and Constraints
- **Assumptions**:
  - Gmail SMTP is reliable for email notifications.
  - SQLite suffices for current scale (single-server deployment).
  - Users have valid CEAT or Gmail email addresses.
- **Constraints**:
  - No password hashing (security risk in production).
  - Limited concurrency with SQLite.
  - Gmail SMTP has sending limits (e.g., 100-500 emails/day).

---

## Future Enhancements
1. **Security**: Implement password hashing (e.g., bcrypt).
2. **Database**: Migrate to PostgreSQL for scalability.
3. **Email**: Use a dedicated service (e.g., SendGrid) for higher volume.
4. **Reports**: Add analytics dashboard for request trends.
5. **Mobile Support**: Optimize UI for mobile devices.

---

**Prepared by**: Digital Team at CEAT  
**Version**: 1.0  
**Last Updated**: March 12, 2025