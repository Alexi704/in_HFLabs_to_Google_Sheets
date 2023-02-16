from __future__ import print_function
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import requests
from bs4 import BeautifulSoup

content_api_information = ''
url_donor = 'https://confluence.hflabs.ru/pages/viewpage.action?pageId=1181220999'
SAMPLE_RANGE_NAME = 'API Code!A1:B20'


def get_information():
    global content_api_information

    response = requests.get(url=url_donor)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    result = soup.find('table', class_='confluenceTable')

    header_api_information = []
    for item in result.find_all('th', class_='confluenceTh'):
        header_api_information.append(item.text)

    content_api_information = []
    x = []
    for i, item in enumerate(result.find_all('td', class_='confluenceTd')):
        if i % 2 == 0:
            x.append(item.text)
        else:
            x.append(item.text)
            content_api_information.append(x)
            x = []

    content_api_information.insert(0, header_api_information)


def write_information():
    with open('data.txt', 'r', encoding='utf-8') as file:
        last_write = file.read()

    if content_api_information == '' or str(content_api_information) != last_write:
        with open('data.txt', 'w', encoding='utf-8') as file:
            file.write(f'{content_api_information}')
            print('Изменения в источнике! Обновляем данные в гугл доках!')
            return True
    else:
        print('Информация в первоисточнике НЕ изменялась. Можно спасть спокойно )))')


class GoogleSheet:
    SPREADSHEET_ID = '1zFZv2H3PLmrKT33cmB13EKKVS6pNIE0xb-HB3VQwhuU'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None

    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def update_range_values(self, range, values):
        data = [{
            'range': range,
            'values': values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID,
                                                                  body=body).execute()
        print('{0} cells updated.'.format(result.get('totalUpdatedCells')))


def main():
    get_information()
    if write_information():
        gs = GoogleSheet()
        test_range = SAMPLE_RANGE_NAME
        test_values = content_api_information
        gs.update_range_values(test_range, test_values)


if __name__ == '__main__':
    main()
