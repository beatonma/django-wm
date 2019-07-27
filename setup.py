import os
from setuptools import find_packages, setup
import mentions

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='django-wm',
    version=mentions.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3',
    description='Webmention support for any Django model.',
    long_description=README,
    long_description_content_type='text/x-rst',
    url='https://beatonma.org/django-wm',
    author='Michael Beaton',
    author_email='michael@beatonma.org',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ]
)
