from __future__ import print_function
import pickle
import os.path
import pandas as pd
import plotly.express as px
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
# SAMPLE_RANGE_NAME = 'Class Data!A2:E'

SAMPLE_SPREADSHEET_ID = '1Bzoa_q7h74_WpVEjOi5dOh1ae4uj3kSysY3Cxqb6Ehg'
SAMPLE_RANGE_NAME = 'Sheet1'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    # if not values:
    #     print('No data found.')
    # else:
    #     print('Name, Major:')
    #     for row in values:
    #         # # Print columns A and E, which correspond to indices 0 and 4.
    #         # print('%s, %s' % (row[0], row[4]))
    #
    #         # Print columns A and B
    #         print('%s, %s' % (row[0], row[1]))

    if not values:
        print('No data found. Exiting.')
        return

    # df = pd.DataFrame(data=values[1:], columns=['Question', 'CompletionDate', 'ProblemsSolved'])
    # df['CompletionDate'] = pd.to_datetime(df['CompletionDate'])
    # df['ProblemsSolved'] = pd.to_numeric(df['ProblemsSolved'])
    #
    # print(df.dtypes)
    #
    # fig = px.line(df, x='CompletionDate', y='ProblemsSolved')
    # fig.show()

    problems_solved_cache = {}
    for row in values[1:]:
        completion_date = row[1]
        problems_solved = row[2]

        problems_solved_cache[completion_date] = problems_solved

    df = pd.DataFrame(problems_solved_cache.items(), columns=['CompletionDate', 'ProblemsSolved'])
    df['CompletionDate'] = pd.to_datetime(df['CompletionDate'])
    df['ProblemsSolved'] = pd.to_numeric(df['ProblemsSolved'])

    print(df)

    fig = px.line(df, x='CompletionDate', y='ProblemsSolved')
    fig.show()


if __name__ == '__main__':
    main()
