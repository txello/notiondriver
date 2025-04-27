from enum import Enum

class OperatorEnum(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    AND = "and"
    OR = "or"
    NOT = "not"