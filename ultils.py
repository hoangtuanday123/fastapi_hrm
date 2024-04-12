from io import BytesIO
import qrcode
from base64 import b64encode
import smtplib
from email.message import EmailMessage
import os
import base64
file_path_default = "MacBook.jpg"
def get_b64encoded_qr_image(data):
    print(data)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered)
    return b64encode(buffered.getvalue()).decode("utf-8")
class Settings:
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # in mins
    COOKIE_NAME = "access_token"
settings = Settings()





def send_mail(to, subject, template,html):
    email_address=os.getenv('EMAIL_USER')
    email_password=os.getenv('EMAIL_PASSWORD')
    #create email
    msg=EmailMessage()
    msg['Subject']=subject
    msg['From']=email_address
    msg['To']=to
    # dung cho send mail xacnhan
    if html==1:
        msg.add_alternative(template, subtype='html')
    else:
        msg.set_content(template)
    #send email
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(email_address,email_password)
        smtp.send_message(msg)
    #return "email successfully sent"

def encode_id(id: int) -> str:
    encoded_id = base64.urlsafe_b64encode(str(id).encode()).decode()
    return encoded_id

def decode_id(encoded_id: str) -> int:
    decoded_id = base64.urlsafe_b64decode(encoded_id).decode()
    return int(decoded_id)

