from __future__ import absolute_import
import boto
import boto.ses
import boto.sns

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

try:
    from Sift.models import *
except:
    from models import *

connection_ses = boto.ses.connect_to_region( 'us-west-2',
                                         aws_access_key_id = 'AKIAJPAOUUTITYRIGX2A',
                                         aws_secret_access_key = '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' )

connection_sns = boto.sns.connect_to_region( 'us-west-2',
                                         aws_access_key_id = 'AKIAJPAOUUTITYRIGX2A',
                                         aws_secret_access_key = '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' )


class SESMessage( object ):

    def __init__( __self, source, to_addresses, subject, **kw):
        __self.ses = connection_ses

        __self._source = source
        __self._to_addresses = to_addresses
        __self._cc_addresses = []
        __self._bcc_addresses = []

        __self.subject = subject
        __self.text = ''
        __self.html = None
        __self.attachments = []

    def set_source ( __self, source ):
        __self._source = source

    def set_to_address( __self, to_address):
        __self._to_address = to_address

    def set_subject( __self, subject ):
        __self.subject = __self.subject + subject

    def set_text( __self, text):
        __self.text = __self.text + text

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

    def add_cc_address(__self, cc_address):
        if cc_address in __self._cc_addresses:
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

class SESVerifyEmail( object ):

    def __init__( __self ):
        __self.ses = connection_ses
        __self.email_list = []

    def make_verify_email_list( __self ):
        temp_email_list = __self.ses.list_verified_email_addresses()
        __self.email_list = temp_email_list['ListVerifiedEmailAddressesResponse']['ListVerifiedEmailAddressesResult']['VerifiedEmailAddresses']
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

class SNSNotification( object ):

    class arn( object ):
        def __init__ ( __self ):
            __self.topic = ''
            __self.arn = ''
            __self.endpoint = []
            __self.protocol = ''

        def set_topic( __self, topic ):
            __self.topic = topic

        def set_arn(  __self, arn ):
            __self.arn = arn

        def set_arn_endpoint( __self, endpoint, endpoint_arn ):
            temp = []
            temp.append( endpoint )
            temp.append( endpoint_arn )
            __self.endpoint.append( temp )

        def set_protocol( __self, protocol ):
            __self.protocol = protocol

        def get_topic( __self ):
            return( __self.topic )

        def get_arn( __self ):
            return( __self.arn )

        def get_endpoint( __self ):
            temp = []
            for i in __self.endpoint:
                temp.append( i )
            return( temp )

        def get_protocol( __self ):
            return( __self.protocol )

    def __init__( __self ):
        __self.sns = connection_sns

        __self.topic = ''
        __self.arn = ''

        __self.subject = ''
        __self.message = ''
        __self.arn_list = []
        __self.subscription_list = []


    def make_arn_list( __self ):
        topic_list = __self.sns.get_all_topics()
        topic_list = topic_list['ListTopicsResponse']['ListTopicsResult']['Topics']

        for i in range( len(topic_list) ):
            temp_arn = SNSNotification.arn()

            temp = topic_list[i]['TopicArn']
            temp_arn.set_arn( temp )

            subscription_list = __self.sns.get_all_subscriptions_by_topic( topic_list[i]['TopicArn'] )
            subscription_list = subscription_list['ListSubscriptionsByTopicResponse']['ListSubscriptionsByTopicResult']['Subscriptions']

            for j in subscription_list:
                temp_arn.set_protocol = j['Protocol']
                temp_arn.set_arn_endpoint( j['Endpoint'], j['SubscriptionArn'])

            temp = topic_list[i]['TopicArn'].split(':')
            temp = temp[len(temp)-1]
            temp_arn.set_topic( temp )

            __self.arn_list.append( temp_arn )

    def get_topic_list( __self ):
        temp = []
        for i in __self.arn_list:
            temp.append( i.get_topic() )
        return( temp )

    def get_topic_arn( __self, topic ):
        for i in __self.arn_list:
            if i.get_topic() == topic:
                return( i.get_arn() )

    def get_arn_list( __self ):
        return( __self.arn_list )

    def set_topic_arn( __self, topic ):
        for i in __self.arn_list:
            if i.get_topic() == topic:
                __self.arn = i.get_arn()
        return( __self.arn )

    def get_subscription_list( __self ):
        temp = []
        for i in __self.arn_list:
            temp.append( i )
        return( temp )

    def set_subject( __self, subject ):
        __self.subject = subject

    def set_message( __self, message ):
        __self.message = message

    def create_topic( __self, topic ):
        __self.sns.create_topic( topic )

    def delete_topic( __self, topic ):
        __self.sns.delete_topic( topic )

    def subscribe( __self, topic, protocol, end_point ):
        for i in __self.arn_list:
            if i.get_topic() == topic:
                topic_arn = i.get_arn()
        __self.sns.subscribe( topic_arn, protocol, end_point )

    def unsubscribe( __self, endpoint ):
        for i in __self.arn_list:
            temp = i.get_endpoint()
            for j in temp:
                if j[0] == endpoint:
                    __self.sns.unsubscribe( j[1] )


    def publication( __self ):
        __self.sns.publish( __self.arn, __self.message )


def add_email( email_address ):
    subscription_list = SNSNotification()
    subscription_list.make_arn_list()
    subscription_list.subscribe( 'NightlyRun', 'email', email_address )

def email_verify():
    subscription_list = SNSNotification()
    subscription_list.make_arn_list()
    temp = subscription_list.get_arn_list()
    email_list = []
    temp_list = []

    for i in temp:
        for j in i.get_endpoint():
            temp_list.append( j )
    for i in temp_list:
        email_list.append(i[0])

    return( email_list )

def get_nightly_list():
    subscription_list = SNSNotification()
    subscription_list.make_arn_list()
    temp = subscription_list.get_arn_list()
    nightly_list = []
    temp_list = []

    for i in temp:
        if 'NightlyRun' == i.get_topic():
            temp_list = i.get_endpoint()
    for i in temp_list:
        nightly_list.append(i[0])

    return ( nightly_list )

def get_important_list():
    subscription_list = SNSNotification()
    subscription_list.make_arn_list()
    temp = subscription_list.get_arn_list()
    important_list = []
    temp_list = []

    for i in temp:
        if 'ImportantChanges' == i.get_topic():
            temp_list = i.get_endpoint()
    for i in temp_list:
        important_list.append(i[0])

    return ( important_list )


def remove( email_address ):
    subscription_list = SNSNotification()
    subscription_list.make_arn_list()
    subscription_list.unsubscribe( email_address )

    # email_list = SESVerifyEmail()
    # email_list.make_verify_email_list()
    # email_list.delete_verified_email( email_address )