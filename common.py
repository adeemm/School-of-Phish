import base64
import re


# Decode URL-safe base64 encoding
def url_base64_decode(url):
    return base64.urlsafe_b64decode(url + '=' * (4 - len(url) % 4)).decode("utf-8")


# Returns hostname (including subdomain(s) and TLD) of a URL
def get_hostname(url):
    return re.search("([a-z0-9-]+\.)*[a-z0-9-]+\.[a-z]{2,}", url).group()


# Returns hostname (but this time ignoring subdomains) of a URL
def get_bare_hostname(url):
    return re.search("(www\.)?(([a-z0-9-]+\.)*([a-z0-9-]+\.[a-z]{2,}))", url).group(4)


# Returns the URL without its protocol identifier
def get_url_strip_protocol(url):
    return re.search("^(https?:\/\/)?(.+)", url).group(2)


# Returns the TLD of a URL
def get_tld(url):
    return re.search("([a-z0-9-]+\.)*[a-z0-9-]+(\.[a-z]{2,})", url).group(2)


# Returns the path of a URL
def get_path(url):
    if "/" in url:
        return get_url_strip_protocol(url).split("/", 1)[1]


# Checks if the input string is a valid IPv4 address
def is_ip(input):
    return bool(re.search("^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", input))


# Calculates the Jaro Wrinkler distance between two strings
def jaro_winkler(s1, s2):
    jaro_dist = jaro_distance(s1, s2)

    if jaro_dist > 0.7:
        # Find the length of common prefix
        prefix = 0

        for i in range(min(len(s1), len(s2))):
            if s1[i] == s2[i]:
                prefix += 1
            else:
                break

        # Max of 4 characters allowed in prefix
        prefix = min(4, prefix)
        jaro_dist += 0.1 * prefix * (1 - jaro_dist)

    return jaro_dist


# Calculates the Jaro distance between two strings
def jaro_distance(s1, s2):
    s1_len = len(s1)
    s2_len = len(s2)

    if s1 == s2:
        return 1.0

    if s1_len == 0 or s2_len == 0:
        return 0.0

    # Maximum matching distance
    max_dist = (max(s1_len, s2_len) // 2) - 1

    matches = 0
    s1_list = [0] * s1_len
    s2_list = [0] * s2_len

    for i in range(s1_len):
        for j in range(max(0, i - max_dist), min(s2_len, i + max_dist + 1)):
            if s1[i] == s2[j] and s2_list[j] == 0:
                s1_list[i] = 1
                s2_list[j] = 1
                matches += 1
                break

    if matches == 0:
        return 0.0

    transpositions = 0
    point = 0

    for i in range(s1_len):
        if s1_list[i]:
            while s2_list[point] == 0:
                point += 1

            if s1[i] != s2[point]:
                point += 1
                transpositions += 1
            else:
                point += 1

        transpositions /= 2

    return (matches / s1_len + matches / s2_len + (matches - transpositions) / matches) / 3.0
