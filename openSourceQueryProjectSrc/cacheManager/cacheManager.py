"""
This file holds unit tests implementations for the MemoryBasedCacheManager. As the name suggests, this caching
mechanism is implemented in a way such that the content of it is stored as part of the process memory.
It follows the following set of rules:
- Due to the fact that it is memory based, in order for it not to "exhaust" the memory consumption of the process, it
is limited with maximum number of items that can be kept in the cache. This fact, has off course some downsides in case
the process CAN have more than the configured amount of maximum items. It is in the hands of the user to set it
in an optimal way according to his needs and resources.
- The "refresh" mechanism of the cache is conducted upon a query for some key in a way that if the entry is found
and is "too old" --> it is removed. This way there is no need to have some "background thread" which is responsible
to perform cleaning" of the cache every once in a while. However, the downside of this approach is that there might
be situations that "more popular" entries won't make it into the cache until the "less popular old ones" will leave
it.
NOTES:

"""
import abc
import datetime
import json

from openSourceQueryProjectSrc.utils.utils import HttpRequestQueryReturnValues, synchronized
from openSourceQueryProjectSrc.utils.logger import MyLogger


class CacheManagerEntry:
    """
    This class is a simple "container" for an entry in the cache.
    """
    def __init__(self, curr_time_stamp, value: list):
        self.__last_insertion_time = curr_time_stamp
        # the value is of type HttpRequestQueryReturnValues
        self.__value = value

    def get_last_insertion_time(self):
        return self.__last_insertion_time

    def get_value(self):
        return self.__value


# Add in order to have some functions synchronized:
synchronizer = synchronized()


class CacheManagerInterface(metaclass=abc.ABCMeta):
    """
    This is the caching mechanism interface.
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, "cache_manager_init") and
                callable(subclass.load_data_source) and
                hasattr(subclass, "cache_manager_query_entry") and
                hasattr(subclass, "cache_manager_update_entry") and
                hasattr(subclass, "cache_manager_should_add_entry") and
                callable(subclass.extract_text) or
                NotImplemented)

    @abc.abstractmethod
    def cache_manager_init(self, config_file: str) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def cache_manager_query_entry(self, key: str) -> HttpRequestQueryReturnValues:
        raise NotImplementedError

    @abc.abstractmethod
    def cache_manager_update_entry(self, key: str, value: list) -> bool:
        raise NotImplementedError

    def cache_manager_should_add_entry(self) -> bool:
        raise NotImplementedError


class MemoryBasedCacheManager(CacheManagerInterface):

    def __init__(self):
        self.__max_duration_of_item_in_cache_seconds = None
        self.__max_number_of_items_in_cache = None
        self.__ip_address_to_response_dict = {}
        MyLogger.log_to_std("created an instance")

    def get_ip_address_to_response_dict(self) -> dict:
        return self.__ip_address_to_response_dict

    def set_max_duration_of_item_in_cache_seconds(self, max_duration: int):
        self.__max_duration_of_item_in_cache_seconds = max_duration

    def set_max_number_of_items_in_cache(self, max_num_items: int):
        self.__max_number_of_items_in_cache = max_num_items

    def cache_manager_init(self, config_file: str) -> bool:
        if config_file is None or not config_file:
            MyLogger.log_to_std("invalid or empty configuration file")
            return False

        try:
            f = open(config_file)
        except FileNotFoundError:
            MyLogger.log_to_std("unable to open file for reading")
            return False
        else:
            with f:
                data = json.load(f)

        cache_manager_config_info = data["cacheManager"]
        self.__max_duration_of_item_in_cache_seconds = cache_manager_config_info["maxNumOfItemsInCache"]
        self.__max_number_of_items_in_cache = cache_manager_config_info["maxDurationOfItemInCacheSeconds"]
        MyLogger.log_to_std("parsed the following values \n"
                            + "maxNumOfItemsInCache:" + str(self.__max_number_of_items_in_cache) + "\n"
                            + "maxDurationOfItemInCacheSecond:" + str(self.__max_duration_of_item_in_cache_seconds))
        return True

    @synchronizer
    def cache_manager_query_entry(self, key: str) -> list:
        if key is None or not key:
            MyLogger.log_to_std("key is None or empty!")
            return None

        MyLogger.log_to_std("searching for key:" + key + " in the cache dictionary")
        value = self.__ip_address_to_response_dict.get(key, None)
        if value is None:
            MyLogger.log_to_std("key:" + key + " is NOT in the cache")
            return None

        current_datatime = datetime.datetime.now()
        current_time_stamp = current_datatime.timestamp()
        entry_current_time_stamp = value.get_last_insertion_time()
        if current_time_stamp - entry_current_time_stamp > self.__max_duration_of_item_in_cache_seconds:
            MyLogger.log_to_std("key:" + key + " is too much time in the cache, removing it")
            del self.__ip_address_to_response_dict[key]
            return None

        MyLogger.log_to_std("key:" + key + " is in the cache, returning it")
        return value.get_value()

    @synchronizer
    def cache_manager_update_entry(self, key: str, value: list) -> bool:
        if key is None or not key:
            MyLogger.log_to_std("invalid key (None or empty)")
            return False

        current_datatime = datetime.datetime.now()
        entry_time_stamp = current_datatime.timestamp()
        updated_cache_entry = CacheManagerEntry(entry_time_stamp, value)
        self.__ip_address_to_response_dict[key] = updated_cache_entry
        MyLogger.log_to_std("key:" + key + " was successfully inserted into the cache at:" + str(current_datatime))
        return True

    @synchronizer
    def cache_manager_should_add_entry(self) -> bool:
        # -1 indicates ALWAYS add to cache (unlimited)
        if self.__max_number_of_items_in_cache == -1:
            return True

        if len(self.__ip_address_to_response_dict) >= self.__max_number_of_items_in_cache:
            return False

        return True
