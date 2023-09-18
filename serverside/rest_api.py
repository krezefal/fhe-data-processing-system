import sys
from flask import Flask, jsonify, request, Response

from request_handler import DBConn
from server_utils import parse_db_creds

app = Flask(__name__)
PORT = 8282


@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.json
    db.create_user(data=data.values())

    return Response(status=200)


@app.route("/get_user_info", methods=["GET"])
def get_user_info():
    login: str = request.args.get("login")
    response = db.get_user_info(login=login)

    return jsonify(response)


@app.route("/check_variable_exist", methods=["GET"])
def check_variable_exist():
    login: str = request.args.get("login")
    var_name: str = request.args.get("var_name")
    response = db.check_variable_exist(login=login, name=var_name)

    return jsonify(response)


@app.route("/get_variable", methods=["GET"])
def get_variable():
    login: str = request.args.get("login")
    var_name: str = request.args.get("var_name")
    response = db.get_variable(login=login, name=var_name)

    return jsonify(response)


@app.route("/get_memory", methods=["GET"])
def get_memory():
    login: str = request.args.get("login")
    response = db.get_memory(login=login)

    return jsonify(response)


@app.route("/init_new_variable", methods=["POST"])
def init_new_variable():
    data = request.json
    db.init_new_variable(var_data=data.values())

    return Response(status=200)


@app.route("/edit_value", methods=["POST"])
def edit_value():
    data = request.json

    login = data["login"]
    name = data["var_name"]
    value = data["value"]

    db.edit_value(login=login, var_name=name, value=value)

    return Response(status=200)


@app.route("/delete_variable", methods=["GET"])
def delete_variable():
    login: str = request.args.get("login")
    var_name: str = request.args.get("var_name")

    db.delete_variable(login=login, var_name=var_name)


@app.route("/calc_variables", methods=["POST"])
def calc_variables():
    data = request.json

    login = data["login"]
    var_name1 = data["var_name1"]
    var_name2 = data["var_name2"]
    var_name_res = data["var_name_res"]
    op = data["op"]

    response = db.calc_variables(login=login,
                                 var_name1=var_name1,
                                 var_name2=var_name2,
                                 var_name_res=var_name_res,
                                 op=op)

    return jsonify(response)


@app.route("/div_variables", methods=["POST"])
def div_variables():
    data = request.json

    login = data["login"]
    var_name1 = data["var_name1"]
    var_name2 = data["var_name2"]

    response = db.div_variables(login=login, var_name1=var_name1, var_name2=var_name2)

    return jsonify(response)


if __name__ == "__main__":
    db_creds = parse_db_creds(sys.argv[1:])
    db = DBConn(*db_creds)

    context = ('./serverside/openssl_certs_example/cert.pem',
               './serverside/openssl_certs_example/key.pem')
    app.run(host='localhost', port=PORT, debug=False, ssl_context=context)

    db.close_connection()
