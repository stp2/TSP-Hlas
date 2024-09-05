#!/bin/bash
# přes mapy.cz API načte GPS souřadnice z adresy získané z csv souboru jméno,adresa...
# API klíč je v souboru key.api
# filtr in:jméno+adresa; out:jméno+GPS

shopt -s extglob

if [[ -r key.api ]]; then
    KEY=$(<key.api)
else
    echo "Create key.api with API key" >&2
    exit 1
fi

while IFS= read -r LINE; do
    NAME=${LINE%%,+([^,]),+([^,]),+([^,])}
    ADDRESS=${LINE##+([^,]),}
    # filter out PSČ
    ADDRESS=${ADDRESS%%,+([^,])}

    GPS=$(curl --get --data-urlencode "query=${ADDRESS}" "https://api.mapy.cz/v1/geocode?lang=cs&limit=1&type=coordinate&apikey=${KEY}" -H 'accept: application/json' \
        | jq -cM .items[0].position | sed -E 's/^.*:([[:digit:].]+).+:([[:digit:].]+).*$/\1,\2/' )

    echo "${NAME},${GPS}"
done

