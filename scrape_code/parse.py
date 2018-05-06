# @Author: Juan Trejo
# @Date:   2018-03-28T17:17:44-05:00
# @Last modified by:   jtrj13
# @Last modified time: 2018-05-02T14:21:17-05:00


from bs4 import BeautifulSoup as soup
# from IPython.core.debugger import Tracer
import pandas as pd
import re

file_path = './raw_data/page_{0}.html'
data_path = '../data/graduate.csv'

DEGREE = [
  (' mfa', 'Other'),
  (' m eng', 'Masters'),
  (' meng', 'Masters'),
  (' m.eng', 'Masters'),
  (' masters', 'Masters'),
  (' phd', 'PhD'),
  (' mba', 'Other'),
  (' other', 'Other'),
  (' edd', 'Other'),
]

errlog = {'major': [], 'gpa': [], 'general': []}

def processScores(index, elems):
    """
    Code source: https://github.com/deedy/gradcafe_data/blob/master/cs/parse.py
    """

    gpafin, grev, grem, grew, new_gre, sub = None, None, None, None, None, None
    if elems:
      gre_text = elems.get_text()
      gpa = re.search('Undergrad GPA: ((?:[0-9]\.[0-9]{1,2})|(?:n/a))', gre_text)
      general = re.search('GRE General \(V/Q/W\): ((?:1[0-9]{2}/1[0-9]{2}/(?:(?:[0-6]\.[0-9]{2})|(?:99\.99)|(?:56\.00)))|(?:n/a))', gre_text)
      new_gref = True

      if gpa:
        gpa = gpa.groups(1)[0]
        if not gpa == 'n/a':
          try:
            gpafin = float(gpa)
          except:
            print('Tracer()()')
      else:
        errlog['gpa'].append((index, gre_text))
      if not general:
        general = re.search('GRE General \(V/Q/W\): ((?:[2-8][0-9]0/[2-8][0-9]0/(?:(?:[0-6]\.[0-9]{2})|(?:99\.99)|(?:56\.00)))|(?:n/a))', gre_text)
        new_gref = False

      if general:
        general = general.groups(1)[0]
        if not general == 'n/a':
          try:
            greparts = general.split('/')
            if greparts[2] == '99.99' or greparts[2] == '0.00' or greparts[2] == '56.00':
              grew = None
            else:
              grew = float(greparts[2])
            grev = int(greparts[0])
            grem = int(greparts[1])
            new_gre = new_gref
            if new_gref and (grev > 170 or grev < 130 or grem > 170 or grem < 130 or (grew and (grew < 0 or grew > 6))):
              errlog['general'].append((index, gre_text))
              grew, grem, grev, new_gre = None, None, None, None
            elif not new_gref and (grev > 800 or grev < 200 or grem > 800 or grem < 200 or (grew and (grew < 0 or grew > 6))):
              errlog['general'].append((index, gre_text))
              grew, grem, grev, new_gre = None, None, None, None
          except Exception as e:
            print('Tracer()()')
      else:
        errlog['general'].append((index, gre_text))

    # print (gpafin, grev, grem, grew, new_gre)
    return (gpafin, grev, grem, grew, new_gre)


def processRow(index, row):

    elems = row.find_all('td')

    if len(elems) != 6:
        print('Tracer()()')

    # Get Decision\
    descision_txt = elems[2].get_text().lower()
    try:
        decision = None
        if 'accepted' in descision_txt:
            decision = 'Accepted'
        elif 'rejected' in  descision_txt:
            decision = 'Rejected'
        else:
            return []
    except:
        print('Tracer()()')

    # Get University name
    try:
        uni_txt = None
        uni_txt = elems[0].get_text()
        university = re.sub("\xa0", "", uni_txt)
    except:
        print('Tracer()()')

    # Get Major
    try:
        major = None
        major_txt = elems[1].get_text().lower()
        if 'computer science' in major_txt:
            major = 'CS'
        else:
            major = 'Other'
            errlog['major'].append((index, row))
        # Get degree (PhD, MS, etc)
        degree = None
        for prog, val in DEGREE:
            if prog in major_txt:
                degree = val
                break
            else:
                degree = 'Other'
    except:
        print('Tracer()()')

    # Get Scores
    scores_elem = elems[2].find(class_='extinfo')
    # processScores(scores_elem)
    gpafin, grev, grem, grew, new_gre = processScores(index, scores_elem)
    # gpafin, grev, grem, grew, new_gre = None, None, None, None, None

    # Get Status (A, U, I)
    try:
        status = elems[3].get_text()
    except:
        print('Tracer()()')

    # Get Comment
    try:
        comment = None
        comment_entry = (elems[5].find_all('li'))
        comment = comment_entry[1].get_text()
    except:
        print('Tracer()()')

    # Get Admission Date
    try:
        year = None
        date_str = elems[4].get_text()
        _, _, y = date_str.split(" ")
        year = int(y)
    except:
        print('Tracer()()')

    return [university, major, degree, decision, status, year, gpafin, grev, grem, grew, new_gre]

data = []
for i in range(1, 147):
    with open(file_path.format(i), 'r') as f:
        page = soup(f, 'html.parser')
        tables = page.find_all('table', id='my-table')
        for table in tables:
            rows = table.find_all('tr', class_=re.compile('row'))
            count = 1
            for row in rows:  # for row in rows
                count = count + 1
                entry = processRow(i, row)
                if len(entry) > 0:
                    print('page:{page}, row:{row}'.format(page=i, row=count, uni=entry[0]))
                    data.append(entry)
    print('processing file {file}...'.format(file=i))

df = pd.DataFrame(data)
df.to_csv('cs_data.csv')
