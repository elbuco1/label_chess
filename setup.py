import io
import os
from pathlib import Path

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'chlabel'
DESCRIPTION = 'Desktop app to annotate chessgames'
URL = 'https://github.com/elbuco1/label_chess'
EMAIL = 'lrtboucaud@gmail.com'
AUTHOR = "Laurent Boucaud"
REQUIRES_PYTHON = '>=3.9,<3.10'


def list_reqs(fname='requirements.txt'):
    with open(fname) as fd:
        return fd.read().splitlines()


INSTALL_REQUIRES = list_reqs(fname='requirements.txt')
# TEST_REQUIRES = list_reqs(fname='requirements-test.txt')

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Load the package's __version__.py module as a dictionary.
ROOT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = ROOT_DIR / NAME
# MODEL_FILE = PACKAGE_DIR/ "models/model.joblib"

about = {}
with open(PACKAGE_DIR / 'VERSION') as f:
    _version = f.read().strip()
    about['__version__'] = _version

setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    package_data={'chlabel': [
        'VERSION', 'resources/pieces/*']},
    install_requires=INSTALL_REQUIRES,
    include_package_data=False,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: No License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
