from lxml import html
import requests
from time import sleep
import json
import argparse
from collections import OrderedDict
from time import sleep
from pandas_datareader import data
import pandas as pd
import quandl
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

quandl.ApiConfig.api_key = 'FsgLTYcgU6NwGbVptrDD'

def parse(ticker):
    # first link
    url = "http://finance.yahoo.com/quote/%s/"%(ticker) #create url to scrape from
    response = requests.get(url, verify=False) # false = ignore verifying the SSL certficate
    print ("Parsing %s"%(url))
    sleep(4) # wait for request to come back
    parser = html.fromstring(response.text) # get text html div
    
    summary_table = parser.xpath('//-contains(@data-test,"summary-table")]//tr') # get info from div with table in it
    summary_data = OrderedDict() # basically a dictionary that remembers the order contents are added,

    # second link
    other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(ticker)
    # the link above takes in the stock ticker as an argument {0}
    # try the filled in tesla one below to see what the json looks like:
    # https://query2.finance.yahoo.com/v10/finance/quoteSummary/tsla?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com
   
   
    summary_json_response = requests.get(other_details_json_link, verify=False) # summary_json is a response object

    try: # only extract something when its a valid ticker/url
        json_loaded_summary =  json.loads(summary_json_response.text)
        #print (json.dumps(json_loaded_summary, indent=4, sort_keys=True)) # print out json from webscrapped data

        #parse data
        y_Target_Est = json_loaded_summary["quoteSummary"]["result"][0]["financialData"]["targetMeanPrice"]['raw']
        earnings_list = json_loaded_summary["quoteSummary"]["result"][0]["calendarEvents"]['earnings']
        eps = json_loaded_summary["quoteSummary"]["result"][0]["defaultKeyStatistics"]["trailingEps"]['raw']
        # quartly = json_loaded_summary["quoteSummary"]["result"][0]["earnings"]["financialsChart"]["quarterly"]["earnings"]["fmt"]
        
        datelist = []
        for i in earnings_list['earningsDate']: # parse earnings data
            datelist.append(i['fmt'])
        earnings_date = ' to '.join(datelist)
        for table_data in summary_table:
            raw_table_key = table_data.xpath('.//td[contains(@class,"C(black)")]//text()') #extract title information from table
            #print(raw_table_key)
            raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()') #extract value information from table
            table_key = ''.join(raw_table_key).strip()  # getting elements like PE ratio and beta
            table_value = ''.join(raw_table_value).strip()
            summary_data.update({table_key:table_value}) # add to data in json form ":"
        
        summary_data.update({'1y Target Est':y_Target_Est,'EPS (TTM)':eps,'Earnings Date':earnings_date,'ticker':ticker,'url':url})
        return summary_data

    except:#invalid stock ticker
        print ("Failed to parse json response")
        return {"error":"Failed to parse json response"}


def quandl_api(userticker,scraped_data):
    tickers = [userticker];
    # api call to quandl, gte and lte are data bounds
    data = quandl.get_table('WIKI/PRICES', ticker = tickers,
                                qopts = { 'columns': ['ticker', 'date', 'adj_close'] },
                                date = { 'gte': '2018-01-19', 'lte': '2018-10-20' },
                                paginate=True)
    print(data.head(1))
    # get most recent entry
    onedata=data.head(1)
    onedata = onedata.reset_index()
    lastdate = onedata[['date'][0]]
    lastdatevalue = lastdate[0]
    lastclosing = onedata[['adj_close'][0]]
    lastclosingvalue = float(lastclosing[0])
    
    
    #convert date to human readable format
    readabledate = "{:%B %d, %Y}".format(lastdatevalue)

    # extract last closing of stock and conver to number
    stripcomma = scraped_data["Previous Close"]
    stripcomma = stripcomma.replace(',' , '')
    currentclose = float(stripcomma)

    # find difference in closing value
    diff = currentclose - lastclosingvalue
    diff = round(diff,2)

    print(str(userticker), ' has had a change of', str(diff), 'since', readabledate)

    # add change to scraped data file
    strwrite = str(diff) + ' from ' + readabledate
    scraped_data["change"] = strwrite


def sendemail(ticker, scraped_data):
    # MUST ENABLE "LESS SECURE APPS ON GMAIL"
    #go to: fi
    fromaddr = "EMAIL"
    toaddr = "EMAIL"

    # create message
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    subjline = ticker + ' information'
    msg['Subject'] = str(subjline)
    body = "JSON attached below"

    # add attachment
    msg.attach(MIMEText(body, 'plain'))
    attachment = MIMEText(json.dumps(scraped_data))
    attachment.add_header('Content-Disposition', 'attachment',
                          filename="stock.json")
    msg.attach(attachment)

    # log in to server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "PASSWORD")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    print("sent email")
    server.quit()


if __name__=="__main__":
    # take in command line arg
    argparser = argparse.ArgumentParser()
    argparser.add_argument('ticker',help = '')
    argparser.add_argument('email',help = ' true/false if you want copy sent to email')
    args = argparser.parse_args()
    ticker = args.ticker # stock ticker
    email = args.email
   
    print ("Fetching data for %s"%(ticker))
    scraped_data = parse(ticker)
    quandl_api(ticker,scraped_data)

    if(email == "true"):
        sendemail(ticker, scraped_data)
    
    print ("Writing data to output file")
    #print (json.dumps(scraped_data, indent=4, sort_keys=True))
    with open('%s-summary.json'%(ticker),'w') as fp:
        json.dump(scraped_data,fp,indent = 4)




##############################################################
# tutorial modified from scrape hero's stock market tutorial #
##############################################################
