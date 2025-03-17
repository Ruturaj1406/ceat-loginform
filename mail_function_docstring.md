def send_email(to_email, admin_name, subject, body, request_details=None, delivered_to=None, delivery_time=None):
    """Send an email using Gmail SMTP with dynamic content based on the subject.

    Args:
        to_email (str): Recipient's email address.
        admin_name (str): Name of the sender (e.g., "Admin", "Department Head").
        subject (str): Email subject line.
        body (str): Email body text (used as fallback if no request_details).
        request_details (dict, optional): Details of the request, including:
            - name (str): Requester's name.
            - email (str): Requester's email.
            - description (str): Request description (comma-separated items with quantities).
        delivered_to (str, optional): Name of the delivery recipient (used for "Delivered" emails).
        delivery_time (str, optional): Time of delivery (used for "Delivered" emails).

    Returns:
        bool: True if the email is sent successfully.

    Raises:
        Exception: If email validation fails (invalid address) or SMTP encounters an error, such as:
            - SMTPAuthenticationError: Invalid Gmail credentials.
            - SMTPServerDisconnected: Connection issues with Gmail SMTP server.
            - Other SMTP-related errors (e.g., rate limits, network issues).

    Notes:
        - Uses hardcoded Gmail credentials (from_email, password), which should be replaced with environment variables in production.
        - Generates HTML email content dynamically based on the subject (approved, rejected, delivered, or default).
        - Parses the request description to create an item table if request_details is provided.
    """