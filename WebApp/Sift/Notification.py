import boto
import boto.ses

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except:
    pass

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES=
        {
            'default':
            {
                  'ENGINE': 'django.db.backends.mysql',
                  'HOST': 'sellerforums.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
                  'PORT': '3306',
                  'USER': 'teamamzn',
                  'PASSWORD': 'TeamAmazon2015!',
                  'NAME': 'sellerforums',
                  'OPTIONS':
                  {
                      'autocommit': True,
                  }
            }
        }
    )

from models import *

connection = boto.ses.connect_to_region( 'us-west-2',
                                         aws_access_key_id = 'AKIAJPAOUUTITYRIGX2A',
                                         aws_secret_access_key = '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' )

class SESMessage( object ):

      def __init__( __self, source, to_addresses, subject, **kw):
            __self.ses = connection

            __self._source = source
            __self._to_addresses = to_addresses
            __self._cc_addresses = []
            __self._bcc_addresses = []

            __self.subject = subject
            __self.text = None
            __self.html = None
            __self.attachments = []
            __self.email_list = []

      def add_bcc_addresses( __self, bcc_address ):
            if bcc_address in __self._bcc_addresses:
                  return False
            else:
                  __self._bcc_addresses.append( bcc_address )
                  return True

      def delete_bcc_addresses( __self, bcc_address ):
            if bcc_address in __self._bcc_addresses:
                  __self._bcc_addresses.remove( bcc_address )
                  return True
            else:
                  return False

      def add_cc_address( __self, cc_address ):
            if cc_addresses in __self._cc_addresses:
                  return False
            else:
                  __self._cc_addresses.append( cc_address )
                  return True

      def delete_cc_address( __self, cc_address ):
            if cc_address in __self._cc_addresses:
                  __self._cc_addresses.remove( cc_address )
                  return True
            else:
                  return False

      def add_attachment( __self, attachment_path ):
            if attachment_path in __self.attachments:
                  return False
            else:
                  __self.attachments.append( attachment_path )
                  return True

      def delete_attachment( __self, attachment_path):
            if attachment_path in __self.attachments:
                  __self.attachments.remove( attachment_path )
                  return True
            else:
                  return False

      def make_verify_email_list( __self ):
            email_list = {}
            email_list = __self.ses.list_verified_email_addresses()

            temp = str(email_list.values())
            temp = temp.split
            temp = temp.split("VerifiedEmailAddresses': ['")
            temp = str(temp[1])
            temp = temp.split("']}}])")
            temp = str(temp[0])

            self.email_list = temp.split( "', '" )

      def check_email( __self, email_address ):
            if email_address in __self.email_list:
                  print ( 'The email address is already in the verified Email list.' )
                  return True
            else:
                  print ( 'The email address is not in the verified Email list.' )
                  return False

      def verify_email( __self, email_address ):
            if __self.check_email( email_address ):
                  print( 'The email address is already in the verified Email list.' )
                  return False
            else:
                  __self.ses.verify_email_address( email_address )
                  return True

      def delete_verified_email( __self, email_address ):
            if __self.check_email( email_address ):
                  __self.ses.delete_verified_email_address( email_address )
                  return True
            else:
                  print ( 'The email address is not in the verified Email list.' )
                  return False

      def send( __self ):
            try:

                  __self.ses
                  if not __self.attachments:

                        __self.ses.send_email( __self._source, __self.subject, __self.text or __self.html,
                                               __self._to_addresses, __self._cc_addresses,
                                               __self._bcc_addresses, format = 'text' if __self.text else 'html')

                  else:
                        message = MIMEMultipart()
                        message.preamble = 'Multipart message.\n'

                        text = MIMEText( __self.text )
                        message.attach( text )

                        for i in __self.attachments:
                              name = i.split('/')
                              name = str(name[name.len()])

                              attachment = MIMEApplication( open( i, 'rb' ).read() )
                              attachment.add_header( 'Content-Disposition', 'attachment',
                                                     filename = name)
                              message.attach(attachment)

                        __self.ses.send_raw_email( message.as_string(), source = __self._source,
                                                   destinations = __self._cc_addresses )
            except:
                  print ( 'Connection not Found.' )

def main():
    c = Notification(email="pritch93@gmail.com")
    c.save()
    temp = Notification.objects.all()
    print (temp)

if __name__ == "__main__":
    main()


# source = 'johnnyclarence@hotmail.com'
# to_address = 'kangzhuang17@gmail.com'
# subject = 'test'
# msg = SESMessage( source, to_address, subject )
# msg.text = 'This is a test!'
# msg.html = 'HTML body'
# msg.send()
