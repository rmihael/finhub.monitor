import os

from purl import URL

from monitor.dao import KnownLoansDAO
from monitor.models import FinhubAPI, FinHubMonitor


def handler(event, context):
    api = FinhubAPI(os.environ['EMAIL'], os.environ['PASSWORD'], URL("https://my.finhub.ua/portal-rs/api"))
    dao = KnownLoansDAO(os.environ['TABLE'])
    monitor = FinHubMonitor(api, dao)
    loans = monitor.get_interesting_loans(max_risk_level=5)
    return str(loans)
