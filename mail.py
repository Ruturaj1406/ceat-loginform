import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError

def send_email(to_email, admin_name, subject, body, request_details=None, delivered_to=None, delivery_time=None):
    """
    Send an email using Gmail SMTP with dynamic content based on the subject.
    
    Args:
        to_email (str): Recipient's email address.
        admin_name (str): Name of the sender (e.g., "Admin").
        subject (str): Email subject line.
        body (str): Email body text.
        request_details (dict, optional): Details of the request (name, email, description).
        delivered_to (str, optional): Delivery recipient name (for "Delivered" emails).
        delivery_time (str, optional): Delivery time (for "Delivered" emails).
    
    Returns:
        bool: True if email is sent successfully.
    
    Raises:
        Exception: If email validation or sending fails.
    """
    # Gmail credentials
    from_email = 'Halol.Admin@ceat.com'  
    password ='khmpqsrfxgspjswk'  

    # Validate recipient email
    try:
        validate_email(to_email)
    except EmailNotValidError as e:
        raise Exception(f"Invalid email address: {e}")

    # Generate HTML content based on request details and subject
    if request_details:
        name = request_details.get('name', 'User')
        email = request_details.get('email', 'N/A')
        description = request_details.get('description', 'N/A')

        # Parse items from description
        items = []
        if description and description != 'N/A':
            item_entries = description.split(", ")
            for entry in item_entries:
                try:
                    item_name, qty_part = entry.split(" (Qty: ")
                    quantity = qty_part.rstrip(")")
                    items.append({"name": item_name, "quantity": quantity})
                except ValueError:
                    items.append({"name": entry, "quantity": "N/A"})

        # Create items table
        items_table = """
        <table border="1" cellpadding="5" style="border-collapse: collapse; width: 50%;">
            <tr>
                <th>Item</th>
                <th>Quantity</th>
            </tr>
        """
        for item in items:
            items_table += f"""
            <tr>
                <td>{item['name']}</td>
                <td>{item['quantity']}</td>
            </tr>
            """
        items_table += "</table>"

        # Email templates based on subject
        if "approved" in subject.lower():
            html_content = f"""
            <html>
                <body>
                    <h3>Hello {name},</h3>
                    <p>We are pleased to inform you that your request has been approved.</p>
                    <p>Details of the approved request:</p>
                    <table border="1" cellpadding="5">
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                        </tr>
                        <tr>
                            <td>{name}</td>
                            <td>{email}</td>
                        </tr>
                    </table>
                    <h4>Items Approved:</h4>
                    {items_table}
                    <p><strong>Approved by:</strong> {admin_name}</p>
                    <p>We will notify you once the items are ready for pickup.</p>
                </body>
            </html>
            """
        elif "rejected" in subject.lower():
            html_content = f"""
            <html>
                <body>
                    <h3>Hello {name},</h3>
                    <p>We regret to inform you that your request has been rejected.</p>
                    <p>Details of the rejected request:</p>
                    <table border="1" cellpadding="5">
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                        </tr>
                        <tr>
                            <td>{name}</td>
                            <td>{email}</td>
                        </tr>
                    </table>
                    <h4>Items Requested:</h4>
                    {items_table}
                    <p><strong>Rejected by:</strong> {admin_name}</p>
                    <p>Contact support for clarification if needed.</p>
                </body>
            </html>
            """
        elif "delivered" in subject.lower() and delivered_to and delivery_time:
            html_content = f"""
            <html>
                <body>
                    <h3>Hello {name},</h3>
                    <p>Your request has been delivered to <strong>{delivered_to}</strong> on <strong>{delivery_time}</strong>.</p>
                    <p>Details of the delivered request:</p>
                    <table border="1" cellpadding="5">
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                        </tr>
                        <tr>
                            <td>{name}</td>
                            <td>{email}</td>
                        </tr>
                    </table>
                    <h4>Items Delivered:</h4>
                    {items_table}
                    <p><strong>Processed by:</strong> {admin_name}</p>
                    <p>Contact us at 9999999999 if you can't receive the item.</p>
                </body>
            </html>
            """
        else:
            html_content = f"""
            <html>
                <body>
                    <h3>Hello {name},</h3>
                    <p>{body}</p>
                    <p>Request details:</p>
                    <table border="1" cellpadding="5">
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                        </tr>
                        <tr>
                            <td>{name}</td>
                            <td>{email}</td>
                        </tr>
                    </table>
                    <h4>Items Requested:</h4>
                    {items_table}
                    <p><strong>Processed by:</strong> System</p>
                    <p>You will be notified once your request is reviewed.</p>
                </body>
            </html>
            """
    else:
        # Custom email without request details
        html_content = f"""
        <html>
            <body>
                <p>{body}</p>
                <p>Best regards,<br>{admin_name}</p>
            </body>
        </html>
        """

    # Set up email message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.attach(MIMEText(html_content, 'html'))

    # Send email via SMTP
    try:
        with smtplib.SMTP('10.64.4.200', 25) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError as e:
        raise Exception(f"SMTP Authentication Error: {e}")
    except Exception as e:
        raise Exception(f"Error sending email: {e}")

if __name__ == "__main__":
    # Test the function
    send_email(
        to_email="test@example.com",
        admin_name="Admin",
        subject="Test Email",
        body="This is a test email."
    )