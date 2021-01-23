#!/bin/bash
set -euo pipefail

. ./.env

error() {
        [[ -n "${H2_DISCORD_URL}" ]] && curl -H "Content-Type: application/json" -X POST -d "{\"content\": \"Failed to update from ${old_version} to ${new_version}\"}" "${H2_DISCORD_URL}"
}

trap 'error' ERR

old_version="${H2_IMAGE_VERSION}"
git pull
new_version="$(git describe)"
if [[ "${old_version}" == "${new_version}" ]]
then
        exit 0
fi
sed -i -e "/^H2_IMAGE_VERSION=/c H2_IMAGE_VERSION=${new_version}" .env
sudo docker-compose pull
sudo docker-compose run --rm app migrate_schemas
sudo docker-compose up -d
[[ -n "${H2_DISCORD_URL}" ]] && curl -H "Content-Type: application/json" -X POST -d "{\"content\": \"Updated from ${old_version} to ${new_version}\"}" "${H2_DISCORD_URL}"
