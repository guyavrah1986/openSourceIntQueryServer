"""
This file holds unit tests implementations for the HttpOutBoundRequestHandler.
IMPORTANT NOTES:
- In the below tests, a usage in "hard coded" IP addresses that are assumed to be valid is made.
- Also, in order for the unit tests to run, it is assumed that the executable will have internet access.
--> both of these assumptions are NOT valid assumptions for unit testing purposes.
The unit testing were written like so ONLY for some TDD development purposes!
"""
import os
import unittest
from unittest import IsolatedAsyncioTestCase

from openSourceQueryProjectSrc.cacheManager.cacheManager import MemoryBasedCacheManager
from openSourceQueryProjectSrc.httpOutBoundRequestHandler.httpOutBoundRequestHandler import HttpOutBoundRequestHandler
from openSourceQueryProjectSrc.utils.logger import MyLogger
from openSourceQueryProjectSrc.utils.utils import utils_aggregate_result_from_all_requests, HttpRequestQueryReturnValues


class TestHttpOutBoundGetRequestHandler(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        """
        This function creates the tested module
        :return:
        """
        script_directory = os.path.dirname(os.path.abspath(__file__))
        MyLogger.log_to_std("the script's folder is:" + script_directory)
        configuration_file_name = "../../../openSourceIntSystemConfigurationFile.json"
        self.configuration_file_path = os.path.join(script_directory, configuration_file_name)

        # create the cache memory object
        self.mem_based_cache_manager = MemoryBasedCacheManager()
        ret_val = self.mem_based_cache_manager.cache_manager_init(self.configuration_file_path)
        if not ret_val:
            raise

        self.tested_module = HttpOutBoundRequestHandler(self.mem_based_cache_manager)
        if not self.tested_module.http_request_handler_init_handler(self.configuration_file_path):
            raise

    def tearDown(self) -> None:
        """
        This function "nullifies" the tested module
        :return:
        """
        self.tested_module = None

    async def test_single_ip_address_get_request(self):
        ip_address_to_check_list = ["176.228.193.161"]
        response_list = await self.tested_module.http_request_handler_handle_response_for_ip_addresses(ip_address_to_check_list)
        utils_aggregate_result_from_all_requests(response_list)

        # we queried only one IP
        response = response_list[0]

        expected_status_code = 200
        # we expect it to be successful
        self.assertEqual(response.return_code, expected_status_code, "Should be successful")

        # check again the same IP address
        response_list = await self.tested_module.http_request_handler_handle_response_for_ip_addresses(ip_address_to_check_list)
        utils_aggregate_result_from_all_requests(response_list)

        # we queried only one IP
        response = response_list[0]
        expected_status_code = 200
        # we expect it to be successful also
        self.assertEqual(response.return_code, expected_status_code, "Should be successful")

    async def test_single_ip_address_get_request_when_entry_in_cache(self):
        print("================================START===================================")
        print("=========test_single_ip_address_get_request_when_entry_in_cache=========")
        ip_address_to_check = "176.228.193.161"
        # set up the CacheManager for this scenario
        server_name = "ip-api"
        response_status = 200
        response_duration = 2
        response_body = "response body"
        response = HttpRequestQueryReturnValues(server_name, response_status, response_duration, response_body)
        ret_val = self.mem_based_cache_manager.cache_manager_update_entry(ip_address_to_check, response)
        self.assertEqual(ret_val, True, "Should have been True")

        ip_address_to_check_list = [ip_address_to_check]
        ret_val = await self.tested_module.http_request_handler_handle_response_for_ip_addresses(ip_address_to_check_list)
        print("=========test_single_ip_address_get_request_when_entry_in_cache=========")
        print("================================END===================================")


suite = unittest.TestLoader().loadTestsFromTestCase(TestHttpOutBoundGetRequestHandler)
unittest.TextTestRunner(verbosity=2).run(suite)
