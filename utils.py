import smtplib
from email.message import EmailMessage
import datetime

# ✅ Function to send email
def send_email(subject, body, to_email):
    try:
        msg = EmailMessage()
        msg.set_content(body)  # Plain text

        # ✅ HTML version of email
        msg.add_alternative(f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="background-color: #fff; padding: 20px; border-radius: 8px;">
              <h2 style="color: #2c3e50;">E-Waste Portal</h2>
              <p style="font-size: 14px; color: #333;">{body}</p>
              <br>
              <p style="font-size: 13px; color: #888;">Sent on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
          </body>
        </html>
        """, subtype='html')

        msg['Subject'] = subject
        msg['From'] = "ewaste079@gmail.com"
        msg['To'] = to_email

        # ✅ Gmail SMTP with App Password
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("ewaste079@gmail.com", "pwytyretdwchdqfg")  # 🔐 App Password, no spaces!
        server.send_message(msg)
        server.quit()

        print(f"[✅] Email successfully sent to {to_email}")
        return True

    except Exception as e:
        print(f"[❌] Email sending failed: {e}")
        return False

# ✅ Get today's date
def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

# ✅ Validate numeric weight
def is_valid_weight(value):
    try:
        val = float(value)
        return val >= 0
    except ValueError:
        return False

# ✅ Sample usage
if __name__ == "__main__":
    subject = "Welcome to E-Waste Portal"
    body = "Hello, Pranav,<br><br>Thank you for registering with the E-Waste Management System.<br>Start recycling today and save the environment!"
    to_email = "ewaste079@gmail.com"  # Change to actual recipient

    send_email(subject, body, to_email)
