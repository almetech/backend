import datetime
import os
import subprocess
import sys

import pandas as pd
import pickle
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from decouple import UndefinedValueError, config

from apps.taskscheduler.jobs import heartbeat, send_email

ist = pytz.timezone('Asia/Kolkata')

scheduler = BackgroundScheduler()

def run_scraper():
    subprocess.check_call((sys.executable, os.path.join(os.getcwd(), 'scraper', 'scraper.py'), '--config', str(os.path.join(os.getcwd(), 'scraper', 'listing.conf'))))


def construct_indexed_df(df, indexed_sentiments=None): # From CLEANED_UP file
    if indexed_sentiments is None:
        with open('indexed_sentiments.pkl', 'rb') as f:
            indexed_sentiments = pickle.load(f)
    sentiments = [{'id': df['id'][idx], 'product_id': df['product_id'][idx], **(indexed_sentiment)} for idx, indexed_sentiment in enumerate(indexed_sentiments) if indexed_sentiment not in ({}, None)]
    indexed_df = pd.DataFrame(sentiments)
    indexed_df.dropna(thresh=1)
    return indexed_df


REVIEW_DATAFRAME = None # Shared Dataframe


def start():
    global REVIEW_DATAFRAME
    try:
        df = pd.read_csv('sentiment_analysis.csv', sep=",", encoding="utf-8")
        REVIEW_DATAFRAME = construct_indexed_df(df)
    except Exception as ex:
        print(f"Error: {ex}. Exception during opening/processing sentiment_analysis.csv")
