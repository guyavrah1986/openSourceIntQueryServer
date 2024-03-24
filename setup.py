from setuptools import setup, find_packages

setup(name='openSourceQueryProjectSrc',
      version='0.1',
      description='Draft project for a simple project in Python 3',
      # url='https://github.com/myProjectGitHubPage',
      author='Guy Avraham',
      # author_email='mymail@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      install_requires=["flask[async]", "netaddr"])
