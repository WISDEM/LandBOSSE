import os
import setuptools

name = 'landbosse'
version = '2.3.0.3'

with open('README.md', 'r') as fh:
    long_description = fh.read()

PACKAGE_PATH = os.path.abspath(os.path.join(__file__, os.pardir))

setuptools.setup(
    url='https://github.com/WISDEM/LandBOSSE',
    name=name,
    version=version,
    author='NREL',
    author_email='Parangat.Bhaskar@nrel.gov',
    include_package_data=True,
    python_requires='>=3.6',
    description='LandBOSSE',
    long_description=long_description,
    long_description_content_type='text/markdown',
    # packages=['landbosse', 'landbosse.model','landbosse.excelio','landbosse.tests', 'landbosse.landbosse_api'], # uncomment this line when uploading a new pip installable version
    # packages=setuptools.find_packages(PACKAGE_PATH, "test"),
    packages=setuptools.find_packages(PACKAGE_PATH, "test"),
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[
        'pandas==1.0.3',
        'numpy==1.17.2',
        'sympy==1.4',
        # 'scipy==1.3.1', # use this line when uploading a new version of pip_installable
        'scipy',
        'xlsxwriter==1.2.1',
        'xlrd==1.2.0',
        'pytest==5.3.5'
        # 'pscyopg2-binary==2.8.4',
        # 'sqlalchemy==1.3.13'
    ],

    command_options={
            'build_sphinx': {
                'project': ('setup.py', name),
                'version': ('setup.py', version),
                # 'release': ('setup.py', release),  # Not yet needed
                'source_dir': ('setup.py', 'docs')}}
)
