
import os
import time
import unittest
from unittest import IsolatedAsyncioTestCase

from openSourceQueryProjectSrc.cacheManager.cacheManager import MemoryBasedCacheManager
from openSourceQueryProjectSrc.httpOutBoundRequestHandler.httpOutBoundRequestHandler import HttpRequestQueryReturnValues
from openSourceQueryProjectSrc.utils.logger import MyLogger


class TestMemoryBasedCacheManager(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        """
        This function creates the tested module
        :return:
        """
        self.tested_module = MemoryBasedCacheManager()
        script_directory = os.path.dirname(os.path.abspath(__file__))
        MyLogger.log_to_std("the script's folder is:" + script_directory)
        # This is not nice...
        configuration_file_name = "../../../openSourceIntSystemConfigurationFile.json"
        configuration_file_path = os.path.join(script_directory, configuration_file_name)
        MyLogger.log_to_std("the configuration file used full path is:" + configuration_file_path)

        if not self.tested_module.cache_manager_init(configuration_file_path):
            raise

        MyLogger.log_to_std("initialization passed well")

    def tearDown(self) -> None:
        """
        This function "nullifies" the tested module
        :return:
        """
        self.tested_module = None

    async def test_single_ip_address_query_from_cache(self):
        ip_address_to_check1 = "1.1.1.1"
        # mimic a situation where there is not an entry for the IP to check
        ret_val = self.tested_module.cache_manager_query_entry(ip_address_to_check1)
        self.assertEqual(ret_val, None, "None should have been returned")

        # mimic a response
        response_server_name = "ip-api"
        response_status = 200
        response_duration = 2
        response_body = "response body"
        response = HttpRequestQueryReturnValues(response_server_name, response_status, response_duration, response_body)
        response_list = [response]
        ret_val = self.tested_module.cache_manager_update_entry(ip_address_to_check1, response_list)
        self.assertEqual(ret_val, True, "Should have been True")

        # reduce the maximum duration of entry in the cache for testing
        self.tested_module.set_max_duration_of_item_in_cache_seconds(1)
        time.sleep(1)

        ret_val = self.tested_module.cache_manager_query_entry(ip_address_to_check1)
        self.assertEqual(ret_val, None, "Should return None")

        # set back the maximum duration of entry in the cache for a "larger value
        self.tested_module.set_max_duration_of_item_in_cache_seconds(3)
        ret_val = self.tested_module.cache_manager_update_entry(ip_address_to_check1, response_list)
        self.assertEqual(ret_val, True, "Should have been True")
        ret_val = self.tested_module.cache_manager_query_entry(ip_address_to_check1)
        self.assertNotEqual(ret_val, None, "Should NOT be None")

        # reduce the maximum number of item to a low number:
        self.tested_module.set_max_number_of_items_in_cache(2)
        ip_address_to_check2 = "2.2.2.2"
        ret_val = self.tested_module.cache_manager_update_entry(ip_address_to_check2, response_list)
        self.assertEqual(ret_val, True, "Should have been True")

        # now add the 3rd element --> this should fail
        ip_address_to_check3 = "3.3.3.3"
        ret_val = self.tested_module.cache_manager_should_add_entry()
        self.assertEqual(ret_val, False, "Should have been False")


suite = unittest.TestLoader().loadTestsFromTestCase(TestMemoryBasedCacheManager)
unittest.TextTestRunner(verbosity=2).run(suite)
