import os
from pprint import pformat

import boto3

from app import MONITOR


def handler(event, context):
    loans = MONITOR.get_interesting_loans(max_risk_level=int(os.environ["MAX_RISK_LEVEL"]))
    if len(loans):
        topic = boto3.resource("sns").Topic(os.environ['TOPIC'])
        topic.publish(Message=pformat(loans), Subject="New interesting loans on FinHub")
