from typing import List

import requests
from purl import URL

from monitor.domain import LoanRequest


class FinhubMonitor:
    def __init__(self, endpoint: URL) -> None:
        self._endpoint = endpoint

    def login(self, email: str, password: str) -> str:
        body = {
            "email": email,
            "password": password,
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

    def get_loan_requests(self, token: str) -> List[LoanRequest]:
        url = self._endpoint.add_path_segment("investor")\
                            .add_path_segment("investment")\
                            .add_path_segment("direct")\
                            .add_path_segment("page")\
                            .add_path_segment("1")
        response = requests.get(url, headers={"Authorization": "Bearer " + token}).json()
        return [LoanRequest(risk_level_group=int(i['riskLevelGroup']), risk_level=i['riskLevelRate'],
                            total=i['amount'], rest=i['investRest'])
                for i in response['data'] if i['investRest'] > 0]
