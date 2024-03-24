# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Get general updates and set the Python repository as one of apt repositories
RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa

# Install some Python 3.10 and its "fundamental" modules
RUN apt-get install -y build-essential python3.10 python3.10-dev python3-pip python3.10-venv
RUN apt-get install -y git

# Update pip
RUN python3.10 -m pip install pip --upgrade
RUN python3.10 -m pip install wheel

# Copy the installation script and the source files of the project
RUN mkdir project
COPY setup.py project/setup.py
COPY openSourceQueryProjectSrc project/openSourceQueryProjectSrc
COPY runScript.sh project/runScript.sh
COPY openSourceIntSystemConfigurationFile.json project/openSourceIntSystemConfigurationFile.json

RUN chmod +x project/runScript.sh


# Run a bash command to display Python version when the container starts
CMD ["bash", "-c", "project/runScript.sh"]


