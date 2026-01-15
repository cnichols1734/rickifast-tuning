import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template, current_app

def send_quote_email(quote):
    """
    Send an email with quote details to the client
    """
    # Get client email
    client_email = quote.client.email
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Aqua Force Pressure Washing - Quote #{quote.id}'
    msg['From'] = os.environ.get('MAIL_USERNAME', 'noreply@aquaforce.com')
    msg['To'] = client_email
    
    # Create the HTML content of the email
    html = render_template('emails/quote.html', quote=quote)
    
    # Convert to MIMEText objects and attach to message
    html_part = MIMEText(html, 'html')
    msg.attach(html_part)
    
    # Send email
    if current_app.config.get('TESTING', False):
        # In testing, don't actually send emails
        return
    
    try:
        # Connect to the server
        smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('MAIL_PORT', 587))
        username = os.environ.get('MAIL_USERNAME')
        password = os.environ.get('MAIL_PASSWORD')
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        
        # Send email
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.close()
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

def send_invoice_email(invoice):
    """
    Send an email with invoice details to the client
    """
    # Get client email
    client_email = invoice.client.email
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Aqua Force Pressure Washing - Invoice #{invoice.id}'
    msg['From'] = os.environ.get('MAIL_USERNAME', 'noreply@aquaforce.com')
    msg['To'] = client_email
    
    # Create the HTML content of the email
    html = render_template('emails/invoice.html', invoice=invoice)
    
    # Convert to MIMEText objects and attach to message
    html_part = MIMEText(html, 'html')
    msg.attach(html_part)
    
    # Send email
    if current_app.config.get('TESTING', False):
        # In testing, don't actually send emails
        return
    
    try:
        # Connect to the server
        smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('MAIL_PORT', 587))
        username = os.environ.get('MAIL_USERNAME')
        password = os.environ.get('MAIL_PASSWORD')
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        
        # Send email
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.close()
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise 