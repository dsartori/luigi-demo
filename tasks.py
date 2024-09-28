import luigi
import requests
import sqlite3
from datetime import date
import logging
import csv

logger = logging.getLogger('luigi-interface')

class FetchRates(luigi.Task):
    def output(self):
        return luigi.LocalTarget(f'/tmp/{self.task_id}.txt')
    
    def run(self):
        currencies = ['FXUSDCAD', 'FXMXNCAD']  
        base_url = "https://www.bankofcanada.ca/valet/observations"
        for currency in currencies:
            url = f"{base_url}/{currency}/json"
            response = requests.get(url)
            data = response.json()

            conn = sqlite3.connect('expenses.db')
            cursor = conn.cursor()

            if 'observations' not in data:
                logger.error(f"Error fetching data for {currency[2:5]}: {data}")
                continue

            new_observations = [obs for obs in data['observations'] if not self.observation_exists(obs, cursor)]

            for obs in new_observations:
                for currency in currencies:
                    if currency in obs:
                        date = obs['d']
                        rate = obs[currency]['v']
                        cursor.execute("INSERT OR IGNORE INTO exchange_rate (currency, date, rate) VALUES (?, ?, ?)", (currency[2:5], date, rate))

            conn.commit()
            conn.close()
            
        with self.output().open('w') as f:
            f.write(f'/tmp/{self.task_id}.txt')

    def observation_exists(self, obs, cursor):
        currency = obs['d']
        date = obs['d']
        cursor.execute("SELECT COUNT(1) FROM exchange_rate WHERE currency = ? AND date = ? LIMIT 1", (currency, date))
        record_exists = cursor.fetchone()[0] > 0
        return record_exists

    def get_existing_data(self, cursor):
        cursor.execute("SELECT currency, date, rate FROM exchange_rate")
        return [row for row in cursor.fetchall()]

class GenerateReport(luigi.Task):
    def output(self):
        return luigi.LocalTarget('output/expense_report.csv')

    def requires(self):
        return ImportExpenses()

    def run(self):
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                e.employee as [Employee], 
                e.exp_date as [Date], 
                e.currency as [Transaction Currency], 
                e.amount as [Amount],
                (x.rate * e.amount) as [CAD Amount],
                e.description as [Description]  
            FROM 
                expenses e
            INNER JOIN 
                exchange_rate x ON e.currency = x.currency AND e.exp_date = x.date
        """)
        expenses = cursor.fetchall()

        with open('output/expense_report.csv', 'w', newline='') as csvfile:
            fieldnames = ['Employee', 'Date', 'Transaction Currency', 'Amount', 'CAD Amount', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for expense in expenses:
                writer.writerow({
                    'Employee': expense[0],
                    'Date': expense[1],
                    'Transaction Currency': expense[2],
                    'Amount': expense[3],
                    'CAD Amount': expense[4],
                    'Description': expense[5]
                })

        conn.commit()
        conn.close()


class ImportExpenses(luigi.Task):
    def output(self):
        return luigi.LocalTarget(f'/tmp/{self.task_id}.txt')
    
    def requires(self):
        return FetchRates()

    def run(self):
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        
        exchange_rate_data = self.get_expense_data(cursor)
        for row in exchange_rate_data:
            name, date, description, currency, amount  = row[0], row[1], row[2], row[3], row[4] # name,date,description,currency,amount
            cursor.execute("INSERT INTO expenses (employee, exp_date, currency, amount, description) VALUES (?, ?, ?, ?, ?)", (name, date, currency, amount, description))
        conn.commit()
        conn.close()

    def get_expense_data(self, cursor):
        exchange_rate_data = []
        with open('demo_data/fake_expense_data.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['name']
                date = row['date']
                description = row['description']
                currency = row['currency']
                amount = float(row['amount'])
                exchange_rate_data.append((name, date, description, currency, amount))

        with self.output().open('w') as f:
            f.write(f'/tmp/{self.task_id}.txt')

        return exchange_rate_data