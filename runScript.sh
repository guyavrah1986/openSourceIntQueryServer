#!/bin/bash
echo "===== Start of script ======"
echo "Python3 version installed is:"
python3 --version

echo "Current working directory is:"
pwd
ls -l
cd project || exit
ls -l

# Create the virtual environment:
python3 -m venv openSourceQueryProjectSrc_env

# Source into it:
source openSourceQueryProjectSrc_env/bin/activate

# Install the server Python3 application
python3 setup.py install

# For debug:
pip3 list

# Run the Python application
python3 openSourceQueryProjectSrc/main.py /project/openSourceIntSystemConfigurationFile.json
#python3 -m unittest openSourceQueryProjectSrc.tests.httpOutBoundRequestHandler.test_httpOutBoundRequestHandler.TestHttpOutBoundGetRequestHandler.test_single_ip_address_get_request_from_single_source
# sudo -E env PATH=${PATH}
echo "===== End of script ======"