from os import path
from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()
with open(
    path.join(path.abspath(path.dirname(__file__)), "README.md"), encoding="utf-8"
) as f:
    long_description = f.read()

PACKAGE_KEYWORDS = [
    "cisco",
    "dna",
    "dnacenter",
    "python",
    "api",
    "sdk",
    "netbox",
]

setup(
    name="netbox-ciscodnac-plugin",
    version="4.0.1",
    description="Cisco DNA Center Integration with NetBox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/erichester76/netbox_ciscodnac_plugin",
    author="Robert Csapo",
    author_email="rcsapo@cisco.com",
    license="CISCO SAMPLE CODE LICENSE",
    install_requires=requirements,
    packages=find_packages(exclude=["img", "dev"]),
    include_package_data=True,
    python_requires=">=3.3",
    zip_safe=False,
)
