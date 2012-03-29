from setuptools import setup, find_packages

setup(
    name="zc.table",
    version="0.9.0dev",
    url="http://pypi.python.org/pypi/zc.table/",
    install_requires=[
        'setuptools',
        'zc.resourcelibrary >= 0.6',
        'zope.browserpage >= 3.10',
        'zope.formlib >= 4',
        'zope.cachedescriptors',
        'zope.component',
        'zope.formlib',
        'zope.i18n',
        'zope.interface',
        'zope.schema',
    ],
    extras_require=dict(
        test=['zope.testing',
              'zope.publisher']),
    packages=find_packages('src'),
    package_dir= {'':'src'},

    namespace_packages=['zc'],
    package_data = {
    '': ['*.txt', '*.zcml', '*.gif', '*.js'],
    'zc.table':['resources/*', '*.pt'],
    },

    author='Zope Project',
    author_email='zope-dev at zope.org',
    description="This is a Zope 3 extension that helps with the construction of (HTML) tables. Features include dynamic HTML table generation, batching and sorting.",
    long_description=open("README.txt").read() + '\n\n' + open('CHANGES.txt').read(),
    license='ZPL',
    keywords="zope zope3",
    zip_safe=False,
    classifiers = ['Framework :: Zope3'],
    )
