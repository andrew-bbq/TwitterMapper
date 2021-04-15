from os import listdir
from os.path import isfile, join
import openpyxl

onlyfiles = [f for f in listdir("Data") if isfile(join("Data", f))]

data_string = ""

for filename in onlyfiles:
    path = "./Data/"+filename
    if filename == "@Arbys_user_tweets.xlsx":
        continue
    wb_obj = openpyxl.load_workbook(path)
    sheet_obj = wb_obj.active
    for i, row in enumerate(sheet_obj.iter_rows(values_only=True)):
        try:
            if row[1][0:1] != "@" and row[1][0:2] != "RT" and row[1] != "Text":
                data_string += row[1] + "\n=======\n"
        except:
            continue

with open("training_data.txt", "w", encoding='utf-8') as outfile:
    outfile.write(data_string)
    outfile.close()