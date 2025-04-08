#!/usr/bin/env python3
""" Holds utils that are used by the app """
import os
from typing import List
from random import shuffle
from win32com.client import Dispatch
from cryptography.fernet import Fernet
import xlrd
import xlwt

DICITIONARY_CSV_FILENAME = 'dictionary.xls'
OUTPUT_DATASET_FILENAME = 'data.xls'


def csv_to_list(decrypted_xls):
    """ converts a list """
    wb = xlrd.open_workbook(file_contents=decrypted_xls)
    sheet = wb.sheet_by_index(0)
    rw = []
    for row_idx in range(sheet.nrows):
        row = sheet.row_values(row_idx)
        print('=', row)
        rw.append(row)
    return rw


def word_exists(word):
    if os.path.exists('dataset/data.xls'):
        wb = xlrd.open_workbook('dataset/data.xls')
        sheet = wb.sheet_by_index(0)
        counter = 0
        for row_idx in range(1, sheet.nrows):
            if sheet.cell_value(row_idx, 1) == word:
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
CSV_HEADERS = ["ID", "Tigrigna", "English"]

if os.path.exists(DICITIONARY_CSV_FILENAME):
    WORDS = []
    wb = xlrd.open_workbook(DICITIONARY_CSV_FILENAME)
    sheet = wb.sheet_by_index(0)
    for row_idx in range(sheet.nrows):
        WORDS.append(sheet.row_values(row_idx))
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
    """ creates a xls file with the given headers """
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Sheet1")
    for i, header in enumerate(headers):
        ws.write(0, i, header)
    wb.save(filename)


def update_csv(filename: str, data: List[str]):
    """ appends a new row to an xls file"""
    if data and data[0] == 'Null':
        return

    if not os.path.exists(filename):
        create_csv(filename, CSV_HEADERS)

    wb = xlrd.open_workbook(filename, formatting_info=True)
    sheet = wb.sheet_by_index(0)
    rows = [sheet.row_values(i) for i in range(sheet.nrows)]

    rows.append(data)

    # Rewrite everything
    new_wb = xlwt.Workbook()
    new_ws = new_wb.add_sheet("Sheet1")
    for row_idx, row in enumerate(rows):
        for col_idx, cell in enumerate(row):
            new_ws.write(row_idx, col_idx, cell)
    new_wb.save(filename)


def dataset_count(filename: str) -> int:
    """ counts how many datasets are in an xls file"""
    if not os.path.exists(filename):
        create_csv(filename, CSV_HEADERS)

    wb = xlrd.open_workbook(filename)
    sheet = wb.sheet_by_index(0)
    return sheet.nrows - 1


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
