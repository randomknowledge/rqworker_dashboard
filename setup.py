from setuptools import setup
import finddata


setup(
    name="rqworker_dashboard",
    author="Florian Finke",
    author_email="flo@randomknowledge.org",
    version='0.1.2',
    packages=['rqworker_dashboard'],
    package_data=finddata.find_package_data(),
    url='https://git.randomknowledge.org/rqworker_dashboard',
    include_package_data=True,
    license='MIT',
    description='rqworker_dashboard is a django app that provides a simple'
                ' dashboard for RQ (Redis Queue).'
                ' Inspired by https://github.com/nvie/rq-dashboard',
    long_description=open('Readme.md').read(),
    zip_safe=False,
    install_requires=['Django==1.4', 'raven==1.8.1', 'rq', 'psutil==0.4.1'],
    dependency_links=['https://github.com/nvie/rq/tarball/master#egg=rq'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
)
