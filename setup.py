import finddata
from setuptools import setup, find_packages


setup(
    name="rqworker_dashboard",
    author="Florian Finke",
    author_email="flo@randomknowledge.org",
    version='0.1',
    packages=find_packages(),
    package_data=finddata.find_package_data(
        exclude_directories=finddata.standard_exclude_directories + ('RQWorkerDashboard',),
        exclude=finddata.standard_exclude + ('database.db',)),
    include_package_data=True,
)
