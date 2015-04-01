import boto
import boto.ses

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from Sift.models import *

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

    def set_sourse ( __self, sourse ):
        __self._source = sourse

    def set_to_address( __self, to_address):
        __self._to_address = to_address

    def set_subject( __self, subject ):
        __self.subject = subject


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

    def enter_text( __self, text):
        __self.text = text

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

class VerifyEmail( object ):

    def __init__( __self ):
        __self.ses = connection
        __self.email_list = []

    def make_verify_email_list( __self ):
        email_list = {}
        email_list = __self.ses.list_verified_email_addresses()
        for key, value in email_list.items():
            temp = value
        temp = str(temp)
        temp = temp.split("'VerifiedEmailAddresses': ['")
        try:
            temp = str(temp[1])
            temp = temp.split("']}, 'ResponseMetadata'")
            temp = str(temp[0])
            temp = temp.split(']}}')
            temp = str(temp[0])
            temp = temp.split("', '")

            if temp[len(temp)-1][len(temp[len(temp)-1])-1] == "'":
                temp[len(temp)-1] = temp[len(temp)-1][:-1]

            __self.email_list = temp

            return( __self.email_list )
        except IndexError:
            __self.email_list = []
            return( __self.email_list )

    def list_verified_email( __self ):
        return __self.email_list

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

def main( email_address ):
    email_list = VerifyEmail()
    email_create = SESMessage(email_address, email_address, "test")
    email_list.verify_email(email_address)

def verify():
    email_list = VerifyEmail()
    email_list.make_verify_email_list()
    return email_list.list_verified_email()

def remove( email_address ):
    email_list = VerifyEmail()
    email_list.make_verify_email_list()
    email_list.delete_verified_email( email_address )


# source = 'johnnyclarence@hotmail.com'
# to_address = 'kangzhuang17@gmail.com'
# subject = 'test'
# msg = SESMessage( source, to_address, subject )
# msg.text = 'This is a test!'
# msg.html = 'HTML body'
# msg.send()
