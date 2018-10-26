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
    # TODO: create first endpoint link that takes in ticker in the url
    # call get requests with the url
    # wait for request to come back and then parse the html
    
    summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr') # get info from specific div
    summary_data = OrderedDict() # this is dictionary that remembers the order contents are added, this is what we will be writing to

    # second link to get more details that arent on the front page
    other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(ticker)
    # the link above takes in the stock ticker as an argument {0} , try the filled in tesla one below to see what the json looks like:
    # https://query2.finance.yahoo.com/v10/finance/quoteSummary/tsla?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com
   
    # TODO: parse the html for the second link and load it into json format
   
    # print (json.dumps(json_loaded_summary, indent=4, sort_keys=True)) # print out json from webscrapped data
    
    # other metrics:
    y_Target_Est = json_loaded_summary["quoteSummary"]["result"][0]["financialData"]["targetMeanPrice"]['raw']
    earnings_list = json_loaded_summary["quoteSummary"]["result"][0]["calendarEvents"]['earnings']
    eps = json_loaded_summary["quoteSummary"]["TODO"][TODO]["TODO"]["TODO"]['TODO']
    
   
    datelist = []
    for i in earnings_list['earningsDate']: # parse earnings data
        datelist.append(i['fmt'])
    earnings_date = ' to '.join(datelist)
    for table_data in summary_table:
        raw_table_key = table_data.xpath('.//td[contains(@class,"C(black)")]//text()')  # extract title information from table
        raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()') # extract value information from table
        table_key = ''.join(raw_table_key).strip()  a
        table_value = ''.join(raw_table_value).strip()
        # TODO: add key value pairs to summary data
    
    # TODO: add other metrics to summary data and return


# TODO: handle invalid tickers


def quandl_api(userticker,scraped_data):
    # we will be using the API to quickly compare closing price with older data
    # we need the old date and the old price from the API
    
    tickers = [userticker];
    # api call to quandl, gte and lte are date bounds
    data = quandl.get_table('WIKI/PRICES', ticker = tickers,
                                qopts = { 'columns': ['ticker', 'date', 'adj_close'] },
                                date = { 'gte': '2018-01-19', 'lte': '<TODAYS DATE> },
                                paginate=True)
    
    # TODO: get most recent entry in table using head and extract date and last closing of stock

    # TODO:  convert date to human readable format

    # TODO: convert to number, remove commas
    
    # TODO: get webscrapped value "previous close" to compare and find difference in closing value, round to nearest cent

    # print(str(userticker), ' has had a change of', str(diff), 'since', readabledate)

    # TODO: add change to scraped data file



def sendemail(ticker, scraped_data):
    # MUST ENABLE "LESS SECURE APPS ON GMAIL"
    #go to: https://myaccount.google.com/lesssecureapps?pli=1
    fromaddr = "YOUR EMAIL HERE"
    toaddr = "TO SEND TO EMAIL HERE"

    # create message
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    subjline = ticker + ' information'
    msg['Subject'] = str(subjline)
    body = "YOUR BODY PARAGRAPH HERE"

    # add attachment
    msg.attach(MIMEText(body, 'plain'))
    attachment = MIMEText(json.dumps(scraped_data))
    attachment.add_header('Content-Disposition', 'attachment',
                          filename="stock.json")
    msg.attach(attachment)

    # TODO: log in to server
    server = smtplib.SMTP('smtp.gmail.com', 587)


if __name__=="__main__":
    # TODO: parse command line
    argparser = argparse.ArgumentParser()
    # TODO: add ticker and email T/F as arguments
    
    # get the values for them
   
    # print ("Fetching data for %s"%(ticker))
   
    # TODO: add function calls
    
    print ("Writing data to output file")
    with open('%s-summary.json'%(ticker),'w') as fp:
        json.dump(scraped_data,fp,indent = 4)




##############################################################
# tutorial modified from scrape hero's stock market tutorial #
##############################################################
