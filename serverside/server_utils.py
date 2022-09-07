import getopt
import sys
from typing import Tuple
import yaml


def parse_db_creds(argv) -> Tuple[str, str, str, str]:
    with open('./serverside/db_creds.yaml', 'r') as file:
        config = yaml.safe_load(file)

    dbname = None
    user = None
    host = None
    password = None

    try:
        opts, args = getopt.getopt(argv, "hdb:u:ip:pw:", ["dbname=", "user=", "ip=", "password="])
    except getopt.GetoptError:
        print("rest_api.py -db <dbname> -u <user> -ip <host> -pw <password>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("rest_api.py -db <dbname> -u <user> -ip <host> -pw <password>")
            sys.exit()
        elif opt in ("-db", "--dbname"):
            dbname = arg
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-ip", "--ip"):
            host = arg
        elif opt in ("-pw", "--password"):
            password = arg

    if dbname is None:
        dbname = config['conn_credentials']['dbname']
    if user is None:
        user = config['conn_credentials']['user']
    if host is None:
        host = config['conn_credentials']['host']
    if password is None:
        password = config['conn_credentials']['password']

    return dbname, user, host, password
