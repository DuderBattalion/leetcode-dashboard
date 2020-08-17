from __future__ import print_function
import pickle
import os.path
import pandas as pd
import plotly.express as px
from datetime import timedelta
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

    # completion_vs_solved = pd.DataFrame(data=values[1:], columns=['Question', 'CompletionDate', 'ProblemsSolved'])
    # completion_vs_solved['CompletionDate'] = pd.to_datetime(completion_vs_solved['CompletionDate'])
    # completion_vs_solved['ProblemsSolved'] = pd.to_numeric(completion_vs_solved['ProblemsSolved'])
    #
    # print(completion_vs_solved.dtypes)
    #
    # fig = px.line(completion_vs_solved, x='CompletionDate', y='ProblemsSolved')
    # fig.show()

    # Total Number of problems solved tagged by date
    solved_progress_cache = {}

    # Problems solved per day
    problems_per_day_cache = {}

    for row in values[1:]:
        completion_date = row[1]
        problems_solved = row[2]

        solved_progress_cache[completion_date] = problems_solved

    prev_day_probs = 0
    for key, val in solved_progress_cache.items():
        int_val = int(val)
        problems_per_day_cache[key] = int_val - prev_day_probs
        prev_day_probs = int_val

    # Progress Trend Line
    completion_vs_solved = pd.DataFrame(solved_progress_cache.items(), columns=['CompletionDate', 'ProblemsSolved'])
    completion_vs_solved['CompletionDate'] = pd.to_datetime(completion_vs_solved['CompletionDate'])
    completion_vs_solved['ProblemsSolved'] = pd.to_numeric(completion_vs_solved['ProblemsSolved'])

    fig = px.line(completion_vs_solved, x='CompletionDate', y='ProblemsSolved')
    fig.show()

    # Problems solved per day
    problems_per_day = pd.DataFrame(problems_per_day_cache.items(), columns=['CompletionDate', 'ProblemsPerDay'])
    problems_per_day['CompletionDate'] = pd.to_datetime(problems_per_day['CompletionDate'])
    problems_per_day['ProblemsPerDay'] = pd.to_numeric(problems_per_day['ProblemsPerDay'])

    problems_per_day_graph = px.bar(problems_per_day, x='CompletionDate', y='ProblemsPerDay')
    problems_per_day_graph.show()

    # Expected date of completion
    num_all_problems = 1500
    total_problems_solved = int(values[-1][2])
    num_days_passed = len(values) - 1  # Exclude first title row
    start_date = pd.to_datetime(values[1][1])

    avg_problems_solved_per_day = total_problems_solved / num_days_passed
    num_days_all_problems = num_all_problems / avg_problems_solved_per_day
    expected_completion_date_all_problems = start_date + timedelta(days=num_days_all_problems)

    print(f'Average problems per day: {avg_problems_solved_per_day}')
    print(f'Expected completion date: {expected_completion_date_all_problems}')


if __name__ == '__main__':
    main()
