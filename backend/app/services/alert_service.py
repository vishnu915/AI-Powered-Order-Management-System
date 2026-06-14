from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import Alert, Order
from app.config import get_settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import os

class AlertService:
    def __init__(self, db: Session = None):
        self.db = db
        self.settings = get_settings()
        self.twilio_client = Client(
            self.settings.twilio_account_sid,
            self.settings.twilio_auth_token
        ) if self.settings.twilio_account_sid else None
    
    def create_breach_alert(self, order: Order):
        """Create and send SLA breach alert"""
        alert = Alert(
            order_id=order.id,
            alert_type="breach_warning",
            message=f"Order {order.order_id} is approaching SLA breach. Expected delivery: {order.expected_delivery_date}",
            priority="high"
        )
        
        self.db.add(alert)
        self.db.commit()
        
        # Send alerts
        self.send_email_alert(order, alert)
        self.send_whatsapp_alert(order, alert)
    
    def send_email_alert(self, order: Order, alert: Alert):
        """Send email notification via SendGrid"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=self.settings.sendgrid_from_email,
                to_emails=order.customer_email,
                subject=f"Order {order.order_id} - SLA Alert",
                html_content=self._generate_email_html(order, alert)
            )
            
            sg = SendGridAPIClient(self.settings.sendgrid_api_key)
            response = sg.send(message)
            
            alert.is_sent = True
            alert.sent_via = "email"
            alert.sent_at = datetime.utcnow()
            self.db.commit()
            
            print(f"Email sent: {response.status_code}")
        except Exception as e:
            print(f"Email send failed: {str(e)}")
    
    def send_whatsapp_alert(self, order: Order, alert: Alert):
        """Send WhatsApp notification via Twilio"""
        try:
            if not self.twilio_client:
                return
            
            message_body = f"Hi {order.customer_name}, your order {order.order_id} is approaching delivery deadline. Check status: https://dashboard.eyewear.com/order/{order.id}"
            
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=f"whatsapp:{self.settings.twilio_phone}",
                to=f"whatsapp:{order.customer_phone}"
            )
            
            alert.is_sent = True
            alert.sent_via = "whatsapp"
            alert.sent_at = datetime.utcnow()
            self.db.commit()
            
            print(f"WhatsApp sent: {message.sid}")
        except Exception as e:
            print(f"WhatsApp send failed: {str(e)}")
    
    def _generate_email_html(self, order: Order, alert: Alert) -> str:
        return f"""
        <html>
        <body>
            <h2>Order Alert: {order.order_id}</h2>
            <p>{alert.message}</p>
            <p><strong>Details:</strong></p>
            <ul>
                <li>Customer: {order.customer_name}</li>
                <li>Lens Type: {order.lens_type}</li>
                <li>Expected Delivery: {order.expected_delivery_date}</li>
                <li>Current Status: {order.status}</li>
            </ul>
            <p><a href="https://dashboard.eyewear.com/order/{order.id}">View Order</a></p>
        </body>
        </html>
        """