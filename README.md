# YNAB

## Author: Austin Traver

This program allows you to import CSV transactions from Apple directly into your YNAB account.

### Installation

Getting this application to work on your machine requires a few initial steps, outlined below:

0. Clone this repository, add its filepath as an element of the `PYTHONPATH` environment variable
1. Get a personal access token from the *Developer Settings* section in YNAB.
2. Assign the environment variable `YNAB_TOKEN` in your `.zshenv` file
3. Ensure your budget name on YNAB is `My Budget`
4. Ensure your Apple Card account on YNAB is named `Apple Card`

### Execution

* Uploading the transactions to YNAB automatically

    ```sh
    python -m ynab < ~/Downloads/march_transactions.csv
    ```
  
 * Converting the transactions into a YNAB-formatted CSV
 
    ```sh 
    python -m ynab -v < ~/Downloads/apple_card.csv
    ```
