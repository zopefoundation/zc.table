from setuptools import setup, find_packages

setup(
    name="zc.table",
    version="0.5",
    install_requires=['zc.resourcelibrary >= 0.5'],
    dependency_links=['http://download.zope.org/distribution/',],
    packages=find_packages('src', exclude=["*.tests", "*.ftests"]),
    
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],
    package_data = {
    '': ['*.txt', '*.zcml', '*.gif', '*.js'],
    'zc.table':['resources/*'],
    },

    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description="""\
This is a Zope 3 extension that helps with the construction of (HTML) tables.
Features include dynamic HTML table generation, batching and sorting.
""",
    license='ZPL',
    keywords="zope zope3",
    )
