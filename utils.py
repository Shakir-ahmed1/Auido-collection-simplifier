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
from config import student_id

DICITIONARY_CSV_FILENAME = 'data.csv'
OUTPUT_DATASET_FILENAME = 'data.xls'
DURATION_COLUMN_NUMBER = 3

if student_id not in [198, 271, 50, 235, 267, 254, 173]:
    raise Exception('WARNING: Set Correct User id first')
skipped_words_counter = 0
last_id = ''

starting_mapper = {
    198: 1,
    271: 80001,
    50: 160001,
    235: 240001,
    267: 320001,
    254: 400001,
    173: 480001
}

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
    global skipped_words_counter
    global last_id
    path = 'dataset/data.xls'
    if not os.path.exists(path):
        return f"tig_{starting_mapper[student_id]:09}"

    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    if sheet.nrows <= 1:
        return f"tig_{starting_mapper[student_id]:09}"  # No data rows yet

    # Get the last row's ID (assuming it's in the first column)
    last_row_id = str(sheet.cell_value(sheet.nrows - 1, 0)).strip()
    if last_row_id == last_id:
        skipped_words_counter += 1
    else:
        skipped_words_counter = 0
    splited = last_row_id.split('_')
    print("Splited", splited)
    label, id = splited
    new_id = f"{label}_{(int(id) + skipped_words_counter + 1):09}"
    last_id = last_row_id
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
    with open(DICITIONARY_CSV_FILENAME, 'r', encoding='utf-8-sig') as file_obj:
        reader_obj = csv.reader(file_obj)
        for row in reader_obj:
            WORDS.append(row)


def word_generator() -> List[str]:
    """ generates word for the user to read

    checks the last row's id
    adds 1
    returns the word using the add index


    """
    new_id = get_next_id()
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
