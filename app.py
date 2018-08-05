import os
import logging

from purl import URL

from monitor.dao import KnownLoansDAO
from monitor.models import FinhubAPI, FinHubMonitor

__all__ = ("MONITOR", )

logging.basicConfig(level=logging.INFO)

_API = FinhubAPI(os.environ['EMAIL'], os.environ['PASSWORD'], URL("https://my.finhub.ua/portal-rs/api"))
_DAO = KnownLoansDAO(os.environ['TABLE'])
MONITOR = FinHubMonitor(_API, _DAO)
