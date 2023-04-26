from setuptools import setup
import subprocess
import os
from version import get_version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
   name='simpler_sf',
   version=get_version(),
   description="Extending Simple Salesforce to support Pandas exports and more.",
   license="MIT",
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='benvigano',
   author_email='beniamino.vigano@protonmail.com',
   url="https://github.com/benvigano/simpler-sf",
   keywords='Salesforce, Simple Salesforce, Pandas, Dataframe, Unpack Salesforce',
   packages=['simpler_sf'],
)
