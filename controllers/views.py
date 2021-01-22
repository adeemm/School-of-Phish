import flask
from app import flask_app
import common, heuristics, lookup, risk, random, os


# TODO: https://stackoverflow.com/questions/31750655/pass-variables-to-all-jinja2-templates-with-flask


@flask_app.route('/')
@flask_app.route('/search')
def search():
	return flask.render_template(
		'search.html'
	)


@flask_app.route('/api/<endpoint>', methods=['POST'])
def api_handler(endpoint):
	query = flask.request.form.get('query')

	if endpoint == "redirect":
		if query:
			return lookup.get_redirect_url(query)
		else:
			return "Missing params", 400

	return "Not Implemented", 501


@flask_app.route('/domain/<domain>/risk')
def get_risk(domain):
	query = common.url_base64_decode(domain)
	hostname = common.get_bare_hostname(query)

	return flask.render_template(
		'risk.html',
		query=query,
		risk_score=risk.get_risk_score(query, use_vt=False),
		heuristic=heuristics.run_tests(query),
		geo=lookup.geoip(hostname),
		register=lookup.domain_registration_date(hostname),
		targeting=lookup.domain_impersonation(query)
	)


@flask_app.route('/domain/<domain>/blacklists')
def get_blacklists(domain):
	query = common.url_base64_decode(domain)

	return flask.render_template(
		'blacklist.html',
		query=query,
		vt=lookup.virustotal(query)
	)


@flask_app.route('/domain/<domain>/info')
def get_info(domain):
	query = common.url_base64_decode(domain)
	hostname = common.get_hostname(query)
	bare = common.get_bare_hostname(query)

	whois = lookup.dq_whois(bare)
	if len(whois) < 3 or whois[0].startswith("No match") or whois[1].startswith("No match"):
		whois = lookup.iana_whois(bare)

	dns = {}
	record_types = ["ANY", "A", "AAAA", "CAA", "CNAME", "MX", "NS", "PTR", "SOA", "SRV", "TXT"]
	for record in record_types:
		r = lookup.dig_dns(hostname, record)
		dns[record] = r

	return flask.render_template(
		'info.html',
		query=query,
		geo=lookup.geoip(hostname),
		whois=whois,
		dns=dns,
		rdap=lookup.rdap(bare)
	)


@flask_app.route('/domain/<domain>/webpage')
def get_page_info(domain):
	query = common.url_base64_decode(domain)

	return flask.render_template(
		'webpage.html',
		query=query,
		urlscan=lookup.urlscan(query)
	)


@flask_app.route('/domain/<domain>/preview')
def get_page_preview(domain):
	query = common.url_base64_decode(domain)

	return flask.render_template(
		'preview.html',
		query=query,
		cached=lookup.find_cached(query),
		urlscan=lookup.urlscan(query)
	)


@flask_app.route('/domain/<domain>/timeline')
def get_page_timeline(domain):
	query = common.url_base64_decode(domain)

	return flask.render_template(
		'timeline.html',
		query=query,
		urlscan=lookup.urlscan(query)
	)
