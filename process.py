import sqlite3
import requests
import sys

try:
    input = open("addresses.db")
except OSError as error:
    print("SQLite database addresses.db not found. Please run the import.py script to generate an address database. Review the README.md for more information.")

connection = sqlite3.connect('addresses.db')
cursor = connection.cursor()

