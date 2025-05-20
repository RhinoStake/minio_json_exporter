import datetime
import os
import re
from minio import Minio
from flask import Flask, jsonify

app = Flask(__name__)
# Force jsonify to not sort keys in json output
app.json.sort_keys = False

# Definitions:
# set tag to filter buckets, grab access from environment variables
tag_name = "public_snapshots"
tag_value = "true"

server_url = os.environ.get('SERVER_URL', 'None')
access_key = os.environ.get('ACCESS_KEY', 'None')
secret_key = os.environ.get('SECRET_KEY', 'None')

print(server_url)

# Connection information
client = Minio(
    server_url,
    access_key=access_key,
    secret_key=secret_key
)

# Return serialized isoformat for json compatibilty
def serialize_datetime(dt):
    # Format to have microsecond precision and +00:00 timezone format
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')

# Format date string to our required format
def format_date_string(date_str):
    try:
        # Check if date string ends with Z (UTC indicator)
        if date_str.endswith('Z'):
            # Remove the Z and parse the datetime
            clean_date_str = date_str[:-1]
            # Parse the datetime - we need to handle nanoseconds vs microseconds
            if '.' in clean_date_str:
                # If there are more than 6 digits after the decimal point for microseconds,
                # truncate to 6 digits (microseconds precision)
                main_part, fraction_part = clean_date_str.split('.')
                fraction_part = fraction_part[:6].ljust(6, '0')  # Pad to exactly 6 digits
                clean_date_str = f"{main_part}.{fraction_part}"

            # Parse the datetime
            dt = datetime.datetime.fromisoformat(clean_date_str)
            # Format with UTC offset
            return dt.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
        else:
            # If already in a different format, try to parse and reformat
            dt = datetime.datetime.fromisoformat(date_str)
            return dt.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
    except Exception as e:
        print(f"Error formatting date string {date_str}: {e}")
        # Return original if parsing fails
        return date_str

# Return a list of buckets that match the "group" tag of tag_value
def filter_buckets_by_tag(tag_value):
    filtered_buckets = []

    all_buckets = client.list_buckets()

    for bucket in all_buckets:
            tags = client.get_bucket_tags(bucket.name)

            if tags is not None and tags.get(tag_name) == tag_value:
                filtered_buckets.append(bucket.name)

    return filtered_buckets

# Generate json output
def generate_json_output(generator_list):
    output_dict = {}

    # Generate "header" json data
    metadata_output = {
        'last_update': serialize_datetime(datetime.datetime.now(datetime.UTC))
    }
    output_dict["result"] = metadata_output

    # Cycle through list of defined bucket names
    for generator_name in generator_list:
        generator_output = []

        # Minio method to pull generator objects from bucket name
        objects = client.list_objects(generator_name)

        # Cycle through objects to define attributes
        for item in objects:
            # Get object metadata
            try:
                # We need to retrieve the object's metadata, which requires making an additional call
                # Use stat_object to get the metadata
                obj_metadata = client.stat_object(generator_name, item.object_name)

                # Extract the requested metadata fields, with default values if not present
                app_hash = obj_metadata.metadata.get('X-Amz-Meta-App_hash', '')
                chain_id = obj_metadata.metadata.get('X-Amz-Meta-Chain_id', '')
                last_block_height = obj_metadata.metadata.get('X-Amz-Meta-Last_block_height', '')
                last_block_time = obj_metadata.metadata.get('X-Amz-Meta-Last_block_time', '')

                # Format the last_block_time if it exists
                if last_block_time:
                    formatted_last_block_time = format_date_string(last_block_time)
                else:
                    # Use the item's last_modified and format it correctly
                    formatted_last_block_time = serialize_datetime(item.last_modified)

                item_dict = {
                    'name': item.object_name,
                    'url': f'https://{server_url}/{generator_name}/{item.object_name}',
                    'size': item.size,
                    'last_modified': formatted_last_block_time,
                    'app_hash': app_hash,
                    'chain_id': chain_id,
                    'last_block_height': last_block_height
                }
            except Exception as e:
                # If we can't get metadata, fall back to the basic info
                print(f"Error getting metadata for {item.object_name}: {e}")
                item_dict = {
                    'name': item.object_name,
                    'url': f'https://{server_url}/{generator_name}/{item.object_name}',
                    'size': item.size,
                    'last_modified': serialize_datetime(item.last_modified)
                }

            generator_output.append(item_dict)

        # Sort generator_output by last_modified date in reverse chronological order
        generator_output.sort(key=lambda x: x['last_modified'], reverse=True)

        # Create dict item with title of bucket name with values
        output_dict[generator_name] = generator_output

    # return json formatted dict of all items
    return jsonify(output_dict)

@app.route('/', methods = ['GET'])
def ReturnJSON():
    generator_list = filter_buckets_by_tag(tag_value)
    json_output = generate_json_output(generator_list)
    return json_output

# Main
if __name__ == '__main__':
    # json_output = generate_json_output(generator_list)
    # print(json_output)
    app.run(host='0.0.0.0', port=5000)