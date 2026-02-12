import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from flask import current_app


def send_email(to_email, subject, html_body, attachments=None, inline_images=None):
    """Send an email via Gmail SMTP.
    
    Args:
        to_email: Single email string or list of email strings.
        subject: Email subject.
        html_body: HTML content of the email.
        attachments: Optional list of dicts with 'filename', 'content' (bytes).
        inline_images: Optional list of dicts with 'cid', 'content' (bytes), 'filename'.
    """
    app = current_app._get_current_object()

    # Normalise recipients
    if isinstance(to_email, str):
        recipients = [e.strip() for e in to_email.split(',') if e.strip()]
    else:
        recipients = list(to_email)

    msg = MIMEMultipart('mixed')
    msg['From'] = app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    # HTML body (with optional inline images via CID)
    if inline_images:
        related_part = MIMEMultipart('related')
        alt_part = MIMEMultipart('alternative')
        alt_part.attach(MIMEText(html_body, 'html'))
        related_part.attach(alt_part)
        for img in inline_images:
            mime_img = MIMEImage(img['content'], _subtype=img.get('subtype', 'png'))
            mime_img.add_header('Content-ID', f'<{img["cid"]}>')
            mime_img.add_header('Content-Disposition', 'inline', filename=img.get('filename', 'image.png'))
            related_part.attach(mime_img)
        msg.attach(related_part)
    else:
        html_part = MIMEMultipart('alternative')
        html_part.attach(MIMEText(html_body, 'html'))
        msg.attach(html_part)

    # Attachments
    if attachments:
        for att in attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(att['content'])
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{att["filename"]}"')
            msg.attach(part)

    try:
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.ehlo()
        if app.config['MAIL_USE_TLS']:
            server.starttls()
            server.ehlo()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.sendmail(msg['From'], recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email to {recipients}: {e}')
        return False


def send_password_reset_email(user, reset_url):
    """Send password reset email."""
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px;">
        <h2 style="color: #0f172a; margin-bottom: 8px;">Reset Your Password</h2>
        <p style="color: #64748b; font-size: 14px; line-height: 1.6;">
            Hi {user.username}, we received a request to reset your password for your Rickifast Tuning account.
        </p>
        <a href="{reset_url}" style="display: inline-block; margin: 24px 0; padding: 12px 24px; background-color: #0f172a; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">
            Reset Password
        </a>
        <p style="color: #94a3b8; font-size: 13px; line-height: 1.5;">
            This link expires in 1 hour. If you didn't request this, you can safely ignore this email.
        </p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
        <p style="color: #94a3b8; font-size: 12px;">Rickifast Tuning LLC</p>
    </div>
    """
    return send_email(user.email, 'Reset Your Password — Rickifast Tuning', html)


def send_invite_email(email, invite_url, invited_by):
    """Send account invite email."""
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px;">
        <h2 style="color: #0f172a; margin-bottom: 8px;">You're Invited!</h2>
        <p style="color: #64748b; font-size: 14px; line-height: 1.6;">
            {invited_by} has invited you to create an account on the Rickifast Tuning CRM system.
        </p>
        <a href="{invite_url}" style="display: inline-block; margin: 24px 0; padding: 12px 24px; background-color: #0f172a; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">
            Create Your Account
        </a>
        <p style="color: #94a3b8; font-size: 13px; line-height: 1.5;">
            This invitation expires in 48 hours. Click the link above to set up your username and password.
        </p>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
        <p style="color: #94a3b8; font-size: 12px;">Rickifast Tuning LLC</p>
    </div>
    """
    return send_email(email, "You're Invited — Rickifast Tuning CRM", html)


# ---------------------------------------------------------------------------
# Invoice emailing
# ---------------------------------------------------------------------------

def generate_invoice_pdf(invoice):
    """Generate a PDF for an invoice using fpdf2. Returns bytes."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ---- Header / Logo area ----
    pdf.set_fill_color(15, 23, 42)  # #0f172a
    pdf.rect(0, 0, 210, 38, 'F')
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(250, 204, 21)  # bolt yellow
    pdf.set_xy(15, 8)
    pdf.cell(0, 10, 'RICKIFAST', ln=False)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(148, 163, 184)
    pdf.set_xy(15, 18)
    pdf.cell(0, 6, 'TUNING LLC', ln=True)

    # Invoice number in header
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(130, 10)
    pdf.cell(65, 10, invoice.invoice_number, align='R')

    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)

    # ---- Dates ----
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.set_x(15)
    pdf.cell(90, 6, f'Created: {invoice.created_at.strftime("%B %d, %Y")}')
    if invoice.due_date:
        pdf.cell(0, 6, f'Due: {invoice.due_date.strftime("%B %d, %Y")}', align='R')
    pdf.ln(10)

    # ---- Client info ----
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_x(15)
    pdf.cell(0, 7, invoice.client.full_name, ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(15)
    pdf.cell(0, 6, invoice.client.vehicle_display, ln=True)
    if invoice.client.email:
        pdf.set_x(15)
        pdf.cell(0, 6, invoice.client.email, ln=True)
    if invoice.client.phone:
        pdf.set_x(15)
        pdf.cell(0, 6, invoice.client.phone, ln=True)
    pdf.ln(8)

    # ---- Table header ----
    pdf.set_fill_color(245, 245, 245)
    pdf.set_text_color(100, 100, 100)
    pdf.set_font('Helvetica', 'B', 9)
    col_w = [80, 18, 28, 18, 32]
    headers = ['DESCRIPTION', 'QTY', 'PRICE', 'TAX', 'AMOUNT']
    aligns = ['L', 'R', 'R', 'C', 'R']
    x_start = 15
    pdf.set_x(x_start)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=0, align=aligns[i], fill=True)
    pdf.ln()

    # ---- Table rows ----
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(50, 50, 50)
    for item in invoice.items:
        pdf.set_x(x_start)
        pdf.cell(col_w[0], 7, item.description[:45], border=0, align='L')
        pdf.cell(col_w[1], 7, str(item.quantity), border=0, align='R')
        pdf.cell(col_w[2], 7, f'${item.unit_price:,.2f}', border=0, align='R')
        pdf.cell(col_w[3], 7, 'Yes' if item.taxable else '', border=0, align='C')
        pdf.cell(col_w[4], 7, f'${item.amount:,.2f}', border=0, align='R')
        pdf.ln()

    # Separator line
    pdf.ln(2)
    pdf.set_draw_color(220, 220, 220)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    # ---- Totals ----
    def _total_row(label, value, bold=False):
        pdf.set_font('Helvetica', 'B' if bold else '', 11 if bold else 10)
        pdf.set_x(120)
        pdf.cell(42, 7, label, align='R')
        pdf.cell(32, 7, value, align='R')
        pdf.ln()

    pdf.set_text_color(80, 80, 80)
    _total_row('Subtotal', f'${invoice.calculate_subtotal():,.2f}')
    _total_row(f'Tax ({invoice.tax_rate * 100:.2f}%)', f'${invoice.calculate_tax():,.2f}')
    pdf.set_text_color(0, 0, 0)
    _total_row('Total', f'${invoice.calculate_total():,.2f}', bold=True)

    paid = invoice.calculate_paid()
    if paid > 0:
        pdf.set_text_color(22, 163, 74)
        _total_row('Paid', f'-${paid:,.2f}')
        pdf.set_text_color(0, 0, 0)
        _total_row('Balance Due', f'${invoice.calculate_balance():,.2f}', bold=True)

    # ---- Notes ----
    if invoice.notes:
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(15)
        pdf.cell(0, 7, 'Notes', ln=True)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.set_x(15)
        pdf.multi_cell(170, 6, invoice.notes)

    # ---- Footer ----
    pdf.set_y(-25)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(0, 5, 'Rickifast Tuning LLC', align='C', ln=True)
    pdf.cell(0, 5, 'Thank you for your business!', align='C')

    return pdf.output()


def _generate_logo_png():
    """Generate a Rickifast logo PNG using Pillow for email embedding."""
    from PIL import Image, ImageDraw
    import io

    size = 88  # 2x for retina display at 44px
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark rounded rectangle background
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=20, fill=(15, 23, 42))

    # Lightning bolt polygon (scaled from 48x48 SVG coordinates)
    s = size / 48
    bolt = [
        (27 * s, 8 * s),
        (14 * s, 27 * s),
        (23 * s, 27 * s),
        (20 * s, 40 * s),
        (33 * s, 21 * s),
        (24 * s, 21 * s),
    ]
    draw.polygon(bolt, fill=(250, 204, 21))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def build_invoice_email_html(invoice):
    """Build a clean HTML email body for an invoice."""
    items_html = ''
    for item in invoice.items:
        items_html += f'''
            <tr>
                <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:13px;color:#333;">{item.description}</td>
                <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:13px;color:#555;text-align:right;">{item.quantity}</td>
                <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:13px;color:#555;text-align:right;">${item.unit_price:,.2f}</td>
                <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:13px;color:#555;text-align:center;">{"Yes" if item.taxable else ""}</td>
                <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:13px;font-weight:600;color:#111;text-align:right;">${item.amount:,.2f}</td>
            </tr>'''

    paid_section = ''
    paid = invoice.calculate_paid()
    if paid > 0:
        paid_section = f'''
            <tr>
                <td style="padding:6px 0;font-size:13px;color:#16a34a;">Paid</td>
                <td style="padding:6px 0;font-size:13px;color:#16a34a;text-align:right;">-${paid:,.2f}</td>
            </tr>
            <tr>
                <td style="padding:8px 0;font-size:16px;font-weight:700;color:#0f172a;border-top:2px solid #e5e5e5;">Balance Due</td>
                <td style="padding:8px 0;font-size:16px;font-weight:700;color:#0f172a;text-align:right;border-top:2px solid #e5e5e5;">${invoice.calculate_balance():,.2f}</td>
            </tr>'''

    due_text = ''
    if invoice.due_date:
        due_text = f'<p style="margin:0;color:#64748b;font-size:13px;">Due: {invoice.due_date.strftime("%B %d, %Y")}</p>'

    notes_section = ''
    if invoice.notes:
        notes_section = f'''
        <div style="margin-top:24px;padding:16px;background-color:#f8fafc;border-radius:8px;">
            <p style="margin:0 0 4px 0;font-weight:600;font-size:13px;color:#0f172a;">Notes</p>
            <p style="margin:0;font-size:13px;color:#64748b;line-height:1.5;white-space:pre-line;">{invoice.notes}</p>
        </div>'''

    html = f'''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background-color:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<div style="max-width:640px;margin:0 auto;padding:24px 16px;">

    <!-- Header -->
    <div style="background-color:#0f172a;border-radius:12px 12px 0 0;padding:28px 32px;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
                <td>
                    <table cellpadding="0" cellspacing="0" border="0"><tr>
                        <td style="padding-right:12px;vertical-align:middle;">
                            <img src="cid:logo" width="44" height="44" alt="Rickifast" style="display:block;border-radius:10px;">
                        </td>
                        <td style="vertical-align:middle;">
                            <span style="font-size:22px;font-weight:800;color:#facc15;letter-spacing:-0.02em;">RICKIFAST</span><br>
                            <span style="font-size:10px;font-weight:600;color:#94a3b8;letter-spacing:0.25em;">TUNING LLC</span>
                        </td>
                    </tr></table>
                </td>
                <td style="text-align:right;">
                    <span style="font-size:12px;font-weight:600;color:#94a3b8;text-transform:uppercase;letter-spacing:0.1em;">Invoice</span><br>
                    <span style="font-size:18px;font-weight:700;color:#ffffff;">{invoice.invoice_number}</span>
                </td>
            </tr>
        </table>
    </div>

    <!-- Body -->
    <div style="background-color:#ffffff;padding:32px;border-radius:0 0 12px 12px;border:1px solid #e2e8f0;border-top:none;">

        <!-- Client & dates -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
            <tr>
                <td style="vertical-align:top;">
                    <p style="margin:0 0 2px 0;font-weight:600;font-size:15px;color:#0f172a;">{invoice.client.full_name}</p>
                    <p style="margin:0;color:#64748b;font-size:13px;">{invoice.client.vehicle_display}</p>
                    {"<p style='margin:2px 0 0 0;color:#64748b;font-size:13px;'>" + invoice.client.email + "</p>" if invoice.client.email else ""}
                    {"<p style='margin:2px 0 0 0;color:#64748b;font-size:13px;'>" + invoice.client.phone + "</p>" if invoice.client.phone else ""}
                </td>
                <td style="text-align:right;vertical-align:top;">
                    <p style="margin:0;color:#64748b;font-size:13px;">Created: {invoice.created_at.strftime("%B %d, %Y")}</p>
                    {due_text}
                </td>
            </tr>
        </table>

        <!-- Line items -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;">
            <thead>
                <tr style="background-color:#f8fafc;">
                    <th style="padding:10px 12px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;font-weight:600;border-bottom:1px solid #e5e5e5;">Description</th>
                    <th style="padding:10px 12px;text-align:right;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;font-weight:600;border-bottom:1px solid #e5e5e5;">Qty</th>
                    <th style="padding:10px 12px;text-align:right;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;font-weight:600;border-bottom:1px solid #e5e5e5;">Price</th>
                    <th style="padding:10px 12px;text-align:center;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;font-weight:600;border-bottom:1px solid #e5e5e5;">Tax</th>
                    <th style="padding:10px 12px;text-align:right;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;color:#94a3b8;font-weight:600;border-bottom:1px solid #e5e5e5;">Amount</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>

        <!-- Totals -->
        <table width="280" cellpadding="0" cellspacing="0" border="0" style="margin-left:auto;">
            <tr>
                <td style="padding:6px 0;font-size:13px;color:#64748b;">Subtotal</td>
                <td style="padding:6px 0;font-size:13px;color:#64748b;text-align:right;">${invoice.calculate_subtotal():,.2f}</td>
            </tr>
            <tr>
                <td style="padding:6px 0;font-size:13px;color:#64748b;">Tax ({invoice.tax_rate * 100:.2f}%)</td>
                <td style="padding:6px 0;font-size:13px;color:#64748b;text-align:right;">${invoice.calculate_tax():,.2f}</td>
            </tr>
            <tr>
                <td style="padding:8px 0;font-size:16px;font-weight:700;color:#0f172a;border-top:2px solid #e5e5e5;">Total</td>
                <td style="padding:8px 0;font-size:16px;font-weight:700;color:#0f172a;text-align:right;border-top:2px solid #e5e5e5;">${invoice.calculate_total():,.2f}</td>
            </tr>
            {paid_section}
        </table>

        {notes_section}
    </div>

    <!-- Footer -->
    <div style="text-align:center;padding:20px 0 8px 0;">
        <p style="margin:0;font-size:12px;color:#94a3b8;">Thank you for your business!</p>
        <p style="margin:4px 0 0 0;font-size:11px;color:#cbd5e1;">Rickifast Tuning LLC</p>
    </div>

</div>
</body>
</html>'''
    return html


def send_invoice_email(invoice, recipient_emails, include_pdf=True):
    """Send an invoice email with optional PDF attachment.
    
    Args:
        invoice: Invoice model instance.
        recipient_emails: Comma-separated string or list of email addresses.
        include_pdf: Whether to attach a PDF copy.
    Returns:
        True on success, False on failure.
    """
    html_body = build_invoice_email_html(invoice)
    subject = f'Invoice {invoice.invoice_number} — Rickifast Tuning LLC'

    attachments = []
    if include_pdf:
        try:
            pdf_bytes = generate_invoice_pdf(invoice)
            attachments.append({
                'filename': f'{invoice.invoice_number}.pdf',
                'content': pdf_bytes,
            })
        except Exception as e:
            current_app.logger.error(f'PDF generation failed: {e}')

    # Generate logo PNG for inline CID embedding
    inline_images = []
    try:
        logo_png = _generate_logo_png()
        inline_images.append({'cid': 'logo', 'content': logo_png, 'filename': 'logo.png'})
    except Exception as e:
        current_app.logger.error(f'Logo generation failed: {e}')

    return send_email(recipient_emails, subject, html_body,
                      attachments=attachments or None,
                      inline_images=inline_images or None)
