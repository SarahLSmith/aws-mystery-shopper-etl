import csv
from datetime import datetime
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

MYSTERY_SHOPPER_FIELDS = [
            'store_id',
            'store_name',
            'mystery_shopper_id',
            'mystery_shopper_name',
            'store_type',
            'number_of_store_employees',
            'visit_date',
            'start_time',
            'end_time',
            'overall_score',
        ]

def extract(body_text):
    LOGGER.info('extract: starting')
    reader = csv.DictReader(
        body_text,
        fieldnames=MYSTERY_SHOPPER_FIELDS,
        delimiter=',',
    )

    # skip header row
    next(reader)

    data = [row for row in reader]
    # e.g., data = [{'Name': 'Alice', 'Age': '30', 'Role': 'Engineer'}, {'Name': 'Bob', 'Age': '25', 'Role': 'Designer'}]

    LOGGER.info(f'extract: done: rows={len(data)}')
    return data


# def remove_sensitive_information(data):
#     LOGGER.info(f'remove_sensitive_information: processing rows={len(data)}')
#     return [
#         {k: v for k, v in item.items() if k != 'mystery_shopper_name'} for item in data
#     ]

def remove_sensitive_information(data):
    LOGGER.info(f'remove_sensitive_information: processing rows={len(data)}')
    
    sanitized_data = []
    
    #[
#     {'mystery_shopper_name': 'Alice', 'age': '30', 'store_rating': '5'},
#     {'mystery_shopper_name': 'Bob', 'age': '25', 'store_rating': '2'}
# ]
    for row in data:
        # 1. Make a copy so we don't accidentally alter the original data
        clean_row = row.copy()
        
        # 2. Safely remove the key (the 'None' prevents errors if the key is already missing)
        clean_row.pop('mystery_shopper_name', None)
        
        # 3. Add the clean row to our new list
        sanitized_data.append(clean_row)

#     [
#     {'age': '30', 'store_rating': '5'},
#     {'age': '25', 'store_rating': '2'}
# ]

    return sanitized_data

def reformat_number_of_store_employees(data):
    LOGGER.info(f'reformat_number_of_store_employees: starting')
    updated_data = []
    for item in data:
        updated_item = item.copy()
        updated_item['number_of_store_employees'] = int(
            updated_item['number_of_store_employees'].strip('"')
        )
        updated_data.append(updated_item)

    LOGGER.info(f'reformat_number_of_store_employees: done: rows={len(updated_data)}')
    return updated_data


def reformat_visit_date(data):
    LOGGER.info('reformat_visit_date: starting')
    updated_data = []
    for item in data:
        updated_item = item.copy()
        input_format_string = '%d/%m/%Y'
        dt = datetime.strptime(updated_item['visit_date'], input_format_string)
        new_datetime = dt.strftime('%Y-%m-%d')
        updated_item['visit_date'] = new_datetime
        updated_data.append(updated_item)

    LOGGER.info(f'reformat_visit_date: done: rows={len(updated_data)}')
    return updated_data


def transform(data):
    LOGGER.info('transform: starting')
    data = remove_sensitive_information(data)
    data = reformat_number_of_store_employees(data)
    data = reformat_visit_date(data)

    LOGGER.info(f'transform: done: rows={len(data)}')
    return data
