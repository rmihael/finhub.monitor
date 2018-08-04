import os
from pprint import pformat

from purl import URL
import boto3

from monitor.dao import KnownLoansDAO
from monitor.models import FinhubAPI, FinHubMonitor


def handler(event, context):
    api = FinhubAPI(os.environ['EMAIL'], os.environ['PASSWORD'], URL("https://my.finhub.ua/portal-rs/api"))
    dao = KnownLoansDAO(os.environ['TABLE'])
    monitor = FinHubMonitor(api, dao)
    loans = monitor.get_interesting_loans(max_risk_level=int(os.environ["MAX_RISK_LEVEL"]))
    if len(loans):
        topic = boto3.resource("sns").Topic(os.environ['TOPIC'])
        topic.publish(Message=pformat(loans), Subject="New interesting loans on FinHub")
    