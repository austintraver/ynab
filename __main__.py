import webbrowser
from datetime import datetime
from sys import exit
from json import load, dumps
from os import getenv
from sys import stdin, stdout, stderr, argv
from csv import DictReader, DictWriter
from urllib.request import Request, urlopen

from argparse import ArgumentParser, FileType

parser = ArgumentParser(
    prog='ynab',
    usage='%(prog)s [CSV_FILE]',
    description='%(prog)s: a backtesting platform'
)
parser.add_argument(
    "-v",
    "--verbose",
    dest='verbose',
    action='store_true',
    help="option to print CSV to stdout"
)
options = parser.parse_args()

endpoint = 'https://api.youneedabudget.com/v1/budgets/last-used'


def get_account_id():
    account_request = Request(
        url=f'{endpoint}/accounts'
    )

    account_request.add_header('Authorization', f'Bearer {api_token}')

    account_response = urlopen(account_request)
    accounts = load(account_response)['data']['accounts']

    ynab_account_id = None

    for account in accounts:
        if account['name'] == 'Apple Card':
            ynab_account_id = account['id']

    if ynab_account_id is None:
        raise (ValueError('ynab: unable to find account "Apple Card"\n'))

    return ynab_account_id


if (api_token := getenv('YNAB_TOKEN')) is None:
    exit('ynab: expected environment variable ${YNAB_TOKEN}')

# Force input to be provided via file redirection
if stdin.isatty():
    if len(argv) == 1:
        stderr.writelines([
            'ynab: please supply the CSV file via standard input\n',
            '\tusage: `ynab < ./Downloads/apple.csv > ~/ynab.csv`\n'
        ])
        exit(2)

apple_csv = DictReader(
    f=stdin,  # The file to read from (standard input)
    fieldnames=None,  # Assume the CSV file's first row contains the field names
    dialect='unix',  # Specify the encoding method for the CSV file
)

expected_fields = [
    'Transaction Date',
    'Clearing Date',
    'Description',
    'Merchant',
    'Category',
    'Type',
    'Amount (USD)'
]

if apple_csv.fieldnames != expected_fields:
    stderr.writelines([
        'ynab: problem reading CSV header row\n',
        f'\texpected:\t{expected_fields}\n',
        f'\treceived:\t{apple_csv.fieldnames}\n'
    ])
    exit(1)

ynab_csv = DictWriter(
    f=stdout,  # The file to write to (standard output)
    fieldnames=['Date', 'Payee', 'Memo', 'Amount'],  # Specify the field names
    dialect='unix',  # Specify the encoding method for the CSV file
)

csv_transactions = list()

api_transactions = list()

account_id = get_account_id()

# Create a list of api_transactions
for row in apple_csv:

    # Format the date from 2020/01/13 to 2020-01-13
    date = datetime.strptime(
        row['Transaction Date'], '%m/%d/%Y'
    ).date().isoformat()

    # Write an entry to the CSV file
    csv_transactions.append({
        'Date': date,
        'Payee': row['Merchant'],
        'Amount': '{:.2f}'.format(float(row['Amount (USD)']) * -1),
        'Memo': ''
    })

    # Store the next transaction as a dictionary, append it to the list
    api_transactions.append({
        'account_id': account_id,
        'date': date,
        'payee_name': row['Merchant'],
        'cleared': 'cleared',
        'approved': False,
        'amount': int(float(row['Amount (USD)']) * -1_000)
    })


if options.verbose:
    # Write the header row to the CSV file (the field names)
    ynab_csv.writeheader()
    # Write each transaction in the list to a row in the CSV file
    ynab_csv.writerows(csv_transactions)

data = {
    'transactions': api_transactions
}

transaction_request = Request(
    headers={
        'Authorization': f'Bearer {api_token}',
        "Content-Type": 'application/json',
    },
    url=f'{endpoint}/transactions',
    data=dumps(data).encode('utf-8')
)

transaction_response = urlopen(transaction_request)
# print(f'ynab: successfully imported {len(api_transactions)} into YNAB')

# Open YNAB for the user on their default web browser
webbrowser.open('https://app.youneedabudget.com')
