from utils import s3_utils, sql_utils, db_utils

import etl
import logging
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

#This value was set in etl-stack.yml, the value will match a key in the AWS Systems Manager Parameter Store, which contains the Redshift connection details
SSM_ENV_VAR_NAME = 'SSM_PARAMETER_NAME'


def lambda_handler(event, context):
    LOGGER.info('lambda_handler: starting')
    
    # Block 1: Parse the event to get the bucket_name and file_path
    try:
        bucket_name, file_path = s3_utils.get_file_info(event)
    except Exception as err:
        LOGGER.error(f'lambda_handler: event parsing failed: error={err}, event={event}')
        raise err
    
    # Block 2: Confirmed that we have the bucket_name and file_path
    # Load the file from S3, extract, transform, and load into Redshift
    try:
        csv_text = s3_utils.load_file(bucket_name, file_path)
        data = etl.extract(csv_text)  



        transformed_data = etl.transform(data)
        # One would not normally log the data directly!!
        # ...there could be loads and it could have PID in it!!
        LOGGER.warning(f'lambda_handler: transformed_data={transformed_data}')

        ssm_param_name = os.environ.get(SSM_ENV_VAR_NAME, 'NOT_SET')
        LOGGER.info(f'lambda_handler: ssm_param_name={ssm_param_name} from ssm_env_var_name={SSM_ENV_VAR_NAME}')
        redshift_details = db_utils.get_ssm_param(ssm_param_name)
        conn, cur = db_utils.open_sql_database_connection_and_cursor(redshift_details)

        sql_utils.create_db_tables(conn, cur)
        sql_utils.save_data_in_db(conn, cur, bucket_name, file_path, transformed_data)
        cur.close()
        conn.close()

        LOGGER.info(f'lambda_handler: done, file={file_path}')

    except Exception as err:
        LOGGER.error(f'lambda_handler: processing failure: error={err}, file={file_path}')
        raise err
