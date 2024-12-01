"""
Simplified database as Google Cloud database includes pricing.
"""
from enum import Enum


class EResourceType(Enum):
    legimi = 'legimi'
    empikgo = 'empik'


form_data = [
        {
            'name': 'Anna',
            'library_card_no': '213721',
            'email': 'example@gmail.com',
            'resource_type': EResourceType.empikgo.value
        }
    ]


def get_next_user_data() -> dict:
    for user_data in form_data:
        yield user_data
