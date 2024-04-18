# minio_json_exporter

Simple script for creating a json endpoint that lists files in minio buckets


## How to Use

First, add a tag on the Minio buckets you want to be visible to this tool, tag them with the tag `public_snapshots`: `true`. Without this tag, they will not be inspected or the contents shown.

Utilize the sample `docker-compose.yml` file and update the following variables:

* `SERVER_URL=base.url.com` : FQDN of your minio server, do not include `https://`.  It is https, right?
* `ACCESS_KEY=minio_access_key` : Access key to use.  This access key needs to have the ability to list both buckets and their contents for the buckets tagged as described above.
* `SECRET_KEY=minio_secret_key` : Associated secret

That's it!  Stand up your favorite reverse proxy (e.g. Caddy) and route requests to `127.0.0.1:5000`.  When a client hits that url, a json-formatted string will output.

Have ideas/changes/additions? Great! Feel free to push a PR to this repo or reach out to [me on Discord](https://discord.gg/SGhQzj5tyz)!

## Who is RHINO?

RHINO is a professionally managed, highly available validator service. Earn rewards and help secure networks by staking your tokens with RHINO. We operate across the Aptos, Cosmos, Chainlink, and Helium ecosystems. Read more at [https://rhinostake.com](https://rhinostake.com).