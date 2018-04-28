import os, smtplib

def send_mail(toaddrs, subject, body):
    fromaddr = 'facetree.petri@gmail.com'
    password = os.getenv('SMTP_PASSWORD')
    msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (fromaddr, toaddrs, subject, body)
    server = smtplib.SMTP_SSL('smtp.gmail.com')
    server.login(fromaddr, password)
    server.sendmail(fromaddr, [toaddrs], bytes(msg, 'utf8'))
    server.quit()