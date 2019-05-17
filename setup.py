from setuptools import setup

from sphinx.setup_command import BuildDoc

name = 'DTSGUI'
version = '1.0'
release = '1.0.0'
cmdclass = {'build_sphinx': BuildDoc}
docs_source = 'docs/'
docs_build_dir = 'docs/_build'
docs_builder = 'html'

setup(
    name=name,
    version=release,
    packages=['dts'],
    url='https://github.com/mdomanski-usgs/DTSGUI',
    license='CC0 1.0',
    author='Marian Domanski',
    author_email='mdomanski@usgs.gov',
    description='Distributed Temperature Sensor GUI',
    classifiers=[
        'Programming Language :: Python 2.7'
    ],
    python_requires='==2.7.*',
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'source_dir': ('setup.py', docs_source),
            'build_dir': ('setup.py', docs_build_dir),
            'builder': ('setup.py', docs_builder)}
    }
)
