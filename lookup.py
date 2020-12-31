from app import cache
import bs4
import common, settings
from itertools import groupby
import requests
import re
import time



@cache.memoize()
def virustotal(url):
    id_url = "https://www.virustotal.com/api/v3/urls"
    result_url = "https://www.virustotal.com/api/v3/analyses/"
    headers = {"x-apikey": settings.settings["virus_total_api"]}

    try:
        analysis = requests.post(id_url, headers=headers, data={"url": url})
        analysis_id = analysis.json()["data"]["id"]

        # Polling to wait until scan is complete
        for i in range(3):
            response = requests.get(result_url + analysis_id, headers=headers)
            results = response.json()["data"]["attributes"]

            if results["status"] == "completed":
                break
            else:
                time.sleep(7)

        return results

    except Exception as e:
        print(repr(e))


# TODO: allow custom user agent in scan, toggle for rescan
@cache.memoize()
def urlscan(url):
    search_url = 'https://urlscan.io/api/v1/search/?q='
    scan_url = 'https://urlscan.io/api/v1/scan/'
    headers = {'API-Key': settings.settings["url_scan_api"], 'Content-Type': 'application/json'}

    path = common.get_path(url)
    query = 'domain:"{}" AND page.url:"{}"'.format(common.get_bare_hostname(url), path if path else "")

    try:
        # Search to see if the site has already been scanned
        search_results = requests.get(search_url + query).json()
        if search_results["total"] > 0:
            result_link = search_results["results"][0]["result"]

        else:
            response = requests.post(scan_url, headers=headers, json={"url": url, "visibility": "public"}).json()
            result_link = response["api"]

        # Polling to wait until scan is complete
        for i in range(10):
            results = requests.get(result_link)

            if results.status_code == 404:
                time.sleep(10)
            else:
                break

        if results.status_code != 200:
            return None

        # Download the plain-text DOM too
        results = results.json()
        results["task"]["dom"] = requests.get(results["task"]["domURL"]).text
        return results

    except Exception as e:
        print(repr(e))


@cache.memoize()
def geoip(query):
    base_url = 'http://ip-api.com/json/'
    response = requests.get(base_url + query)
    results = response.json()

    if response.status_code != 200 or results["status"] == "fail":
        results["as"] = "ERROR"
        results["countryCode"] = "AQ"

    return results


@cache.memoize()
def iana_whois(query):
    base_url = 'https://www.iana.org/whois?q='
    response = requests.get(base_url + query)

    if response.status_code != 200:
        return ["Error"]

    parser = bs4.BeautifulSoup(response.text, "html.parser")
    result = parser.pre.get_text().splitlines()

    # Remove consecutive newlines
    return [x[0] for x in groupby(result)]
    

@cache.memoize()
def dq_whois(query, cached=True):
    base_url = 'https://dnsquery.org/whois/'
    cache = '/nocache' if not cached else ''

    session = requests.Session()
    page = session.get(base_url + query + cache).text
    
    new_url = re.search("\$\.ajax\({\s*url: '(.*)',", page).group(1)
    response = session.get(new_url)

    if response.status_code != 200:
        return ["Error"]

    parser = bs4.BeautifulSoup(response.text, "html.parser")
    result = parser.pre.get_text().splitlines()

    # Remove consecutive newlines
    result = [x[0] for x in groupby(result)]
    result.pop(0)
    return result


@cache.memoize()
def dig_dns(query, type="A"):
    form_url = 'https://toolbox.googleapps.com/apps/dig/'
    post_url = 'https://toolbox.googleapps.com/apps/dig/lookup'

    session = requests.Session()
    page = session.get(form_url)

    parser = bs4.BeautifulSoup(page.text, "html.parser")
    token = parser.find("input", {"name": "csrfmiddlewaretoken"})['value']
    
    response = session.post(post_url, headers={"Referer": form_url}, data={"csrfmiddlewaretoken": token, "domain": query, "typ": type})

    if response.status_code == 200:
        return response.json()["response"].split("\n")
    else:
        return ["Error"]


@cache.memoize()
def rdap(query):
    if common.is_ip(query):
        base_url = 'https://www.rdap.net/ip/'
    else:
        base_url = 'https://www.rdap.net/domain/'

    response = requests.get(base_url + query)

    if response.status_code == 200:
        return response.json()
    else:
        return {"Error": "Not Found"}


@cache.memoize()
def find_cached(query):
    cache_providers = {
        "Wayback Machine": "https://web.archive.org/web/",
        "Google": "http://webcache.googleusercontent.com/search?q=cache:",
    }

    results = []

    for provider, url in cache_providers.items():
        try:
            response = requests.get(url + query)

            if response.status_code == 200:
                results.append((provider, url + query))
        except Exception:
            pass

    return results


@cache.memoize()
def get_redirect_url(query):
    try:
        if "http" not in query:
            query = "http://" + query

        return requests.get(query).url

    except Exception:
        pass


@cache.memoize()
def domain_registration_date(query):
    r = rdap(query)
    if len(r) > 2 and "events" in r:
        return r["events"][0]["eventDate"]

    w = dq_whois(query)
    if len(w) > 2:
        trim = "Creation Date: "
        creation = [item for item in w if trim in item]
        return creation[0].split(trim, 1)[1] if creation else []


@cache.memoize()
def domain_impersonation(query):
    scan = urlscan(query)
    return scan["verdicts"]["urlscan"]["brands"] if scan else []


api_function_mapping = {
            'virustotal': virustotal,
            'urlscan': urlscan,
            'geoip': geoip,
            'iana-whois': iana_whois,
            'dq-whois': dq_whois,
            'rdap': rdap,
            'redirect': get_redirect_url
        }
