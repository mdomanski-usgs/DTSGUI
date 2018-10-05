from distutils.core import setup

setup(
    name='dtsgui',
    version='0.0.0dev1',
    packages=['dts'],
    url='https://github.com/mdomanski-usgs/DTSGUI',
    license='CC0 1.0',
    author='Marian Domanski',
    author_email='mdomanski@usgs.gov',
    description='Distributed Temperature Sensor GUI',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python 2.7'
    ],
    python_requires='==2.7.*',
)
