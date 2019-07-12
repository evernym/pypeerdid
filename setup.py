import pathlib
from setuptools import setup
import sys

v = sys.version_info
if sys.version_info < (3, 5):
    v = sys.version_info
    print("FAIL: Requires Python 3.5 or later, but setup.py was run using %s.%s.%s" % (v.major, v.minor, v.micro))
    print("NOTE: Installation failed. Run setup.py using python3")
    sys.exit(1)

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="peerdid",
    version="0.1.1",
    description="Python Peer DID Library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/evernym/pypeerdid",
    author="Daniel Hardman",
    author_email="daniel.hardman@gmail.com",
    license="Apache 2.0",
    keywords="did decentralized identity",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta"
    ],
    packages=["peerdid"],
    #include_package_data=True,      -- write a MANIFEST.in with glob patterns if uncommented
    install_requires=[],
    download_url='https://github.com/evernym/pypeerdid/archive/v0.1.1.tar.gz',
)
