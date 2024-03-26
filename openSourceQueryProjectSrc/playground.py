"""
This file is for testing purposes of all sort of stuff, code here is non-production
"""
from http.server import SimpleHTTPRequestHandler
import socket
import select
import time
import urllib.request
from urllib.request import Request

from openSourceQueryProjectSrc.utils.logger import MyLogger
from openSourceQueryProjectSrc.httpOutBoundRequestHandler.httpOutBoundRequestHandler import HttpRequestQueryReturnValues


def compose_aggregate_response():
    result_list = []
    request_return_values = HttpRequestQueryReturnValues("ip-api", 200, 1, "ip-api contents")
    result_list.append(request_return_values)
    request_return_values = HttpRequestQueryReturnValues("bgpview", 200, 2, "bgpview contents")
    result_list.append(request_return_values)


def tmp_func():
    # Get socket file descriptor as a TCP socket using the IPv4 address family
    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set some modes on the socket, not required but it's nice for our uses
    listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host_name = "127.0.0.1"
    port = 80
    address_port = (host_name, port)
    # serve address and port
    listener_socket.bind(address_port)
    # listen for connections, a maximum of 1
    listener_socket.listen(1)
    MyLogger.log_to_std("Server listening @ " + host_name + ":" + str(port))

    # loop indefinitely to continuously check for new connections
    while True:
        # Poll the socket to see if there are any newly written data, note excess data dumped to "_" variables
        read_ready_sockets, _, _ = select.select(
            [listener_socket],  # list of items we want to check for read-readiness (just our socket)
            [],  # list of items we want to check for write-readiness (not interested)
            [],  # list of items we want to check for "exceptional" conditions (also not interested)
            0  # timeout of 0 seconds, makes the method call non-blocking
        )
        # if a value was returned here then we have a connection to read from
        if read_ready_sockets:
            # select.select() returns a list of readable objects, so we'll iterate, but we only expect a single item
            for ready_socket in read_ready_sockets:
                # accept the connection from the client and get its socket object and address
                client_socket, client_address = ready_socket.accept()

                # read up to 4096 bytes of data from the client socket
                client_msg = client_socket.recv(4096)
                print(f"Client said: {client_msg.decode('utf-8')}")

                # Send a response to the client, notice it is a byte string
                client_socket.sendall(b"Welcome to the server!\n")
                try:
                    # close the connection
                    client_socket.close()
                except OSError:
                    # client disconnected first, nothing to do
                    pass


class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    try:

        def do_GET(self):
            print("got url:" + self.path)
            # Shared Queue of Background Tasks
            asyncio.get_event_loop().run_until_complete(MyHttpRequestHandler.asyncio_func())

            self.send_response(200)
            self.wfile.write(bytes("Ok", "utf8"))

    except Exception as e:
        print(str(e))

    @staticmethod
    async def asyncio_func():
        try:
            print('asyncio_func')
            self.asyncio_usage_sample_code()
            #winsound.PlaySound("SystemExit", winsound.SND_ALIAS)

        # Maybe you want to add Error handling
        finally:
            pass

    async def asyncio_usage_sample_code(self) -> None:
        MyLogger.log_to_std("start")
        tasks = []
        start_time = time.time()
        # Create and gather async tasks in a loop
        for i in range(3):
            task = asyncio.create_task(run_task(i + 1))
            tasks.append(task)

        # Await the completion of all tasks and get their results
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed_time = end_time - start_time
        MyLogger.log_to_std("tasks ran within:" + str(elapsed_time) + " seconds")

        # Print the results
        for result in results:
            print(result)
            MyLogger.log_to_std(result)

        MyLogger.log_to_std("end")

import asyncio
from flask import Flask
import json
from flask import Response
import sys
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


loop = asyncio.get_event_loop()
app = Flask(__name__)


def thread_per_server(server_name: str):
    # Create run loop for this thread and block until completion
    MyLogger.log_to_std("executing thread work for server:" + server_name)


def handle_get_dispatcher(ip: str):
    """
    This method initiate thread for every server present in the
    server list. This way, all the queries to each server are
    executed each in a different thread and within each of these
    usage in asyncio function is done in order run tasks concurrently
    """
    MyLogger.log_to_std("starting dispatching threads to handle IP:" + ip)
    thread_per_server_list = []
    server_list = ["server-1, server-2", "server-3"]
    thread_pool = ThreadPoolExecutor(len(server_list))
    MyLogger.log_to_std("created thread pool executor with:" + str(len(server_list)) + " worker threads")
    for server in server_list:
        thread_per_server_list.append(thread_pool.submit(thread_per_server, server))

    MyLogger.log_to_std("BEFORE calling wait on the list of threads")
    wait(thread_per_server_list, timeout=None, return_when=ALL_COMPLETED)
    MyLogger.log_to_std("AFTER calling wait on the list of threads")

@app.route("/<ip>", methods=["GET"])
async def get_handle(ip):
    MyLogger.log_to_std("Got IP address in the request:" + str(ip))
    handle_get_dispatcher(ip)
    status = 400
    dummy_reply = "reply for IP:" + str(ip)
    """
    if valid_ip_list:
        reply = await handle_get_request(valid_ip_list)
        MyLogger.log_to_std("return to client the following reply:" + str(reply).replace("\\", ""))
        reply = json.dumps(str(reply).replace("\\", ""))
        reply = json.loads(reply)
        status = 200
    else:
        reply = utils_aggregate_result_from_all_requests(valid_ip_list)
    """
    reply = json.dumps(str(dummy_reply).replace("\\", ""))
    reply = json.loads(reply)
    response = Response(response=reply, status=status, mimetype="application/json")
    response.headers["Content-Type"] = "application/json"
    response.headers["Access-Control-Allow-Origin"] = "*"
    MyLogger.log_to_std("about to return reponse:" + str(response)
                        + " to query for IP:" + str(ip))
    return response


def run_flask_tmp(config_file: str):
    local_http_server_listening_address = "0.0.0.0"
    local_http_server_port = 8080
    MyLogger.log_to_std("about to start HTTP server @ " + local_http_server_listening_address + ":"
                        + str(local_http_server_port))
    app.run(debug=True, host=local_http_server_listening_address, port=local_http_server_port, threaded=True)


async def main():
    MyLogger.log_to_std("----start----")
    run_flask_tmp(sys.argv[1])
    MyLogger.log_to_std("----end----")


def test_func():
    # https://api.iplocation.net/?ip=8.8.8.8
    protocol = "https://"
    url = "api.iplocation.net/?ip="
    ip_address_to_query = "8.8.8.8"

    request_url = protocol + url + ip_address_to_query
    req = Request(url=request_url)
    req.add_header("User-Agent", "Mozilla/5.0")
    req_timeout_sec = 10
    response = urllib.request.urlopen(req, timeout=req_timeout_sec)
    return_code = response.getcode()
    contents = response.read()
    MyLogger.log_to_std("return code when requesting IP:" + ip_address_to_query + " is:" + str(return_code))


if __name__ == "__main__":
    print("===== start =====")
    test_func()
    # asyncio.run(main())
    print("===== end =====")