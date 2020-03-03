import setuptools

name = 'landbosse'
version = '2.1.5'

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    url='https://github.com/WISDEM/LandBOSSE',
    name=name,
    version=version,
    author='NREL',
    author_email='alicia.key@nrel.gov',
    description='LandBOSSE',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['landbosse'],
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[
        'pandas==0.25.2',
        'numpy',
        'sympy',
        'scipy',
        'shapely',
        'xlsxwriter',
        'xlrd',
        'psycopg2-binary',
        'sqlalchemy'
    ],
    command_options={
            'build_sphinx': {
                'project': ('setup.py', name),
                'version': ('setup.py', version),
                # 'release': ('setup.py', release),  # Not yet needed
                'source_dir': ('setup.py', 'docs')}}
)
