"""
This file is for testing purposes of all sort of stuff, code here is non-production
"""
import asyncio
from http.server import SimpleHTTPRequestHandler
import socket
import select
import time


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

