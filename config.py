# Klaviyo account
public_api_key = "abc123"

# The bucket name of the S3 to which you want to send log files
s3_bucket_name = "klaviyo-s3-triggered-csv-ingestion-bucket"

# The folder on the S3 where logs will be sent
s3_logs_folder = "logs/"

# The working directory where the code will be run on the EC2
working_dir = "/home/ec2-user/"

# Event mapping example
# edit this to conform to your CSV's headers, or delete
event_name = "CSV Triggered Event Name",
event_mapping = {
   "customer_properties": {
      "$email": {
         "column_header": "EMAIL"
      }
   },
   "properties": {
      "$event_id": {
         "column_header": "ORDER_ID"
      },
      "$value": {
         "column_header": "ORDER_TOTAL"
      },
      "OrderType": {
         "column_header": "ORDER_TYPE"
      },
      "CouponCode": {
         "column_header": "COUPON_CODE"
      }
   },
   "time": {
      "column_header": "DATE_ORDERED",
      "data_type_override": "date",
      "data_type_details": "%Y-%m-%d %H:%M:%S"
   }
}

# Profile property mapping example
# edit this to conform to your CSV's headers, or delete
profile_mapping = {
   "properties": {
      "$email": {
         "column_header": "EMAIL"
      },
      "$first_name": {
         "column_header": "BILLING_FIRST_NAME"
      },
      "$last_name": {
         "column_header": "BILLING_LAST_NAME"
      },
      "$region": {
         "column_header": "BILLING_STATE_CODE"
      },
      "$zip": {
         "column_header": "BILLING_ZIP"
      },
      "$phone_number": {
         "column_header": "BILLING_PHONE"
      }
   }
}
