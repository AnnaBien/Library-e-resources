"""
Simplified database as Google Cloud database includes pricing.
"""

form_data = [
        {'name': '', 'library_card_no': '', 'email': '', 'resource_type': ''}
    ]


def get_next_user_data() -> dict:
    for user_data in form_data:
        yield user_data
