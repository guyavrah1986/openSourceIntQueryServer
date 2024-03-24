1. This is the very basic needed in order to "kick off" a Python based project.
It is based on the virtual environment concept (note that in a containerized
application case, this is not so crucial anymore...).

2. In order to install the git repo (the project) do the following:

3. In order to run the several unit tests for the different modules of the system do the following:
- Navigate to the project's main folder:
$ cd openSourceQueryProjectSrc
- source the virtual environment
$ source openSourceQueryProjectSrc_env/bin/activate
- Run some unit tests, for example, for the HttpOutBoundGetRequestHandler module:
$ python3 -m unittest openSourceQueryProjectSrc/tests/module1/test_httpOutBoundGetRequestHandler.py
