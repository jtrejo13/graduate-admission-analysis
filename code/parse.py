from bs4 import BeautifulSoup as soup
from IPython.core.debugger import Tracer
import pandas as pd
import re

file_path = './raw_data/page_{0}.html'
data_path = '../data/graduate.csv'

def processAcceptance(elems):
    for elem in elems:
        pass
        # print(elem)

def processRow(index, row):

    elems = row.find_all('td')

    if len(elems) != 6:
        Tracer()()

    # Get University name
    try:
        uni_name = elems[0].get_text()
    except:
        Tracer()()

    # Get Status
    try:
        status = elems[3].get_text()
    except:
        Tracer()()

    # Get Comment
    try:
        comment_entry = (elems[5].find_all('li'))
        comment = comment_entry[1].get_text()
    except:
        Tracer()()

    # Get Admission Date
    try:
        date_str = elems[4].get_text()
        print(date_str)
        _, _, y = date_str.split(" ")
        year = int(y)
    except:
        Tracer()()

    #_data = elems[1].get_text()
    #processAcceptance(elems[2])

    return [uni_name, status, comment, year]

data = []
for i in range(1, 2):
    with open(file_path.format(i), 'r') as f:
        page = soup(f, 'html.parser')
        tables = page.find_all('table', id='my-table')
        for table in tables:
            rows = table.find_all('tr', class_=re.compile('row'))
            for row in range(1, 2):  # for row in rows
                entry = processRow(i, rows[0])
                if len(entry) > 0:
                    data.append(entry)
    print('processing file {0}...'.format(i))

print(data)
