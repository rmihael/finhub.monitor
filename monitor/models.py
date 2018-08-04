from datetime import datetime
import logging
from typing import List

import requests
from purl import URL

from monitor.dao import KnownLoansDAO
from monitor.domain import LoanRequest

log = logging.getLogger()
log.setLevel(logging.INFO)


class FinhubAPI:
    def __init__(self, email: str, password: str, endpoint: URL) -> None:
        self._email = email
        self._password = password
        self._endpoint = endpoint
        self._raw_token = None

    @property
    def _token(self):
        if self._raw_token is None:
            self._raw_token = self._login()
        return self._raw_token

    def _login(self) -> str:
        body = {
            "email": self._email,
            "password": self._password,
            "session": {
                "browser": "chrome",
                "deviceId": "mac",
                "deviceType": "DESKTOP"
            },
            "analytics": {
                "utm_source": "none",
                "utm_medium": "none",
                "utm_campaign": "none",
                "sd_mark": "none",
                "ad_mark": "none",
                "fl_mark": "none",
                "doaff_mark": "none",
                "cid": "none",
                "uagent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/67.0.3396.99 Safari/537.36"
            }
        }
        response = requests.post(self._endpoint.add_path_segment("user").add_path_segment("login").as_string(),
                                 json=body)
        return response.headers['JWT']

    def get_loan_requests(self) -> List[LoanRequest]:
        url = self._endpoint.add_path_segment("investor")\
                            .add_path_segment("investment")\
                            .add_path_segment("direct")\
                            .add_path_segment("page")\
                            .add_path_segment("1")
        response = requests.get(url, headers={"Authorization": "Bearer " + self._token}).json()
        return [LoanRequest(risk_level_group=int(i['riskLevelGroup']), risk_level=i['riskLevelRate'],
                            total=i['amount'], rest=i['investRest'], loan_id=i['appNum'])
                for i in response['data'] if i['investRest'] > 0]


class FinHubMonitor:
    def __init__(self, api: FinhubAPI, known_loans: KnownLoansDAO):
        self._api = api
        self._known_loans = known_loans

    def get_interesting_loans(self, max_risk_level: int) -> List[LoanRequest]:
        loans = self._api.get_loan_requests()
        log.info("Got %s loans from API" % len(loans))
        new_ids = self._known_loans.filter_out_known_ids([l.loan_id for l in loans])
        new_loans = [l for l in loans if l.loan_id in new_ids]
        log.info("Got %s new loans" % len(new_loans))
        interesting_loans = [l for l in new_loans if l.risk_level_group <= max_risk_level and l.rest > 0]
        log.info("Got %s interesting loans" % len(interesting_loans))
        self._known_loans.memorize_loans(new_ids, datetime.utcnow())
        return interesting_loans
