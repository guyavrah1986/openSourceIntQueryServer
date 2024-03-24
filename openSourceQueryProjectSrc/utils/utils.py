"""
This file holds all sort of general purposes utilities functions, class definitions, etc...
"""
from functools import wraps
import json
import netaddr
from threading import RLock

from openSourceQueryProjectSrc.utils.logger import MyLogger


class HttpRequestQueryReturnValues:
    """
    This class is a simple "container" class for the relevant information that needs to be
    retrieved about some query, such as:
    return_code: What was the status of the HTTP request towards the server
    query_duration: How long did it take
    response: The actual content of the response
    """
    def __init__(self, server_name: str, return_code: int, query_duration: float, response):
        self.server_name = server_name
        self.return_code = return_code
        self.query_duration = query_duration
        self.response = response


def utils_check_valid_ip(str_ip) -> bool:
    if netaddr.valid_ipv4(str_ip) is True:
        print("IP is IPv4")
        return True
    else:
        if netaddr.valid_ipv6(str_ip) is True:
            print("IP is IPv6")
            return True

    return False


def utils_extract_ip_addresses(ip_list_from_url: str) -> list:
    MyLogger.log_to_std("got IP:" + str(ip_list_from_url))
    # split according to ","
    tokens = ip_list_from_url.split(",")
    for token in tokens:
        MyLogger.log_to_std("token is:" + token)
    valid_ip_list = []
    for addr_candidate in tokens:
        if utils_check_valid_ip(addr_candidate) is True:
            valid_ip_list.append(addr_candidate)

    return valid_ip_list


def utils_convert_status_code_to_string(status_code: int) -> str:
    if status_code == 200:
        return "success"

    return "failure"


def utils_aggregate_result_from_all_requests(result_list: list):
    MyLogger.log_to_std("got results list of size:" + str(len(result_list)))
    entire_data = {"metrics": {}, "raw_data": {}}
    total_duration = 0
    total_response_code = 200
    if len(result_list) == 0:
        total_response_code = 400

    for response in result_list:
        entire_data["metrics"][response.server_name] = {}
        entire_data["metrics"][response.server_name]["status"] = utils_convert_status_code_to_string(response.return_code)
        entire_data["metrics"][response.server_name]["time"] = response.query_duration
        total_duration += response.query_duration
        if response.return_code != 200:
            total_response_code = 400

        if response.response is None:
            entire_data["raw_data"][response.server_name] = ""
        else:
            entire_data["raw_data"][response.server_name] = response.response.decode("utf-8")

    entire_data["metrics"]["total"] = {}
    entire_data["metrics"]["total"]["status"] = utils_convert_status_code_to_string(total_response_code)
    entire_data["metrics"]["total"]["time"] = total_duration
    json_output = json.dumps(entire_data, indent=4)
    return json_output


def synchronized():
    lock = RLock()

    def wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            with lock:
                return f(*args, **kwargs)
        return inner_wrapper
    return wrapper
