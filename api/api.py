import json
import os
import time
from urllib.parse import quote

import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route("/url/urlscan")
def urlscan_url():
    url_to_scan = request.args.get("url")  # get the query from thblacke url
    privacy = request.args.get("option")  # Set the privacy of the scan
    headers = {
        "API-Key": os.getenv("URLSCAN_IO_KEY"),  # Your api key for urlscan.io
        "Content-Type": "application/json",
    }
    data = {"url": f"{url_to_scan}", "visibility": f"{privacy}"}
    response = requests.post(
        "https://urlscan.io/api/v1/scan/",
        headers=headers,
        data=json.dumps(data),
    ).json()

    uuid = response["uuid"]  # You need the uuid to get the report of your scan
    time.sleep(30)  # You need to wait for the server to process your request
    scan_results = requests.get(f"https://urlscan.io/api/v1/result/{uuid}/").json()

    return scan_results


# task_url = scan_results['task']['url']
# verdicts_overall_score = scan_results['verdicts']['overall']['score']
# verdicts_overall_malicious = scan_results['verdicts']['overall']['malicious']
# task_report_URL = scan_results['task']['reportURL']


@app.route("/url/opswat")
def opswat_url():
    domain = quote(request.args.get("d"), safe="")  # encode :// to %3A%2F%2F
    headers = {"apikey": os.getenv("OPSWAT_KEY")}  # your api key for opswat
    response = requests.get(
        f"https://api.metadefender.com/v4/url/{domain}", headers=headers
    ).json()  # make sure the response is json

    return response


@app.route("/url/vt")
def vt_url():
    query = request.args.get("query")
    url = "https://www.virustotal.com/vtapi/v2/url/scan"
    params = {"apikey": os.environ.get("VT_KEY"), "url": f"{query}"}
    response_post = requests.post(url, data=params).json()

    resource = response_post["resource"]
    time.sleep(15)  # API is limited to 4 requests per minute w/ free version
    urlreport = "https://www.virustotal.com/vtapi/v2/url/report"
    params = {"apikey": os.environ.get("VT_KEY"), "resource": f"{resource}"}
    response = requests.get(urlreport, params=params).json()
    return response


@app.route("/domain/opswat")
def opswat_domain():
    domain_to_scan = request.args.get("domain")  # get the query from the url
    headers = {"apikey": os.getenv("OPSWAT_KEY")}  # your api key for opswat
    response = requests.get(
        f"https://api.metadefender.com/v4/domain/{domain_to_scan}", headers=headers
    ).json()

    return response


@app.route("/domain/vt")
def vt_domain():
    domain = request.args.get("domain")
    url = "https://www.virustotal.com/vtapi/v2/domain/report"
    params = {"apikey": os.environ.get("VT_KEY"), "domain": f"{domain}"}
    response = requests.get(url, params=params).json()
    return response


@app.route("/file/vt")
def vt_file():
    upload = request.args.get("file")  # must give absolute path
    url = "https://www.virustotal.com/vtapi/v2/file/scan"
    params = {"apikey": os.environ.get("VT_KEY")}
    files = {"file": (upload, open(upload, "rb"))}
    response_post = requests.post(url, files=files, params=params).json()

    resource = response_post["resource"]
    time.sleep(15)
    url = "https://www.virustotal.com/vtapi/v2/file/report"
    params = {"apikey": os.environ.get("VT_KEY"), "resource": f"{resource}"}
    response = requests.get(url, params=params).json()

    return response


@app.route("/file/opswat")
def opswat_file():
    upload = request.args.get("file")
    url = "https://api.metadefender.com/v4/file"
    headers = {
        "apikey": os.getenv("OPSWAT_KEY"),
        "content-type": "application/octet-stream",
    }
    response_post = requests.post(url, data=upload, headers=headers).json()

    dataID = response_post["data_id"]
    time.sleep(15)  # wait for file to be generated
    urlScan = "https://api.metadefender.com/v4/file/" + dataID
    get_headers = {"apikey": os.getenv("OPSWAT_KEY")}
    response = requests.get(urlScan, headers=get_headers)

    return response.json()


@app.route("/dns/ibm")
def ibm_url():
    url_to_scan = quote(request.args.get("url"), safe="")
    url = f"https://api.xforce.ibmcloud.com/resolve/{url_to_scan}"
    get_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f'Basic {os.environ.get("IBM_AUTH_TOKEN")}',  # ibm_key:ibm_key_passwd base 64 encoded...
    }
    response = requests.get(url, headers=get_headers)

    return response.json()


@app.route("/ip/ibm")
def ibm_ip():
    ip_to_scan = request.args.get("ip")
    url = f"https://api.xforce.ibmcloud.com/ipr/{ip_to_scan}"
    get_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f'Basic {os.environ.get("IBM_AUTH_TOKEN")}', 
    }
    response = requests.get(url, headers=get_headers)

    return response.json()
  