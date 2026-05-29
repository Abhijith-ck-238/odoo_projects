from flask import Flask, jsonify, request
from flask_cors import CORS
import xmlrpc.client
import os
import logging
from datetime import datetime
from random import randint

app = Flask(__name__)
CORS(app)

# ------------------------
# CONFIG (Use environment variables)
# ------------------------
ODOO_URL = os.getenv("ODOO_URL", "http://109.123.246.211")
ODOO_DB = os.getenv("ODOO_DB", "Alitkan_18_live")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "your_password_here")

# ------------------------
# Logging Setup
# ------------------------
logging.basicConfig(
    filename="/tmp/flask_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------
# Utility Functions
# ------------------------
def generate_reference(n=8):
    return str(randint(10**(n-1), (10**n)-1))


def encode_files(data, files):
    if not files:
        return data
    for key, value in files.items():
        if value:
            data[key] = value.encode().decode("ascii")
    return data


# ------------------------
# Odoo API Wrapper
# ------------------------
class OdooAPI:

    def __init__(self):
        self.common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        self.uid = self.common.authenticate(
            ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {}
        )

        if not self.uid:
            raise Exception("Authentication failed")

    def execute(self, model, method, *args, **kwargs):
        return self.models.execute_kw(
            ODOO_DB,
            self.uid,
            ODOO_PASSWORD,
            model,
            method,
            args,
            kwargs
        )


# ------------------------
# ROUTES
# ------------------------

@app.route("/api", methods=["POST"])
def create_applicant():
    try:
        content = request.get_json()
        data = content.get("data", {})
        files = content.get("files", {})

        api = OdooAPI()

        data = encode_files(data, files)
        ref = generate_reference()
        data["external_ref"] = ref

        # Create candidate
        candidate_id = api.execute(
            "hr.candidate", "create",
            {"partner_name": data["name"]}
        )

        data["candidate_id"] = candidate_id
        data.pop("name")

        applicant_id = api.execute("hr.applicant", "create", data)

        logging.info(f"Applicant created: {applicant_id}")

        return jsonify({"created": True, "ref": ref})

    except Exception as e:
        logging.error(str(e))
        return jsonify({"created": False, "error": str(e)})


@app.route("/api/get", methods=["GET"])
def get_jobs():
    try:
        api = OdooAPI()

        jobs = api.execute(
            "hr.job",
            "search_read",
            [[("id", "!=", 0)]],
            fields=[
                "name", "description", "opening_date",
                "state", "card_image", "city", "private_job"
            ]
        )

        public_jobs = [job for job in jobs if not job["private_job"]]

        return jsonify(public_jobs)

    except Exception as e:
        logging.error(str(e))
        return jsonify([])


@app.route("/api/check", methods=["POST"])
def check_status():
    try:
        ref = request.get_json().get("ref")

        if not ref or len(ref) != 8:
            return jsonify({"id": "empty", "msg": "Invalid reference number"})

        api = OdooAPI()

        result = api.execute(
            "hr.applicant",
            "search_read",
            [[("external_ref", "=", ref)]],
            fields=["stage_id"],
            limit=1
        )

        if result:
            return jsonify({
                "id": result[0]["stage_id"][0],
                "msg": result[0]["stage_id"][1]
            })

        return jsonify({"id": "empty", "msg": "No application found"})

    except Exception as e:
        logging.error(str(e))
        return jsonify({"id": "error", "msg": "Something went wrong"})


@app.route("/api/description", methods=["GET"])
def get_description():
    try:
        job_id = int(request.args.get("job_id"))
        api = OdooAPI()

        job = api.execute(
            "hr.job",
            "read",
            [job_id],
            fields=[
                "name", "city", "type_of_position",
                "technical_knowledge", "behavioral_competencies",
                "education_language_requirements", "notes",
                "department_id", "description", "state"
            ]
        )

        if job:
            return jsonify({"found": True, "job": job[0]})

        return jsonify({"found": False})

    except Exception as e:
        logging.error(str(e))
        return jsonify({"found": False})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
