from flask import Flask
from flask import request
from werkzeug.utils import secure_filename
from policy_engine.policy_engine import PolicyEngine
from flask import jsonify


app = Flask(__name__, static_url_path='', static_folder="frontend/app")

def create_error_response(reason="Error"):
	return jsonify({"success": False, "message": reason}), 400

def create_ok_response(message={}):
	return jsonify(message), 200

@app.route("/api/v1/policies", methods=['GET', 'POST'])
def get():
	"""
	Return all policies
	"""
	if request.method == "GET":
		policies = PolicyEngine().list_policies()
		return create_ok_response([{"id": idx, "policy": policy, "enabled": False} for idx, policy in enumerate(policies)])
	if request.method == "POST":
		print(request.form)
		args = {}
		if request.args.get('from_json'):
			args = {
				'data': request.form,
				'from_json': True
			}
		elif request.get_data() is not None:
			args = {
				'data': request.get_data().decode('UTF-8'),
				'from_json': False
			}
		else:
			return create_error_response("No data were provided")
		try:
			PolicyEngine().add_policy(**args)
		except Exception as e:
			return create_error_response("Error while parsing policy")

		filename = request.args.get('filename')
		if filename is None:
			create_error_response("No filename was specified")

		filename = secure_filename(filename)
		## TODO Create the file on a separate thread
		with open('./policy_engine/policies/' + filename + '.yaml', 'w+') as pf:
			pf.write(data)

		return create_ok_response("Successfully added policy {0}".format(filename))
	

@app.route("/api/v1/policies/<int:policy_id>", methods=['GET', 'PUT', 'DELETE'])
def CRUD_policy(policy_id):
	if request.method == "GET":
		policy = PolicyEngine().get_policy(policy_id)
		if policy is None:
			return create_error_response("Invalid policy ID")
		return create_ok_response(policy)