import os

from setuptools import find_packages, setup

import mentions

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setup(
    name="django-wm",
    version=mentions.__version__,
    packages=find_packages(),
    include_package_data=True,
    license="GPLv3",
    description="Webmention support for any Django model.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://beatonma.org/webmentions_tester/",
    project_urls={
        "Source": "https://github.com/beatonma/django-wm",
    },
    author="Michael Beaton",
    author_email="michael@beatonma.org",
    data_files=[
        (
            "",
            [
                "mentions/templates/webmention-submit-manual.html",
            ],
        ),
    ],
    install_requires=[
        "beautifulsoup4",
        "celery",
        "django",
        "mf2py",
        "requests",
    ],
    python_requires=">=3.7",
    tests_require=[
        "django-nose",
        "pinocchio",
    ],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
