import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='mentions',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3',
    description='Automatic webmentions for Django with minimal setup.',
    long_description=README,
    url='https://beatonma.org/django-wm',
    author='Michael Beaton',
    author_email='michael@beatonma.org',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python'
    ]
)
