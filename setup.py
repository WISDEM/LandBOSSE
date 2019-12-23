import setuptools

name = 'landbosse'
version = '1.1.2'

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    url='https://github.com/WISDEM/LandBOSSE',
    name=name,
    version=version,
    author='NREL',
    author_email='Parangat.Bhaskar@nrel.gov',
    include_package_data=True,
    install_requires=[
        'pandas==0.25.1',
        'numpy==1.17.2',
        'sympy==1.4',
        'scipy==1.3.1',
        'shapely==1.6.4.post2',
        'xlsxwriter==1.2.1',
        'xlrd==1.2.0',
        'pytest==5.2.1'
    ],
    python_requires='>=3.7',
    description='LandBOSSE',
    long_description=long_description,
    long_description_content_type='text/markdown',
    # packages=setuptools.find_packages(),
    packages=['landbosse', 'landbosse.model','landbosse.excelio','landbosse.tests', 'landbosse.landbosse_api'],
    test_suite='nose.collector',
    tests_require=['nose'],
    command_options={
            'build_sphinx': {
                'project': ('setup.py', name),
                'version': ('setup.py', version),
                # 'release': ('setup.py', release),  # Not yet needed
                'source_dir': ('setup.py', 'docs')}}
)
