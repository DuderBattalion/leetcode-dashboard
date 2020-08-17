from __future__ import print_function
import pickle
import os.path
import pandas as pd
import plotly.express as px
import logging
from datetime import timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SAMPLE_SPREADSHEET_ID = '1Bzoa_q7h74_WpVEjOi5dOh1ae4uj3kSysY3Cxqb6Ehg'
SAMPLE_RANGE_NAME = 'Sheet1'


def main():
    values = get_values_from_google()
    if not values:
        print('No data found. Exiting.')
        return

    solved_progress_cache = init_solved_progress_cache(values)
    problems_per_day_cache = init_problems_per_day_cache(solved_progress_cache)

    # Display graphs
    show_trend_line(solved_progress_cache)
    show_problems_per_day(problems_per_day_cache)

    num_all_problems = 1500
    total_problems_solved = int(values[-1][2])
    num_days_passed = len(values) - 1  # Exclude first title row
    start_date = pd.to_datetime(values[1][1])
    problems_left = num_all_problems - total_problems_solved
    today_date = pd.to_datetime('now')

    print_expected_completion_date(num_all_problems, num_days_passed, start_date, total_problems_solved)
    print_desired_completion_date(problems_left, today_date)
    print_forecast_completion_date(problems_left, today_date)


def get_values_from_google():
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
    return values


def init_solved_progress_cache(values):
    solved_progress_cache = {}
    for row in values[1:]:
        completion_date = row[1]
        problems_solved = row[2]

        solved_progress_cache[completion_date] = problems_solved

    return solved_progress_cache


def init_problems_per_day_cache(solved_progress_cache):
    problems_per_day_cache = {}

    prev_day_problems = 0
    for key, val in solved_progress_cache.items():
        int_val = int(val)
        problems_per_day_cache[key] = int_val - prev_day_problems
        prev_day_problems = int_val

    return problems_per_day_cache


def show_trend_line(solved_progress_cache):
    """Shows a trend line for progress along total problems solved. Useful for visualizing
    rate of progress.
    """
    completion_vs_solved = pd.DataFrame(solved_progress_cache.items(), columns=['CompletionDate', 'ProblemsSolved'])
    completion_vs_solved['CompletionDate'] = pd.to_datetime(completion_vs_solved['CompletionDate'])
    completion_vs_solved['ProblemsSolved'] = pd.to_numeric(completion_vs_solved['ProblemsSolved'])
    fig = px.line(completion_vs_solved, x='CompletionDate', y='ProblemsSolved')
    fig.show()


def show_problems_per_day(problems_per_day_cache):
    """Plots a histogram that shows number of problems solved per day.
    """
    problems_per_day = pd.DataFrame(problems_per_day_cache.items(), columns=['CompletionDate', 'ProblemsPerDay'])
    problems_per_day['CompletionDate'] = pd.to_datetime(problems_per_day['CompletionDate'])
    problems_per_day['ProblemsPerDay'] = pd.to_numeric(problems_per_day['ProblemsPerDay'])
    problems_per_day_graph = px.bar(problems_per_day, x='CompletionDate', y='ProblemsPerDay')
    problems_per_day_graph.show()


def print_expected_completion_date(num_all_problems, num_days_passed, start_date, total_problems_solved):
    """Calculates the current progress trend and forecasts expected date all problems will be solved.
    """
    avg_problems_solved_per_day = total_problems_solved / num_days_passed
    num_days_all_problems = num_all_problems / avg_problems_solved_per_day
    expected_completion_date_all_problems = start_date + timedelta(days=num_days_all_problems)
    print(f'Average problems per day: {avg_problems_solved_per_day}')
    print(f'Expected completion date: {expected_completion_date_all_problems}')
    print()


def print_desired_completion_date(problems_left, today_date):
    """Given a desired completion date, this function prints the number of problems
    that would need to be solved per day solve all problems by the desired date.
    """
    desired_completion_date = pd.to_datetime('2020-11-30')
    days_left = desired_completion_date - today_date
    desired_problems_per_day = problems_left / days_left.days
    print(f'Desired completion date: {desired_completion_date}')
    print(f'Numbers of problems per day requird: {desired_problems_per_day}')
    print()


def print_forecast_completion_date(problems_left, today_date):
    """Given an estimate of number of problems expected to be solved in a day,
    this function prints the expected completion date when all problems will be solved.
    """
    estimated_problems_per_day = 10
    forecasted_days_required = problems_left / estimated_problems_per_day
    forecasted_completion_date = today_date + timedelta(days=forecasted_days_required)
    print(f'Estimated number of problems solved per day: {estimated_problems_per_day}')
    print(f'Forecasted completion date: {forecasted_completion_date}')


if __name__ == '__main__':
    main()
