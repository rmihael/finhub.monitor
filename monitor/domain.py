from typing import NamedTuple


class LoanRequest(NamedTuple):
    risk_level_group: int
    risk_level: float
    total: int
    rest: int
