import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import cfgfile

emailusercfgpath = '../Private/user.ini'
emailuserdict = cfgfile.read(emailusercfgpath,'gmail')

# # Create message container - the correct MIME type is multipart/alternative.
# msg = MIMEMultipart('alternative')
# msg['Subject'] = "Raspberry Pi"
# msg['From'] = emailuserdict['address']
# msg['To'] = emailuserdict['emailrecipient']

# # Create the body of the message
# text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org"
# msg.attach(MIMEText(text, 'plain'))

# server = smtplib.SMTP('smtp.gmail.com', 587)
# server.starttls()
# server.login(emailuserdict['address'], emailuserdict['password'])

# server.sendmail(emailuserdict['address'],emailuserdict['emailrecipient'], msg.as_string())
# #server.sendmail(emailuserdict['address'],emailuserdict['textrecipient'], msg)
# server.quit()

def SendMail(message, subject='Raspberry Pi'):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = emailuserdict['address']
    msg['To'] = emailuserdict['emailrecipient']
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(emailuserdict['address'], emailuserdict['password'])

    server.sendmail(emailuserdict['address'],emailuserdict['emailrecipient'], msg.as_string())
    #server.sendmail(emailuserdict['address'],emailuserdict['textrecipient'], msg)
    server.quit()

def SendText(message):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Text'
    msg['From'] = emailuserdict['address']
    msg['To'] = emailuserdict['textrecipient']
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(emailuserdict['address'], emailuserdict['password'])

    #server.sendmail(emailuserdict['address'],emailuserdict['emailrecipient'], msg.as_string())
    server.sendmail(emailuserdict['address'],emailuserdict['textrecipient'], msg.as_string())
    server.quit()
