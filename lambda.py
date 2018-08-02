import os

from purl import URL

from monitor.models import FinhubMonitor


def handler(event, context):
    monitor = FinhubMonitor(URL("https://my.finhub.ua/portal-rs/api"))
    token = monitor.login(os.environ['EMAIL'], os.environ['PASSWORD'])
    loans = monitor.get_loan_requests(token)
    return str(loans)
