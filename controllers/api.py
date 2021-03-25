import flask
from app import flask_app
import common, lookup


@flask_app.route('/api/<endpoint>', methods=['POST'])
def api_handler(endpoint):
	query = flask.request.form.get('query')

	if endpoint == "redirect":
		if query and common.is_url(query):
			redirected = lookup.get_redirect_url(query)
			return redirected if redirected else ("Error", 500)
		else:
			return "Missing params", 400

	return "Not Implemented", 501
