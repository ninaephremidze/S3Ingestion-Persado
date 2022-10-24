import config
import utils

from datetime import datetime
import boto3
import sys


def build_and_send_events(klaviyo_client, file_dict_array):
    event_payloads = utils.map_dict_array_to_payloads(file_dict_array, config.event_mapping)
    successful_requests, failed_requests = klaviyo_client.send_klaviyo_track_or_identify_bulk(
        utils.API_ROUTE_TRACK,
        event_payloads
    )
    print('Successful profile payload count: ', len(successful_requests))
    print('Failed profile payloads count: ', len(failed_requests))

    # Send logs to S3 after processing is done
    #   (these are commented out by default to reduce S3 storage)
    send_logs_to_s3(
        request_type=utils.API_ROUTE_TRACK,
        successful_requests=successful_requests,
        failed_requests=failed_requests
    )


def build_and_send_profiles(klaviyo_client, file_dict_array):
    profile_payloads = utils.map_dict_array_to_payloads(file_dict_array, config.profile_mapping)
    successful_requests, failed_requests = klaviyo_client.send_klaviyo_track_or_identify_bulk(
        utils.API_ROUTE_IDENTIFY,
        profile_payloads
    )
    print('Successful profile payload count: ', len(successful_requests))
    print('Failed profile payloads count: ', len(failed_requests))

    # Send logs to S3 after processing is done
    #   (these are commented out by default to reduce S3 storage)
    send_logs_to_s3(
        request_type=utils.API_ROUTE_IDENTIFY,
        successful_requests=successful_requests,
        failed_requests=failed_requests
    )


def send_logs_to_s3(request_type, successful_requests=None, failed_requests=None):
    # Save successful requests log if there were any
    if successful_requests and isinstance(successful_requests, list):
        filename_successful = f"{date_time} - {request_type} payloads - successful"
        utils.save_json_array(
            successful_requests,
            filename=filename_successful
        )
        s3.upload_file(f"./{filename_successful}.txt", config.s3_bucket_name, f"{config.s3_logs_folder}{filename_successful}.txt")
    # Save failed requests log if there were any
    if failed_requests and isinstance(failed_requests, list):
        filename_failed = f"{date_time} - {request_type} payloads - successful"
        utils.save_json_array(
            failed_requests,
            filename=f"{date_time} - {request_type} payloads - failed"
        )
        s3.upload_file(f"./{filename_failed}.txt", config.s3_bucket_name, f"{config.s3_logs_folder}{filename_failed}.txt")


s3 = boto3.client("s3")
now = datetime.now()
date_time = now.strftime("%Y-%m-%d %H:%M:%S")

# Capture filename from incoming terminal args
filename = sys.argv[1]
# Create a Klaviyo client for sending track or identify requests
klaviyo_client = utils.KlaviyoClient(public_api_key=config.public_api_key)
# Load up the CSV as an array of dicts
file_dict_array = utils.load_csv_as_dict_array(filename, filepath=config.working_dir)

# Uncomment this line if you plan to send Track requests to sync events
#   (activity or actions a person or thing has taken) from these CSVs
build_and_send_events(klaviyo_client, file_dict_array)

# Uncomment this line if you plan to send Identify requests to sync profile properties
#   (attributes about a person) from these CSVs
build_and_send_profiles(klaviyo_client, file_dict_array)
