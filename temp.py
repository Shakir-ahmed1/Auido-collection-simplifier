# filename = 'data.csv'
# CSV_HEADERS = ["id", "text"]

# import csv
# import os
# from typing import List

# def create_csv(filename: str, headers: List[str]):
#     """ creates a csv file with the given headers """
#     with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
#         writer = csv.writer(file)
#         writer.writerow(headers)


# def update_csv(filename: str, data: List[str]):
#     """ appends a new row to a csv file"""
#     if data and data[0] == 'Null':
#         return
#     if not os.path.exists(filename):
#         create_csv(filename, CSV_HEADERS)
#     with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
#         writer = csv.writer(file)
#         data = list(data)
#         writer.writerow(data)


# create_csv(filename,CSV_HEADERS)

# with open('output.txt', encoding='utf-8') as input:
#     lines = input.read().split('\n')
#     output_lines = []
#     counter = 0
#     for line in lines:
#         counter += 1 
#         if counter % 1000 == 0:
#             print("Progress: ", counter, '/', len(lines))
#         update_csv(filename, [f"tig_{counter:09}", line])
        
