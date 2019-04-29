import os
from setuptools import find_packages, setup
from dj_ansible import __version__, __author__, __license__

with open("README.md", "r") as fh:
    long_description = fh.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ansible',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['ansible'],
    license=__license__,
    description='Django app which provide an APIs to integrate Ansible with Django projects',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email='aaqrabaw@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
