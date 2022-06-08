import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    
    
    def __init__(self):
        self.username = 'bkcitsystem@gmail.com'
        self.password ='htifchddaxgfljaj'
        self.sender = 'bkcitsystem@gmail.com'
        self.server = smtplib.SMTP('smtp.gmail.com:587')
    
    def sendEmail(self,sv,lophp,buoihoc,destination):
        self.destination = destination
        buoihoc=buoihoc.split('_')[-1]
        message = """\
            <html>
            <head></head>
            <body>
                <p><h1>Sinh viên {} có mặt trong lớp {} buổi học {}</h1></p>
            </body>
            </html>
            """
        message = message.format(sv,lophp,buoihoc)
        msg = MIMEText(message, "html")
        msg['Subject'] = "Thông báo điểm danh"
        msg['From'] = str(self.sender)
        msg['To'] = str(self.destination)
        
        
        
        
        
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.username,self.password)
        self.server.sendmail(self.sender, self.destination, msg.as_string())
        self.server.quit()
        
        