#!/usr/bin/env python3
""" Holds utils that are used by the app """
import csv
from typing import List
import os
from random import shuffle
from win32com.client import Dispatch
from cryptography.fernet import Fernet

DICITIONARY_CSV_FILENAME = '_exlib.dsd'
OUTPUT_DATASET_FILENAME = 'data.csv'
numbers = b'R7FhWrWdE6fenQ8aucOyYCZSAHD_oK7gsVkLvFw1WFo='


def decrypt_file(key, encrypted_filename):
    """ decryptes an encrypted file using the given key and returns string"""
    with open(encrypted_filename, 'rb') as f:
        encrypted_data = f.read()
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    return ''.join(decrypted_data.decode('utf-8')).strip()


def csv_to_list(decrypted_csv):
    """ converts a list """
    all_words = [d.split('#') for d in decrypted_csv.split('\r\n')]
    return all_words


def word_exists(word):
    if os.path.exists('dataset/data.csv'):
        with open('dataset/data.csv', encoding='utf-8') as file:
            content = csv.reader(file)
            counter = 0
            for b in content:
                if b[0] == word:
                    return True
                counter += 1
            if counter >= 600:
                return True
    return False


INDEX = 0
WORDS = [
    ('እሱ', 'he'),
    ('ኣለዎ', 'has'),
    ('ወርቂ', 'gold'),
    ('ስራሕ', 'work'),
]
CSV_HEADERS = ["Tigrigna", "English", "file_name"]

if os.path.exists(DICITIONARY_CSV_FILENAME):
    WORDS = []
    decrypted_string = decrypt_file(numbers, DICITIONARY_CSV_FILENAME)
    WORDS = csv_to_list(decrypted_string)
    shuffle(WORDS)


def word_generator() -> List[str]:
    """ generates word for the user to read"""
    global INDEX
    INDEX += 1
    len_word = len(WORDS)
    while INDEX < len_word and word_exists(WORDS[INDEX][0]):
        INDEX += 1
        if INDEX >= len_word:
            return ['Null', 'Null']
    if INDEX >= len_word:
        return ['Null', 'Null']
    return WORDS[INDEX]


def create_csv(filename: str, headers: List[str]):
    """ creates a csv file with the given headers """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)


def update_csv(filename: str, data: List[str]):
    """ appends a new row to a csv file"""
    if data and data[0] == 'Null':
        return
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
    return len(datas) - 1


def create_shortcut(target_path, shortcut_name):
    """ creates a shortcut for target_path using shortcut_name in desktop"""
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    shortcut_path = os.path.join(desktop_path, shortcut_name + '.lnk')

    if not os.path.exists(shortcut_path):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = os.path.abspath(target_path)
        shortcut.WorkingDirectory = os.path.dirname(
            os.path.abspath(target_path))
        shortcut.save()
