import datetime
import os
from minio import Minio
from flask import Flask, jsonify

app = Flask(__name__)
# Force jsonify to not sort keys in json output
app.json.sort_keys = False

# Definitions:
# set tag to filter buckets, grab access from environment variables
tag_name="public_snapshots"
tag_value="true"

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
    return datetime.datetime.isoformat(dt)

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
        'last_update': datetime.datetime.now(datetime.UTC).isoformat()
    }
    output_dict["result"] = metadata_output

    # Cycle through list of defined bucket names
    for generator_name in generator_list:
        generator_output = []

        # Minio method to pull generator objects from bucket name
        objects = client.list_objects(generator_name)

        # Cycle through objects to define attributes
        for item in objects:
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
    app.run(host='0.0.0.0',port = 5000)
