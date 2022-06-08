import smtplib

class EmailSender:
    
    
    def __init__(self):
        self.username = 'bkcitsystem@gmail.com'
        self.password ='htifchddaxgfljaj'
        self.sender = 'bkcitsystem@gmail.com'
        self.server = smtplib.SMTP('smtp.gmail.com:587')
    
    def sendEmail(self,msg,destination):
        self.destination = destination
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.username,self.password)
        self.server.sendmail(self.sender, self.destination, msg)
        self.server.quit()
        
        