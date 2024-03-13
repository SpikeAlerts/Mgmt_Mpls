'''
using this to handle all text sending functions. 
NEED TO uncomment Twilio in requirements.txt
'''

import os
from twilio.rest import Client

# Getting .env information
from dotenv import load_dotenv
import time # Sleeping
import numpy as np

def send_messages(numbers, messages): 
    '''
    basic send function that takes in a list of numbers + list of messages and sends them out
    '''

    load_dotenv()

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_number = os.environ['TWILIO_NUMBER']
    messaging_service_sid = os.environ['TWILIO_SERVICE_SID']
    
    # Check Unsubscriptions
    
    unsubscribed_indices = [] # check_unsubscriptions(numbers) # NEEDS WORK
    
    # pop() unsubscriptions from numbers/record_ids/messages list
        
    for unsubscribed_index in unsubscribed_indices:
        numbers.pop(unsubscribed_index)
        messages.pop(unsubscribed_index)
    
    client = Client(account_sid, auth_token)

    for number, message in zip(numbers, messages):

        msg = client.messages.create(
        body= message,
        messaging_service_sid=messaging_service_sid,
        from_=twilio_number,
        to=number # replace with number in PROD
        ) # should check error handling, if needed based on SDK
        
        time.sleep(1) # Sleeping for 1 second between sending messages
        
    return unsubscribed_indices
    
def check_unsubscriptions(numbers):
    '''Returns the indices of the phone numbers in numbers that have unsubscribed
    Which corresponds to record_ids_to_text'''

    load_dotenv()

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    
    unsubscribed_indices = []
    
    stop_key_words = ['STOP', 'STOPALL', 'UNSUBSCRIBE', 'CANCEL', 'END', 'QUIT'] # see https://support.twilio.com/hc/en-us/articles/223134027-Twilio-support-for-opt-out-keywords-SMS-STOP-filtering-

    # Set up Twilio Client

    client = Client(account_sid, auth_token)

    # Iterate through the numbers 
    
    for i, number in enumerate(numbers):
        
        messages_from = client.messages.list(from_=number) # Check if the numbers have responded, messages_from is a list twilio objects

        if len(messages_from) > 0: # If yes

            for message in messages_from: # What have they said?
    
                if message.body in stop_key_words: # If stopword

                    unsubscribed_indices += [i] # Keep track of that list index
                    
                    break

    return unsubscribed_indices
    
def delete_twilio_info(numbers):
    '''This function deletes texts to/from phone numbers in twilio
    '''
    
    load_dotenv()

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    # Set up Twilio Client

    client = Client(account_sid, auth_token)

    # Iterate through the unique numbers 
    
    numbers_unique = np.unique(numbers)
    
    for number in numbers_unique:
        
        messages_from = client.messages.list(from_=number) # Check if the numbers have responded, messages_from is a list twilio objects
        
        for message in messages_from:
        
            message.delete()

        messages_to = client.messages.list(to_=number) # Get all messages we have sent to this number, messages_to is a list twilio objects
        
        for message in messages_to:
        
            message.delete()
