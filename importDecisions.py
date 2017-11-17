import urllib.request, csv
from datetime import *


months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

def getAllDecisions(url, pnp, earlyDate):
    decInfo = {}
    response = urllib.request.urlopen(url)
    html = str(response.read())
    start_page = html.find('Dockets - PACER System')
    html = html[start_page:]
    while True:

        if html.find('Filed') == -1:
            break
        start_date = html.find('Filed')
        end_date = html.find(',', start_date)
        date = html[start_date + 6:end_date]
        checkDate = datetime.strptime(date, "%m/%d/%Y")
        if earlyDate >= checkDate:
            html = html[end_date:]
            continue
        start_docket = html.find('No.', end_date)
        end_docket = html.find('<br', start_docket)
        docket = html[start_docket:end_docket]
        start_target = html.find('href=', end_docket)
        end_target = html.find('target', start_target)
        target = html[start_target + 6:end_target - 2]
        start_name = html.find('blank', end_target)
        end_name = html.find('a>', start_name)
        name = html[start_name + 7:end_name - 2]
        if name[-3:] == 'v. ':
            name = name[:-4]
            if name[:5].upper() != 'IN RE':
                name = 'In Re: ' + name
        start_court = html.find('r />', end_name)
        end_court = html.find('<br', start_court)
        court = html[start_court + 4:end_court]
        Inf = []
        Inf.extend([name, target, court, docket, 'FALSE', '', '', date])
        if pnp == 'p':
            Inf[6] = 'Precedential'
        if pnp == 'np':
            Inf[6] = 'Non-Precedential'
        mon = int(date[:2])
        Inf[5] = months[mon - 1]
        html = html[end_court:]
        decInfo[target] = Inf
    return decInfo

def main():
    earlyDate = input('Enter the earliest desired date for decisions MM/DD/YYYY: ')
    earlyDate = datetime.strptime(earlyDate, "%m/%d/%Y")
    print("Retrieving Precedential Opinions...")
    precedentials = getAllDecisions('http://www2.ca3.uscourts.gov/recentop/week/recprec.htm', 'p', earlyDate)
    print("Retrieving Non-Precedential Opinions...")
    nonprecedentials = getAllDecisions('http://www2.ca3.uscourts.gov/recentop/week/recnonprec.htm', 'np', earlyDate)
    sheetName = '3rdCir ' + str(earlyDate)[:10] + '.csv'
    print("Writing to filename " + sheetName)
    with open(sheetName, 'w', newline='') as csvfile:
        courtWriter = csv.writer(csvfile, delimiter="|")
        for k in precedentials:
            courtWriter.writerow(precedentials[k])
        for k in nonprecedentials:
            courtWriter.writerow(nonprecedentials[k])
            
if __name__ == '__main__':
    main()
