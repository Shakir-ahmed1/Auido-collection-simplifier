#!/usr/bin/env python3
""" Holds utils that are used by the app """
import csv
from typing import List
import os
from random import shuffle


DICITIONARY_CSV_FILENAME = 'dictionary.csv'
OUTPUT_DATASET_FILENAME = 'data.csv'
INDEX = 0
WORDS = [
    ('እሱ', 'he'),
    ('ኣለዎ', 'has'),
    ('ወርቂ', 'gold'),
    ('ይሰርሕ', 'does'),
]
CSV_HEADERS = ["Tigrigna", "English", "file_name"]

if os.path.exists(DICITIONARY_CSV_FILENAME):
    WORDS = []
    with open(DICITIONARY_CSV_FILENAME, 'r', encoding='utf-8') as file_obj:
        reader_obj = csv.reader(file_obj)
        for row in reader_obj:
            WORDS.append(row)
    shuffle(WORDS)


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


def update_csv(filename: str, data: List[str]):
    """ appends a new row to a csv file"""
    if not os.path.exists(filename):
        create_csv(filename, CSV_HEADERS)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        data = list(data)
        writer.writerow(data)


def dataset_count(filename: str) -> int:
    """ counts how many datasets are in a csv file"""
    datas = []
    if not os.path.exists(filename):
        create_csv(filename, CSV_HEADERS)
    with open(filename, 'r', encoding='utf-8') as file_obj:
        reader_obj = csv.reader(file_obj)
        for row in reader_obj:
            datas.append(row)
    return f'total words: {len(datas)}'
