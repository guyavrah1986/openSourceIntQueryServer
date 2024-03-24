"""
This file holds the main program function. This is the entry point that is used for this application.
"""
import asyncio
import sys

from openSourceQueryProjectSrc.utils.logger import MyLogger
from openSourceQueryProjectSrc.flaskServer.flaskServer import run_flask


async def main():
    MyLogger.log_to_std("----start----")
    run_flask(sys.argv[1])
    MyLogger.log_to_std("----end----")

if __name__ == "__main__":
    print("===== start =====")
    asyncio.run(main())
    print("===== end =====")
