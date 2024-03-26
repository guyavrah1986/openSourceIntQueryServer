"""
This file holds the implementation of the flask server that is being used as the hosting HTTP server
"""
import asyncio
from flask import Flask
import json
from flask import Response

from openSourceQueryProjectSrc.cacheManager.cacheManager import MemoryBasedCacheManager
from openSourceQueryProjectSrc.httpOutBoundRequestHandler.httpOutBoundRequestHandler import HttpOutBoundRequestHandler
from openSourceQueryProjectSrc.utils.logger import MyLogger
from openSourceQueryProjectSrc.utils.utils import utils_aggregate_result_from_all_requests, utils_extract_ip_addresses

# Globals to handle the requests:
mem_based_cache = MemoryBasedCacheManager()
http_outbound_request_handler = HttpOutBoundRequestHandler(mem_based_cache)

# Defaults, can be over-written via configuration file if desired
local_http_server_port = 8080
local_http_server_listening_address = "0.0.0.0"


def init_global_objects(configuration_file_path: str) -> bool:
    MyLogger.log_to_std("about to initialize the relevant components of the system")
    MyLogger.log_to_std("the configuration file used full path is:" + configuration_file_path)
    if not mem_based_cache.cache_manager_init(configuration_file_path):
        MyLogger.log_to_std("had issues trying to initialize the memory based cache, aborting")
        return False

    if not http_outbound_request_handler.http_request_handler_init_handler(configuration_file_path):
        MyLogger.log_to_std("had issues trying to initialize the HTTP request handler, aborting")
        return False

    with open(configuration_file_path) as f:
        data = json.load(f)

    global local_http_server_port
    local_http_server_port = data["localHttpServerInfo"]["port"]
    MyLogger.log_to_std("extracted local_http_server_port from configuration file:" + str(local_http_server_port))
    return True


async def handle_get_request(ip_address_to_query_list: list):
    MyLogger.log_to_std("got IP list:" + str(ip_address_to_query_list))
    response_list = await http_outbound_request_handler.http_request_handler_handle_response_for_ip_addresses(
        ip_address_to_query_list)

    result_list = response_list
    MyLogger.log_to_std("result_list for IP list:" + str(ip_address_to_query_list) + " is:" + str(result_list))
    my_server_reply = utils_aggregate_result_from_all_requests(result_list)
    return my_server_reply


loop = asyncio.get_event_loop()
app = Flask(__name__)


@app.route("/<ip>", methods=["GET"])
async def get_handle(ip):
    valid_ip_list = utils_extract_ip_addresses(ip)
    # In case any IP appears more than once, keep the list unique values
    valid_ip_list = list(set(valid_ip_list))
    MyLogger.log_to_std("after removal of duplications:" + str(valid_ip_list))
    MyLogger.log_to_std("the list of valid IP address got in the request is:" + str(valid_ip_list))
    status = 400
    if valid_ip_list:
        reply = await handle_get_request(valid_ip_list)
        MyLogger.log_to_std("return to client the following reply:" + str(reply).replace("\\", ""))
        reply = json.dumps(str(reply).replace("\\", ""))
        reply = json.loads(reply)
        status = 200
    else:
        reply = utils_aggregate_result_from_all_requests(valid_ip_list)

    response = Response(response=reply, status=status, mimetype="application/json")
    response.headers["Content-Type"] = "application/json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


def run_flask(config_file: str):
    if not init_global_objects(config_file):
        return

    MyLogger.log_to_std("about to start HTTP server @ " + local_http_server_listening_address + ":"
                        + str(local_http_server_port))
    app.run(debug=True, host=local_http_server_listening_address, port=local_http_server_port, threaded=True)
