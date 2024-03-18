### Import Packages

# File Manipulation

from io import StringIO

# Getting .env information
from dotenv import load_dotenv
import os

# Web

import requests # Accessing the Web

# Data Manipulation

import pandas as pd
import geopandas as gpd

# ~~~~~~~~~~~~~

def get_contacts(messaging_df):
    '''
    
    Sorry this is cryptic. Still trying to figure out the best way to this
    
    takes a dataframe with at least the fields api_id, message
    
    Gets contacts associated with the api_ids (record_ids in REDCap). 
    
    Returns api_ids, contacts, messages with the same indexing!
    
    ** Note: phone numbers come in the format '(XXX) XXX-XXXX'
    '''
    
    # Initialize the returned values
    
    api_ids = messaging_df.api_id.to_list()
    contacts = []
    messages = messaging_df.message.to_list()
    
    # Load env information
    
    load_dotenv()
    
    base_url = os.environ['CONTACT_INFO_BASEURL']
    redCap_token_signUp = os.environ['CONTACT_API_TOKEN']
    fieldname = os.environ['CONTACT_INFO_FIELD']
    
    # Initialize return value
    
    ## Prep the REDCap Query
    
    # For how to do this - https://education.arcus.chop.edu/redcap-api/
    # Redcap logic guide - https://cctsi.cuanschutz.edu/docs/librariesprovider28/redcap/redcap-logic-guide.pdf?sfvrsn=258e94ba_2
    # Info from PyCap - https://redcap-tools.github.io/PyCap/api_reference/records/
    
    # Select by record_id <- probably not the best way, but I couldn't get 'record' to work properly in data
    
    record_id_strs = [str(record_id) for record_id in api_ids]
    filterLogic_str = '[record_id]=' + ' OR [record_id]='.join(record_id_strs)
    
    # Select fields
    
    field_names = f'record_id, {fieldname}' # Field Names
    
    data = {
    'token': redCap_token_signUp,
    'content': 'record',
    'fields' : field_names,
    'action': 'export',
    'format': 'csv',
    'type': 'flat',
    'csvDelimiter': '',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'csv',
    'filterLogic': filterLogic_str  
    }
    
    # Send the request
    r = requests.post(base_url, data=data)
    
    # Unpack the response
    
    if r.status_code == 200 and r.text != '\n':
        
        df = pd.read_csv(StringIO(r.text)) # Read as a dataframe
        
        sorted_df = df.set_index('record_id').loc[api_ids] # Sort df by input record_ids
        
        contacts = list(sorted_df[fieldname]) # Extract contacts
        
    else:
        print('Error Receiving REDCap data')
    
    return api_ids, contacts, messages
