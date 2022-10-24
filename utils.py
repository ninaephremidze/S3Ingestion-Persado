import config

import csv
import copy
import datetime
import json
import random
import urllib
import urllib3

true = True
false = False
null = None

API_ROUTE_TRACK = "track"
API_ROUTE_IDENTIFY = "identify"
BASE_URL_TRACK = "https://a.klaviyo.com/api/track"
BASE_URL_IDENTIFY = "https://a.klaviyo.com/api/identify"
#requests = urllib3.PoolManager()
import requests

class KlaviyoClient:
    def __init__(self, public_api_key=None, private_api_key=None):
        self.public_api_key = public_api_key
        self.private_api_key = private_api_key

    def send_klaviyo_track_or_identify_bulk(self, route, json_list):
        counter = 0
        total = len(json_list)
        data = []
        # Send each request
        print(f"Starting {route} batch")
        for payload in json_list:
            counter = counter + 1
            if counter % 50 == 0:
                print(f"Sending {str(counter)} out of {str(total)} {route} requests")
            data.append(self._send_klaviyo_track_or_identify(route=route, json_payload=payload))
        # Return failed requests
        successful_requests = []
        failed_requests = []
        for item in data:
            if item.get("response") == "0":
                failed_requests.append(item)
            else:
                successful_requests.append(item)
        print("Done!")
        return successful_requests, failed_requests

    def _send_klaviyo_track_or_identify(self, route, json_payload):
        if route == API_ROUTE_TRACK:
            base_url = BASE_URL_TRACK
        elif route == API_ROUTE_IDENTIFY:
            base_url = BASE_URL_IDENTIFY
        else:
            return None
        json_payload["token"] = self.public_api_key
        # Event name imports as a tuple in python 3 so convert it to a string
        json_payload["event"] = ",".join(config.event_name)
        #encoded_json_payload = urllib.parse.quote(json.dumps(json_payload).encode())
        headers = {"Content-Type": "application/json"}
        response = requests.request(
            method="POST",
            url=base_url,
            headers=headers,
            json=json_payload
        )
        return json_payload


def load_csv_as_dict_array(filename, filepath=config.working_dir):
    print('Loading "' + str(filename) + '"...')
    dict_array = []
    with open(filepath + filename + ".csv", errors="ignore") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            dict_array.append(dict(row))
    print('"' + str(filename) + '" loaded!')
    return dict_array


def map_dict_array_to_payloads(dict_array, mapping):
    payloads = []
    for dict_item in dict_array:
        mapped_dict = map_dict_to_payload(dict_item, mapping)
        validated_dict = validate_payload(mapped_dict)
        payloads.append(validated_dict)
    return payloads


def map_dict_to_payload(dict_item, mapping):
    current_payload = {}
    for key, mapping_item in mapping.items():
        if isinstance(mapping_item, dict) and "column_header" not in mapping_item.keys():
            # If this item is a dict and doesnt contain a header mapping (ie. not mapped directly to CSV data)
            current_payload[key] = map_dict_to_payload(dict_item, mapping_item)
        else:
            current_payload[key] = resolve_mapping(mapping_item, dict_item)
    return current_payload


def resolve_mapping(mapping_item, dict_item):
    #print(f"Mapping item: {mapping_item}")
    #print(f"Dict item: {dict_item}")
    column_header = mapping_item.get("column_header")
    if mapping_item.get("data_type_override") == "number":
        if dict_item.get(column_header, "").isnumeric:
            # If the value is a number, attempt to interpret it as a number
            return float(dict_item.get(column_header, 0))
        else:
            # Fall back to interpreting it as a string if the conversion doesnt work
            return dict_item.get(column_header, "")
    elif mapping_item.get("data_type_override") == "boolean":
        if is_truthy(dict_item.get(column_header, "")):
            return True
        elif is_falsy(dict_item.get(column_header, "")):
            return False
        else:
            # Fall back to interpreting it as a string if the conversion doesnt work
            return dict_item.get(column_header, "")
    elif mapping_item.get("data_type_override") == "date" and mapping_item.get("data_type_details"):
        try:
            # If the value is a date, attempt to interpret it as a date
            parsed_date = datetime.datetime.strptime(
                dict_item.get(column_header, ""),
                mapping_item.get("data_type_details")
            )
            # Convert the date to a unix timestamp
            return int(parsed_date.replace(tzinfo=datetime.timezone.utc).timestamp())
        except ValueError:
            # Fall back to interpreting it as a string if the conversion doesnt work
            return dict_item.get(column_header, "")
    # If we can't resolve the item or there is no override, just return pass the value directly
    #   (or an empty string if it doesn't exist)
    return dict_item.get(column_header, "")


def is_truthy(value):
    truthy_values = [1, "1", True, "true", "t", "yes", "y"]
    if value in truthy_values:
        return True
    else:
        return False


def is_falsy(value):
    falsy_values = [0, "0", False, "false", "f", "no", "n"]
    if value in falsy_values:
        return True
    else:
        return False


def validate_payload(mapped_dict):
    validated_dict = copy.deepcopy(mapped_dict)

    # Make sure "time" is a unix timestamp or missing so we can auto-hydrate it
    if validated_dict.get("time", None):
        try:
            # If the "time" exists and is an int, attempt to interpret it as a date
            datetime.datetime.utcfromtimestamp(validated_dict.get("time", None))
        except (ValueError, TypeError):
            # If that fails, remove the "time" property so we consider the event as happening "now"
            validated_dict.pop("time")

    # Make sure $event_id is set in case events come in at the same time for a given profile
    if validated_dict.get("properties") and not validated_dict.get("properties", {}).get("$event_id"):
        # Using unix timestamp in milliseconds plus a random number
        validated_dict["properties"]["$event_id"] = f"{datetime.datetime.utcnow().timestamp() * 1e3}_{random.random()}"

    return validated_dict


def save_json_array(json_array, filepath="./", filename="data_export"):
    with open(filepath + filename + ".txt", "w") as outfile:
        json.dump(json_array, outfile, indent=4)
