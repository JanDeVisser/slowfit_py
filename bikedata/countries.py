import json

outdata = {}
with open("iso3166.orig") as fh:
    data = json.load(fh)

    for c in data:
        outdata[c["name"]] = {
                "isoCode": c["alpha-2"],
                "isoCode3": c["alpha-3"]
        }

with open("country.json", "w+") as fh:
    json.dump(outdata, fh, indent=4)

