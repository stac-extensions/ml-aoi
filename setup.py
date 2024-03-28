import logging
import os
import sys
from typing import Optional, Set, Tuple

from setuptools import find_packages, setup

CUR_DIR = os.path.abspath(os.path.dirname(__file__))

# ensure that 'weaver' directory can be found for metadata import
sys.path.insert(0, CUR_DIR)
sys.path.insert(0, os.path.join(CUR_DIR, os.path.split(CUR_DIR)[-1]))

CUR_PKG = os.path.basename(CUR_DIR)
LOGGER = logging.getLogger(f"{CUR_PKG}.setup")
if logging.StreamHandler not in LOGGER.handlers:
    LOGGER.addHandler(logging.StreamHandler(sys.stdout))  # type: ignore # noqa
LOGGER.setLevel(logging.INFO)
LOGGER.info("starting setup")


def read_doc_file(*file_names: str) -> Optional[Tuple[str, str]]:
    for file_name in file_names:
        for ext, ctype in [("md", "text/markdown"), ("rst", "text/x-rst")]:
            file_path = os.path.join(CUR_DIR, f"{file_name}.{ext}")
            if os.path.isfile(file_path):
                with open(file_path, mode="r", encoding="utf-8") as doc_file:
                    return doc_file.read(), ctype


CHANGE, CHANGE_CTYPE = read_doc_file("CHANGES", "CHANGELOG")
README, README_CTYPE = read_doc_file("README")
LONG_DESCRIPTION = LONG_DESCRIPTION_CTYPE = None
if CHANGE or README:
    LONG_DESCRIPTION = f"{README}\n\n{CHANGE}"
    LONG_DESCRIPTION_CTYPE = README_CTYPE or CHANGE_CTYPE


def _parse_requirements(file_path, requirements, links):
    # type: (str, Set[str], Set[str]) -> None
    """
    Parses a requirements file to extra packages and links.

    :param file_path: file path to the requirements file.
    :param requirements: pre-initialized set in which to store extracted package requirements.
    :param links: pre-initialized set in which to store extracted link reference requirements.
    """
    if not os.path.isfile(file_path):
        return
    with open(file_path, "r") as requirements_file:
        for line in requirements_file:
            # ignore empty line, comment line or reference to other requirements file (-r flag)
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if "git+https" in line:
                pkg = line.split("#")[-1]
                links.add(line.strip())
                requirements.add(pkg.replace("egg=", "").rstrip())
            elif line.startswith("http"):
                links.add(line.strip())
            else:
                requirements.add(line.strip())


LOGGER.info("reading requirements")
# See https://github.com/pypa/pip/issues/3610
# use set to have unique packages by name
LINKS = set()
REQUIREMENTS = set()
DOCS_REQUIREMENTS = set()
TEST_REQUIREMENTS = set()
_parse_requirements("requirements.txt", REQUIREMENTS, LINKS)
_parse_requirements("requirements-doc.txt", DOCS_REQUIREMENTS, LINKS)
_parse_requirements("requirements-dev.txt", TEST_REQUIREMENTS, LINKS)
LINKS = list(LINKS)
REQUIREMENTS = list(REQUIREMENTS)

LOGGER.info("base requirements: %s", REQUIREMENTS)
LOGGER.info("docs requirements: %s", DOCS_REQUIREMENTS)
LOGGER.info("test requirements: %s", TEST_REQUIREMENTS)
LOGGER.info("link requirements: %s", LINKS)

AUTHORS = {
    "Francis Charette-Migneault": "francis.charette.migneault@gmail.com",
}

# this is automatically updated by 'make bump'
VERSION = "0.2.0"

setup(
    name="pystac-ml-aoi",
    version=VERSION,
    description="Implementation of pystac utilities for STAC ML-AOI extension.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CTYPE,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Pydantic",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: System :: Distributed Computing",
    ],
    author=", ".join(AUTHORS.keys()),
    author_email=", ".join(AUTHORS.values()),
    url="https://github.com/stac-extensions/ml-aoi",
    download_url=f"https://github.com/stac-extensions/ml-aoi/archive/refs/tags/{VERSION}.zip",
    license="Apache License 2.0",
    keywords=" ".join([
        "STAC",
        "pystac",
        "Machine Learning",
        "Area of Interest",
        "Annotation",
        "Geospatial",
    ]),
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["*.json"]},
    zip_safe=False,
    test_suite="tests",
    python_requires=">=3.8, <4",
    install_requires=REQUIREMENTS,
    dependency_links=LINKS,
    extras_require={
        "docs": DOCS_REQUIREMENTS,
        "dev": TEST_REQUIREMENTS,
        "test": TEST_REQUIREMENTS,
    },
    entry_points={
    }
)
