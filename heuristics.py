import common
import datetime
import lookup
import math
from models.heuristic import Heuristic
import re


# Returns a dict with the results of each heuristic test
def run_tests(url):
    results = []
    stripped = common.get_url_strip_protocol(url)
    hostname = common.get_hostname(url)
    bare = common.get_bare_hostname(url)
    tld = common.get_tld(url)

    if count_dots(hostname) > 3:
        results.append(Heuristic("Multiple subdomains", "Phishing domains usually have more subdomains designed to fool users", 0.35))
    if count_hyphens(hostname) > 1:
        results.append(Heuristic("Hyphens in hostname", "Hyphens can be used to pad URLs and masquerade as legitimate sites", 0.15))
    if entropy(hostname) > 3.7:
        results.append(Heuristic("High entropy hostname", "Phishing domains usually have a higher entropy than legitimate domains", 0.3))
    if count_length(hostname) > 20:
        results.append(Heuristic("Long hostname", "Phishing domains are usually longer than legitimate domains", 0.3))
    if check_pattern(hostname):
        results.append(Heuristic("Suspicious TLD pattern in hostname", "Phishing domains use these patterns to try to masquerade as legitimate domains", 0.75))
    if check_keywords(hostname):
        results.append(Heuristic("Suspicious keywords", "This domain contains suspicious keywords", 0.35))
    if check_tld(tld):
        results.append(Heuristic("Suspicious TLD", "This TLD is less common in legitimate domains and is often used by phishing websites", 0.2))
    
    if count_special(url) > 0:
        results.append(Heuristic("Special characters in URL", "Special characters are not very common in legitimate domains", 0.1))
    if count_at_sign(url) > 0:
        results.append(Heuristic("\"@\" in URL", "In URLs everything preceding @ often gets ignored", 0.1))
    if count_double_slash(stripped) > 0:
        results.append(Heuristic("Double slash in URL", "\"//\" Could indicate a redirect", 0.01))
    if count_colon(stripped) > 0:
        results.append(Heuristic("Port number in URL", "\":\" Specifies a port number, which isn't common among legitimate domains", 0.4))
    if get_url_len_ratio(stripped) >= 1:
        results.append(Heuristic("High URL length ratio", "(Ratio of hostname to path), legitimate URLs usually have a ratio of < 1", 0.05))

    if common.is_ip(url):
        results.append(Heuristic("IP Address", "Legitimate websites usually have a domain name, and not just an IP address", 0.5))

    if check_domain_registration(bare):
        results.append(Heuristic("Recently Registered", "This domain was registered less than 1 year ago", 0.75))

    # Mutually exclusive impersonation checks
    if check_domain_impersonation(url):
        results.append(Heuristic("Impersonation", "This domain is trying to impersonate a legitimate one", 1))
    elif 0.8 < check_closeness(bare) < 1:
        results.append(Heuristic("Possible Impersonation", "This domain could be trying to impersonate a legitimate one", 0.25))

    return results


# No. of dots in hostname
# Suspicious (> 3)
def count_dots(hostname): 
    return hostname.count(".")


# No. of hyphens in hostname
# Suspicious (> 1)
def count_hyphens(hostname): 
    return hostname.count("-")


# Calculates Shannon entropy of a hostname
# Suspicious (> 3.7)
def entropy(hostname):
        prob = [float(hostname.count(c)) / len(hostname) for c in dict.fromkeys(list(hostname))]
        return -sum([p * math.log(p) / math.log(2.0) for p in prob])


# Calculates the length of a hostname
# Suspicious (> 20)
def count_length(hostname):
    return len(hostname)


# No. of special characters in URL
# Suspicious (> 0)
def count_special(url):
    return len(re.findall("[!$~*_,()';]", url))


# Check if URL contains "@"
# Suspicious (> 0)
def count_at_sign(url): 
    return url.count("@")


# Check if URL contains "//" (outside of protocol identifier)
# Suspicious (> 0)
def count_double_slash(url):
    return url.count("//")


# Check if URL specifies a port number (outside of protocol identifier)
# Suspicious (> 0)
def count_colon(url):
    return url.count(":")


# Check URL length ratio (ratio of hostname to path)
# Suspicious (>= 1)
def get_url_len_ratio(url):
    if "/" not in url:
        return 0
    else:
        delimited = url.split("/")
        hostname_len = len(delimited[0])
        path_len = len(''.join(delimited[1:]))
        return (hostname_len / path_len) if path_len != 0 else 0


# Check for suspicious TLD patterns in hostname
# Suspicious (True)
def check_pattern(hostname):
    suspicious = ["-com.", ".net-", ".org-", ".com-", ".net.", ".org.", ".com.", ".gov-", ".gov.", ".gouv-", "-gouv-", ".gouv."]
    return any(tld in hostname for tld in suspicious)


# Check for suspicious keywords in hostname
# Suspicious (True)
def check_keywords(hostname):
    suspicious = ["login", "log-in", "sign-in", "signin", "account", "verification", "verify", "password", "credential", "support", "security", "update", "authentication", "authenticate", "authorize", "wallet", "alert", "purchase", "transaction", "recover", "unlock", "confirm", "office", "service", "manage", "portal", "invoice", "secure", "customer", "client", "bill", "online", "safe", "form", "appleid", "apple-id", "icloud", "itunes", "bank"]
    return any(sus in hostname for sus in suspicious)


# Check if hostname is impersonating by checking string closeness using Jaro-Winkler similarity
# Suspicious (0.8 < x < 1)
def check_closeness(hostname):
    impersonation = ["clemson", "google", "facebook", "apple"]

    try:
        name = hostname.split(".", 1)[0]
        return max(common.jaro_winkler(brand, name) for brand in impersonation)

    except Exception:
        pass


# Check for uncommon TLD
# Suspicious (True)
def check_tld(tld):
    suspicious = [".ga", ".gq", ".ml", ".cf", ".tk", ".xyz", ".pw", ".cc", ".club", ".work", ".top", ".support", ".bank", ".info", ".study", ".click", ".country", ".stream", ".gdn", ".mom", ".xin", ".kim", ".men", ".loan", ".download", ".racing", ".online", ".center", ".ren", ".gb", ".win", ".review", ".vip", ".party", ".tech", ".science", ".business"]
    return any(sus in tld for sus in suspicious)


# Get domain registration date
# Suspicious (True) (if registered within 1 year)
def check_domain_registration(bare):
    curr_date = datetime.datetime.utcnow()
    one_year = datetime.timedelta(days=365)
    registration = lookup.domain_registration_date(bare)

    try:
        register_date = datetime.datetime.strptime(registration, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        register_date = datetime.datetime.strptime(registration, '%Y-%m-%dT%H:%M:%S.%fZ')
    except Exception:
        return False

    if registration and curr_date - one_year < register_date:
        return True


# Check for impersonation
# Suspicious (True)
def check_domain_impersonation(url):
    if len(lookup.domain_impersonation(url)) > 0:
        return True
