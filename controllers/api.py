import flask
from flask import Blueprint
import common, lookup


api_routes = Blueprint('api_routes', __name__)


@api_routes.route('/api/<endpoint>', methods=['POST'])
def api_handler(endpoint):
	query = flask.request.form.get('query')

	if endpoint == "redirect":
		if query and common.is_url(query):
			redirected = lookup.get_redirect_url(query)
			return redirected if redirected else ("Error", 500)
		else:
			return "Missing params", 400

	return "Not Implemented", 501
