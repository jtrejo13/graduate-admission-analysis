from bs4 import BeautifulSoup as soup
import pandas as pd
import re

file_path = './raw_data/page_{0}.html'
data_path = '../data/graduate.csv'

def processRow(index, row):
    print(row)
    return [index]

data = []
for i in range(1, 2):
    with open(file_path.format(i), 'r') as f:
        page = soup(f, 'html.parser')
        tables = page.findAll('table', id='my-table')
        for table in tables:
            rows = table.findAll('tr', class_=re.compile('row'))
            for row in range(1, 2):
                entry = processRow(i, rows[0])
                if len(entry) > 0:
                    data.append(entry)
    print('processing file {0}...'.format(i))

print(data)
