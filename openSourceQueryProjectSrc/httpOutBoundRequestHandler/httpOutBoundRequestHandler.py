"""
This file holds the implementation of the HttpOutBoundRequestHandler class along other relevant classes/definitions.
The role of the HttpOutBoundRequestHandler class is to handle an HTTP request towards some open source API in order
to query meta-data about some IP address(es). The query for will be towards all the defined open source servers.
"""
import abc
import asyncio
import json
import urllib.request
import time
from urllib.request import Request

from openSourceQueryProjectSrc.cacheManager.cacheManager import MemoryBasedCacheManager
from openSourceQueryProjectSrc.utils.logger import MyLogger
from openSourceQueryProjectSrc.utils.utils import HttpRequestQueryReturnValues


class HttpOutBoundRequestHandlerInterface(metaclass=abc.ABCMeta):
    """
    This class represents the interface of the HTTP outbound request handler.
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "http_request_handler_init_handler") and
                callable(subclass.load_data_source) and
                hasattr(subclass, "http_request_handler_handle_response_for_ip_addresses") and
                callable(subclass.extract_text) or
                NotImplemented)

    @abc.abstractmethod
    def http_request_handler_init_handler(self, config_file: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def http_request_handler_handle_response_for_ip_addresses(self, ip_addresses: list) -> list:
        raise NotImplementedError


class OpenSourceServerInterface(metaclass=abc.ABCMeta):
    """
    This class represents the interface for any potential OpenSourceServer
    classes.
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "open_source_server_compose_req") and
                hasattr(subclass, "open_source_server_get_server_name") and
                callable(subclass.load_data_source) and
                callable(subclass.extract_text) or
                NotImplemented)

    @abc.abstractmethod
    def open_source_server_compose_req(self, ip_addr_to_query: str) -> Request:
        raise NotImplementedError

    @abc.abstractmethod
    def open_source_server_get_server_name(self) -> str:
        raise NotImplementedError


class OpenSourceServer(OpenSourceServerInterface):
    """
    This class implements the OpenSourceServerInterface by returning
    the "common" part of the HTTP request for the two open source
    servers that were given in the description of the task.
    """
    def __init__(self, name: str, protocol: str, url: str):
        self.__name = name
        self.__protocol = protocol
        self.__url = url

    def open_source_server_compose_req(self, ip_addr_to_query: str) -> Request:
        request_full_url = self.__protocol + "://" + self.__url + ip_addr_to_query
        req = Request(url=request_full_url)
        return req

    def open_source_server_get_server_name(self) -> str:
        return self.__name


class OpenSourceServerWithHeader(OpenSourceServer):
    """
    This server implementation adds "on top of its parent"
    the addition of the dummy header to avoid the HTTP error 403
    phenomena that takes place when running a script and not
    executing the request from a "real browser"
    """
    def __init__(self, name: str, protocol: str, url: str):
        OpenSourceServer.__init__(self, name, protocol, url)

    def open_source_server_compose_req(self, ip_addr_to_query: str) -> Request:
        req = OpenSourceServer.open_source_server_compose_req(self, ip_addr_to_query)
        # In order to overcome the HTTP 403 error, add "dummy" User-Agent header
        req.add_header("User-Agent", "Mozilla/5.0")
        return req


