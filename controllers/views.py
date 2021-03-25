import flask
from app import flask_app
from models import query
import common, heuristics, lookup, risk


@flask_app.route('/')
@flask_app.route('/search')
def search():
	return flask.render_template(
		'search.html'
	)


@flask_app.route('/domain/<domain>/risk')
def get_risk(domain):
	q = query.Query(domain)

	if q.err:
		flask.abort(500)
	else:
		return flask.render_template(
			'risk.html',
			query=q.query,
			risk_score=risk.get_risk_score(q.query, use_vt=False),
			heuristic=heuristics.run_tests(q.query),
			geo=lookup.geoip(q.hostname),
			register=lookup.domain_registration_date(q.bare),
			targeting=lookup.domain_impersonation(q.query)
		)


@flask_app.route('/domain/<domain>/blacklists')
def get_blacklists(domain):
	q = query.Query(domain)

	if q.err:
		flask.abort(500)
	else:
		return flask.render_template(
			'blacklist.html',
			query=q.query,
			vt=lookup.virustotal(q.query)
		)


@flask_app.route('/domain/<domain>/info')
def get_info(domain):
	q = query.Query(domain)

	if q.err:
		flask.abort(500)
	else:
		whois = lookup.dq_whois(q.bare)
		if len(whois) < 3 or whois[0].startswith("No match") or whois[1].startswith("No match"):
			whois = lookup.iana_whois(q.bare)

		dns = {}
		record_types = ["ANY", "A", "AAAA", "CAA", "CNAME", "MX", "NS", "PTR", "SOA", "SRV", "TXT"]
		for record in record_types:
			r = lookup.dig_dns(q.hostname, record)
			dns[record] = r

		return flask.render_template(
			'info.html',
			query=q.query,
			geo=lookup.geoip(q.hostname),
			whois=whois,
			dns=dns,
			rdap=lookup.rdap(q.bare)
		)


@flask_app.route('/domain/<domain>/webpage')
def get_page_info(domain):
	q = query.Query(domain)

	if q.err:
		flask.abort(500)
	else:
		return flask.render_template(
			'webpage.html',
			query=q.query,
			urlscan=lookup.urlscan(q.query)
		)


@flask_app.route('/domain/<domain>/preview')
def get_page_preview(domain):
	q = query.Query(domain)

	if q.err:
		flask.abort(500)
	else:
		return flask.render_template(
			'preview.html',
			query=q.query,
			cached=lookup.find_cached(q.query),
			urlscan=lookup.urlscan(q.query)
		)


@flask_app.route('/domain/<domain>/timeline')
def get_page_timeline(domain):
	q = query.Query(domain)

	if q.err:
		flask.abort(500)
	else:
		return flask.render_template(
			'timeline.html',
			query=q.query,
			urlscan=lookup.urlscan(q.query)
		)
