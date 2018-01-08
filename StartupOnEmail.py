import imaplib
import email

server= imaplib.IMAP4_SSL("imap.gmail.com")
server.login("jamiebickerspcmanager@googlemail.com", "yM05YkJWGirq")
server.select()
response, emails = server.search(None, "(SUBJECT 'startup')")
print(emails)
first = emails[0].split()[0]
response, data = server.fetch(first, "(RFC822)")
decoded = data[0][1].decode("utf-8")
message = email.message_from_string(decoded)
print(message["Date"])