class HttpOutBoundRequestHandler(HttpOutBoundRequestHandlerInterface):

    def __init__(self, mem_based_cache_manager: MemoryBasedCacheManager):
        MyLogger.log_to_std("created an instance")
        self.__mem_based_cache_manager = mem_based_cache_manager
        # default, can be altered via configuration
        self.__req_timeout = 120
        self.__open_source_server_dict = {}

    def http_request_handler_init_handler(self, config_file: str) -> bool:
        if config_file is None or not config_file:
            MyLogger.log_to_std("got an invalid name for the configuration file")
            return False

        MyLogger.log_to_std("got the configuration file:" + config_file)
        return self.__parse_configuration_file(config_file)

    async def http_request_handler_handle_response_for_ip_addresses(self, ip_addresses: list) -> list:
        if ip_addresses is None or not ip_addresses:
            MyLogger.log_to_std("invalid input or empty list - returning")
            return []

        MyLogger.log_to_std("about to handle the request for the following IP addresses:" + str(ip_addresses))
        # TODO:  for now, take only the first IP address
        ip_address_to_check = ip_addresses[0]
        ret_val = await self.__run_query_for_single_ip_address(ip_address_to_check)
        return ret_val

    async def __run_query_for_single_ip_address(self, ip_addr_to_query: str) -> list:
        # first, check if the IP is in the cache. This call is to
        # a "synchronized" function because it reads from the cache
        # which is accessible for write operations as well from other
        # threads!
        ret_val = self.__mem_based_cache_manager.cache_manager_query_entry(ip_addr_to_query)
        if ret_val is not None:
            MyLogger.log_to_std("entry for IP:" + ip_addr_to_query + " was found in cache, returning")
            return ret_val

        task_list = []
        for server_name, server_obj in self.__open_source_server_dict.items():
            MyLogger.log_to_std("adding an async task to initiate HTTP(S) query to server:"
                                + server_name)
            task = asyncio.create_task(self.__run_request_towards_single_open_source_server(server_obj, ip_addr_to_query))
            task_list.append(task)

        MyLogger.log_to_std("added total of " + str(len(task_list)) + " async tasks")
        results_list = await asyncio.gather(*task_list)
        for result in results_list:
            MyLogger.log_to_std("return code for server:" + result.server_name + " is:" + str(result.return_code))

        # Just before returning, we update the cache with the new/modified entry
        # TODO: Maybe we wish to change the population of the cache to a different policy
        if self.__mem_based_cache_manager.cache_manager_should_add_entry():
            self.__mem_based_cache_manager.cache_manager_update_entry(ip_addr_to_query, results_list)

        return results_list

    async def __run_request_towards_single_open_source_server(self, server_obj: OpenSourceServerInterface,
                                                              ip_addr_to_query: str) -> HttpRequestQueryReturnValues:
        request = server_obj.open_source_server_compose_req(ip_addr_to_query)
        MyLogger.log_to_std("about to send the following request:" + request.get_full_url())

        # send the request
        exception_raised = False
        start_time = time.time()
        try:
            response = urllib.request.urlopen(request, timeout=self.__req_timeout)
        except TimeoutError:
            MyLogger.log_to_std("TimeoutError when running query of:" + ip_addr_to_query + " to server:"
                                + server_obj.open_source_server_get_server_name())
            exception_raised = True
        # This can probably be "fine-tuned", I tried to go for the "most case scenario" in the case above
        except:
            MyLogger.log_to_std("exception when running query of:" + ip_addr_to_query + " to server:"
                                + server_obj.open_source_server_get_server_name())
            exception_raised = True

        end_time = time.time()
        query_duration = end_time - start_time
        if not exception_raised:
            return_code = response.getcode()
            contents = response.read()
        else:
            return_code = 400
            contents = None

        request_return_values = HttpRequestQueryReturnValues(server_obj.open_source_server_get_server_name(),
                                                             return_code, query_duration, contents)
        MyLogger.log_to_std("response status code is:" + str(return_code))
        return request_return_values

    def __parse_configuration_file(self, config_file: str) -> bool:
        with open(config_file) as f:
            data = json.load(f)

        self.__req_timeout = data["reqeustHandler"]["maxReqTimeOutSeconds"]
        servers = data["servers"]
        for server_name, server_info in servers.items():
            protocol = server_info["protocol"]
            url = server_info["url"]
            if protocol == "http":
                open_source_server = OpenSourceServer(server_name, protocol, url)
            else:
                open_source_server = OpenSourceServerWithHeader(server_name, protocol, url)

            self.__open_source_server_dict[server_name] = open_source_server

        return True

