#!/usr/bin/env python3
""" Holds utils that are used by the app """
import os
from typing import List
from random import shuffle
from win32com.client import Dispatch
from cryptography.fernet import Fernet
import xlrd
import xlwt
import csv

DICITIONARY_CSV_FILENAME = 'dictionary.xls'
OUTPUT_DATASET_FILENAME = 'data.xls'
DURATION_COLUMN_NUMBER = 3


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


# def word_exists(word):
#     if os.path.exists('dataset/data.xls'):
#         wb = xlrd.open_workbook('dataset/data.xls')
#         sheet = wb.sheet_by_index(0)
#         counter = 0
#         for row_idx in range(1, sheet.nrows):
#             if sheet.cell_value(row_idx, 1) == word:
#                 return True
#             counter += 1
#         if counter >= 600:
#             return True
#     return False


def get_next_id():
    """Returns the index in WORDS where the last recorded word ID is found, or -1 if not found."""
    path = 'dataset/data.xls'
    if not os.path.exists(path):
        return -1

    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    if sheet.nrows <= 1:
        return -1  # No data rows yet

    # Get the last row's ID (assuming it's in the first column)
    last_row_id = str(sheet.cell_value(sheet.nrows - 1, 1)).strip()

    label, id = last_row_id.split('_')
    new_id = f"{label}_{(int(id) + 1):09}"
    return new_id


WORDS = [
    ('እሱ', 'he'),
    ('ኣለዎ ', 'ሓድሽ ወተሃደራዊ እዚ እቶም ኣብ መግለጺ መንግስቲ ክልል ትግራይ ርእይቶኦም ክህቡ ዝተሓተቱ ነባራት ወተሃደራዊ ኪኢላታት ኣብቲ ናይ መንነነት ሕቶ ዝለዓለሉ ከባቢ ወልቃይት ዝሕቆፍ ሰሜን ምዕራብ ዝተሰምየ ሓድሽ ወተሃደራዊ እዚ ምጥያስ፡ ነቲ ክልል ትግራይ ምስ ሱዳን ዘራኽባ ዶብ ንምዕጻውን ምስ ሓይልታት ደገ ቀጥታዊ ርክብ ንምግባርን ክኸውን ከም ዝኽእል ይዛረቡ።'),
    ('ወርቂ', 'gold'),
    ('ስራሕ', 'work'),
]
# CSV_HEADERS = ["ID", "Tigrigna", "English"]
CSV_HEADERS = ['id', 'text', 'path', 'duration', 'voice_name']

if os.path.exists(DICITIONARY_CSV_FILENAME):
    WORDS = []
    wb = xlrd.open_workbook(DICITIONARY_CSV_FILENAME)
    sheet = wb.sheet_by_index(0)
    for row_idx in range(sheet.nrows):
        WORDS.append(sheet.row_values(row_idx))
    shuffle(WORDS)


def word_generator() -> List[str]:
    """ generates word for the user to read

    checks the last row's id
    adds 1
    returns the word using the add index


    """
    new_id = get_next_id()
    print("Word generator", WORDS)
    found_word = next((el for el in WORDS if el[0] == new_id), None)
    if not found_word:
        return ['Null', 'Null']
    return found_word


def create_xls(filename: str, headers: List[str]):
    """ creates a xls file with the given headers """
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Sheet1")
    for i, header in enumerate(headers):
        ws.write(0, i, header)
    wb.save(filename)


def update_xls(filename: str, data: List[str]):
    """ appends a new row to an xls file"""
    if data and data[0] == 'Null':
        return

    if not os.path.exists(filename):
        create_xls(filename, CSV_HEADERS)

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
        create_xls(filename, CSV_HEADERS)

    wb = xlrd.open_workbook(filename)
    sheet = wb.sheet_by_index(0)
    return sheet.nrows - 1


def dataset_total_duration(filename: str) -> float:
    """Sums all values in column 3 (index 2) of the dataset file."""
    if not os.path.exists(filename):
        create_xls(filename, CSV_HEADERS)

    wb = xlrd.open_workbook(filename)
    sheet = wb.sheet_by_index(0)

    total = 0.0
    for row_idx in range(1, sheet.nrows):  # Skip header row
        try:
            value = float(sheet.cell_value(row_idx, DURATION_COLUMN_NUMBER))
            total += value
        except ValueError:
            continue  # skip rows where value isn't a number

    return total


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


def convert_xls_to_csv(xls_filename: str, csv_filename: str):
    """ Converts .xls file to .csv with utf-8-sig encoding """
    if not os.path.exists(xls_filename):
        print(f"File not found: {xls_filename}")
        return

    wb = xlrd.open_workbook(xls_filename)
    sheet = wb.sheet_by_index(0)

    with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        for row_idx in range(sheet.nrows):
            row = sheet.row_values(row_idx)
            writer.writerow(row)


def time_displayer(seconds):
    """Returns a duration in HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"
