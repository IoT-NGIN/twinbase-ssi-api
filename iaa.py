import json
import os

import dtweb
import requests
from fastapi import FastAPI
from pyld import jsonld

app = FastAPI(title="IAA-configurator", version="0.0.1")


IAA_CONF_FILE = os.environ["IAA_CONF_FILE"]
OWNER_DID = os.environ["OWNER_DID"]
PROXY_PASS = os.environ["PROXY_PASS"]
CONFIGURATOR_ADDRESS = os.environ["CONFIGURATOR_ADDRESS"]

LD_ACCESS_REQUIREMENTS = "https://twinschema.org/accessRequirements"
LD_LOCATION = "http://www.w3.org/2003/01/geo/wgs84_pos#location"
LD_NEIGHBOURHOOD = "https://saref.etsi.org/saref4city/Neighbourhood"

BASE_URL = "https://juusoautiosalo.github.io/twinbase-smart-city"

# Initialize a conf file
iaa_conf = {
    "resources": {
        "/twins": {
            "authorization": {
                "type": "jwt-vc-dpop",
                "trusted_issuers": {
                    OWNER_DID: {"issuer_key": OWNER_DID, "issuer_key_type": "did"}
                },
                "filters": [
                    [
                        "$.vc.credentialSubject.capabilities.'https://iot-ngin.twinbase.org/twins'[*]",
                        "READ",
                    ]
                ],
            },
            "proxy": {"proxy_pass": PROXY_PASS},
        },
        "/docs": {"proxy": {"proxy_pass": PROXY_PASS}},
        "/openapi.json": {"proxy": {"proxy_pass": PROXY_PASS}},
        "/favicon.ico": {"proxy": {"proxy_pass": PROXY_PASS}},
        "/update": {"proxy": {"proxy_pass": CONFIGURATOR_ADDRESS}},
    }
}


def get_conf_twin_template() -> dict:
    return {
        "authorization": {
            "type": "jwt-vc-dpop",
            "trusted_issuers": {
                OWNER_DID: {"issuer_key": OWNER_DID, "issuer_key_type": "did"}
            },
            "filters": [
                [
                    "$.vc.credentialSubject.capabilities.'https://iot-ngin.twinbase.org/twins'[*]",
                    "READ",
                ]
            ],
        },
        "proxy": {"proxy_pass": PROXY_PASS},
    }


@app.get("/update")
def update():
    try:
        with open(IAA_CONF_FILE, "r") as jsonfiler:
            conf = json.load(jsonfiler)
    except FileNotFoundError:
        print("IAA.conf not found, creating new from template.")
        conf = iaa_conf

    listurl = BASE_URL + "/" + "/index.json"
    r = requests.get(listurl)
    twins = r.json()["twins"]

    for twin in twins:
        print("\nChecking " + twin["name"])
        # pprint.pprint(twin)
        try:
            doc = dtweb.client.fetch_dt_doc(twin["dt-id"])
        except:
            print(
                "This twin is not working properly. Probably the DTID is not working."
            )
            pass
        filters = get_location_filters_for(doc)
        configure(conf, twin, filters)

    with open(IAA_CONF_FILE, "w", encoding="utf-8") as jsonfilew:
        json.dump(conf, jsonfilew, indent=4, ensure_ascii=False)

    return {"detail": "updated"}


def configure(conf: dict, twin: dict, filters: list[str]) -> None:
    """Define twin conf"""

    conf_twin = get_conf_twin_template()
    print("Conf template: " + str(conf_twin))

    for filter_content in filters:
        print("Creating filter: " + filter_content)
        filter = [f"$.vc.credentialSubject.capabilities.'{filter_content}'[*]", "READ"]
        conf_twin["authorization"]["filters"].append(filter)

    local_id = twin["dt-id"].split("/")[3]
    conf["resources"]["/twins/" + local_id] = conf_twin

    print(conf_twin)


def get_location_filters_for(document: dict) -> list[str]:
    filters: list[str] = []
    expanded_doc = jsonld.expand(document)

    if not len(expanded_doc) > 0:
        print("Found no linked data.")
        return filters

    if LD_LOCATION not in expanded_doc[0]:
        print(f"Found linked data, but not {LD_LOCATION}")
        return filters

    loc = expanded_doc[0][LD_LOCATION]

    if type(loc) is dict:
        print("One location definitions found")
        print("Value: " + loc["@value"])
        filters.append(f"{LD_NEIGHBOURHOOD} = {loc['@value']}")

    elif type(loc) is list:
        print("Several location definitions found")
        for location in loc:
            print(f"Type: {location['@type']} Value: {location['@value']}")
            # This @type & @value style was used at least in:
            # https://csiro-enviro-informatics.github.io/info-engineering/linked-data-api.html
            if location["@type"] == LD_NEIGHBOURHOOD:
                print("Found neighbourhood!")
                filters.append(f"{LD_NEIGHBOURHOOD} = {location['@value']}")
                print("Appended neighbourhood filter.")

    return filters


# Update conf file at startup
update()
