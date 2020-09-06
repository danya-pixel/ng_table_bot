from __future__ import print_function

import datetime
import os.path
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1kECw2Cm7pvuo89XrhIxZPR4Qk3gEEdvYJTX_7Hqquoo'
# SAMPLE_RANGE_NAME = '2 курс!B2:P'

TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'
CONFIG_PATH = 'data'

cache_sheet_value = {}


def cache_sheet(func):
    def memoized_func(range_name):
        today = datetime.datetime.now()
        if range_name in cache_sheet_value and cache_sheet_value[range_name].get('time').day == today.day \
                and cache_sheet_value[range_name].get('time').hour + 4 >= today.hour:
            return cache_sheet_value[range_name]['result']
        result = func(range_name)
        cache_sheet_value[range_name] = {
            "result": result,
            "time": datetime.datetime.now()
        }
        return result

    return memoized_func


@cache_sheet
def get_sheet_values(range_name: str):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(CONFIG_PATH, TOKEN_PATH)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_path = os.path.join(CONFIG_PATH, CREDENTIALS_PATH)
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=range_name).execute()
    return result.get('values', [])
