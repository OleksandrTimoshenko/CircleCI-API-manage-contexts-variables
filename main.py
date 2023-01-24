import os
import json
import argparse
import http.client
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

conn = http.client.HTTPSConnection('circleci.com')


def parsing_parametrs():

    parser = argparse.ArgumentParser(
        description='CircleCI API',
        usage='use "%(prog)s --help" for more information',
        epilog="!!!WARNING!!!: Only the variables that are written in \
                the files ./files/value/<context_name>.txt will be affected")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--all',
                       action='store_true',
                       help='Update variables in all contexts')
    group.add_argument(
        '-c',
        '--context',
        type=str,
        help='Update variable in some conext(s) (comma separated)')
    parser.add_argument(
        '-l',
        '--list',
        action='store_true',
        help='Create file with all CircleCI variables names in ./files/variables')
    parser.add_argument('-del', '--deletion',
                        action='store_true',
                        help='Delete all variables from contexts')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Detailed output')
    parser.add_argument('-ap', '--auto_approve',
                        action='store_true',
                        help='Auto approve')

    return parser.parse_args()


def list_contexts(circle_ci_token, oraganisation_id):
    api = "/api/v2/context?owner-id="
    token = "&page-token=NEXT_PAGE_TOKEN"

    headers = {
        'Content-Type': 'application/json',
        'Circle-Token': circle_ci_token
    }

    url = api + oraganisation_id + token
    conn.request('GET', url, headers=headers)

    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data)
    contexts_dict = {}
    for item in json_data["items"]:
        contexts_dict[item["name"]] = item["id"]
    return contexts_dict


def get_vars(context_id, circle_ci_token):
    headers = {'Circle-Token': circle_ci_token}
    api = "/api/v2/context/"
    env = "/environment-variable?page-token=NEXT_PAGE_TOKEN"
    url = api + context_id + env
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    variables_list = []
    json_data = json.loads(data.decode("utf-8"))
    for item in json_data["items"]:
        variables_list.append(item["variable"])
    return variables_list


def get_variables_from_context(all_contexts, needed_contexts, circle_ci_token):
    if len(needed_contexts) == 0:
        for key in all_contexts:
            needed_contexts.append(key)
    variables_for_adding = {}
    for context_name, context_id in all_contexts.items():
        if context_name in needed_contexts:
            variables_for_adding[context_name] = get_vars(
                context_id, circle_ci_token)
    return variables_for_adding


def create_variables_list(variables_dict):
    filename = os.path.join(
        Path().resolve(),
        "./files/variables/CircleCI_variables_" +
        datetime.now().strftime("%d-%m-%Y_%H:%M:%S") +
        ".txt")
    file = open(filename, "w")
    for context_name, variables in variables_dict.items():
        variables_str = ''
        for var in variables:
            variables_str += "," + var
        file.write(context_name + ": " + variables_str[1:] + '\n')
    file.close()


def add_vars_to_the_context(
        context_id,
        context_name,
        ci_token,
        method,
        verbose):
    headers = {
        'Content-Type': 'application/json',
        'Circle-Token': ci_token
    }
    file_path = os.path.join(
        Path().resolve(),
        "./files/values/",
        context_name + ".txt")
    url = "/api/v2/context/"
    env2 = '/environment-variable/'
    # Read new value from file
    with open(file_path, 'r') as file:
        new_name = file.readlines()
    for line in new_name:
        data = line.split("=", 1)
        context_name = data[0]
        value = data[1]
        full_url = url + context_id + env2 + context_name
        payload = "{\"value\":\"" + value + "\"}"
        conn.request(method, full_url, payload, headers=headers)
        res = conn.getresponse()
        data1 = res.read()
        if verbose:
            if method == "PUT":
                print("Adding variable: " + full_url)
            elif method == "DELETE":
                print("Delete variable: " + full_url)
            print(data1.decode("utf-8"))


def user_confirm(context):
    print(
        "Do you really want to delete/update variables from context " +
        context +
        " y/n?")
    while True:
        agree = input()
        if agree.lower() == "y":
            agree = True
            break
        elif agree.lower() == "n":
            agree = False
            break
        else:
            print("Please enter 'y' or 'n'")
    return agree


def preparing_for_adding_variables(
        ci_token,
        all_contexts,
        needed_contexts,
        deletion,
        verbose,
        auto_approve):
    if len(needed_contexts) == 0:
        for key in all_contexts:
            needed_contexts.append(key)
    if deletion:
        method = "DELETE"
    else:
        method = "PUT"
    for my_context in needed_contexts:
        if auto_approve or user_confirm(my_context):
            add_vars_to_the_context(
                all_contexts[my_context],
                my_context,
                ci_token,
                method,
                verbose)


if __name__ == "__main__":
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv()
    params = parsing_parametrs()
    if not params.all:
        contexts_arr = params.context.split(",")
    else:
        contexts_arr = []
    contexts = list_contexts(
        os.environ.get('CIRCLE_CI_TOKEN'),
        os.environ.get('ORGANIZATION_ID'))
    vars_dict = get_variables_from_context(
        contexts, contexts_arr, os.environ.get('CIRCLE_CI_TOKEN'))
    if params.list:
        create_variables_list(vars_dict)
    preparing_for_adding_variables(
        os.environ.get('CIRCLE_CI_TOKEN'),
        contexts,
        contexts_arr,
        params.deletion,
        params.verbose,
        params.auto_approve)
