#!/usr/bin/env python3
""" Holds utils that are used by the app """
import csv
from typing import List


WORDS = [
    ('እሱ', 'he'),
    ('ኣለዎ', 'has'),
    ('ወርቂ', 'gold'),
    ('ይሰርሕ', 'does'),
]
INDEX = 0
DEBUG = False


def word_generator() -> List[str]:
    """ generates word for the user to read"""
    global INDEX
    INDEX += 1
    return WORDS[INDEX % len(WORDS)]


def create_csv(filename: str, headers: List[str]):
    """ creates a csv file with the given headers """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
    if DEBUG:
        print(f"CSV file '{filename}' created successfully.")


def update_csv(filename: str, data: List[str]):
    """ appends a new row to a csv file"""
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        data = list(data)
        writer.writerow(data)
    if DEBUG:
        print("Data added to CSV file => ", data)
