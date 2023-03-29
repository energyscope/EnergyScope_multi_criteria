from setuptools import setup, find_packages
import codecs
import os

HERE = os.path.abspath(os.path.dirname(__file__))

FINAL_RELEASE = open(os.path.join(HERE, 'VERSION')).read().strip()


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


setup(
    name='energyscope',
    author='',
    description='Energy Scope',
    packages=find_packages(),
    long_description=read('README.md'),
    include_package_data=True,
    use_scm_version={
        'version_scheme': 'post-release',
        'local_scheme': lambda version: version.format_choice("" if version.exact else "+{node}", "+dirty"),
        'fallback_version': FINAL_RELEASE,
    },
    python_requires='>=3.7',
    setup_requires=["setuptools_scm"],
    install_requires=[
        'numpy',
        'pandas',
        'pyyaml',
        'matplotlib',
        'plotly'
    ],
    keywords=[]
)
