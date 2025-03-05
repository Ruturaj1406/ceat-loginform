import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError

def send_email(to_email, admin_name, subject, body, request_details=None, delivered_to=None, delivery_time=None):
  
    from_email = 'Ruturajnavale1406@gmail.com'  # Replace with your Gmail address
    password = 'dgfy rkwj efij xcbb'            # Replace with your App Password if using Gmail with 2FA

    try:
        validate_email(to_email)
    except EmailNotValidError as e:
        print(f"Invalid email address: {e}")
        return

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

        # Create items table for email
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
                    <p>Details of the approved request are as follows:</p>
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
                    <p>We will process your request and notify you once the items are ready for pickup.</p>
                </body>
            </html>
            """
        elif "rejected" in subject.lower():
            html_content = f"""
            <html>
                <body>
                    <h3>Hello {name},</h3>
                    <p>We regret to inform you that your request has been rejected.</p>
                    <p>Details of the rejected request are as follows:</p>
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
                    <p>If you have any questions or need further clarification, please feel free to reach out to the support team.</p>
                </body>
            </html>
            """
        elif "delivered" in subject.lower() and delivered_to and delivery_time:
            html_content = f"""
            <html>
                <body>
                    <h3>Hello {name},</h3>
                    <p>Your requested item is delivered to: <strong>{delivered_to}</strong> on <strong>{delivery_time}</strong>.</p>
                    <p>Details of the delivered request are as follows:</p>
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
                    <p>If you can't receive the item, please contact us at <strong>9999999999</strong>.</p>
                    <p><strong>Processed by:</strong> {admin_name}</p>
                </body>
            </html>
            """
        else:
            html_content = f"""
            <html>
                <body>
                    <h3>Hello {name},</h3>
                    <p>{body}</p>
                    <p>Details of your request:</p>
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
                    <p>You will be notified once the request has been approved or rejected.</p>
                </body>
            </html>
            """
    else:
        # For custom emails without request details
        html_content = f"""
        <html>
            <body>
                <p>{body}</p>
                <p>Best regards,<br>{admin_name}</p>
            </body>
        </html>
        """

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Email successfully sent to {to_email}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")
