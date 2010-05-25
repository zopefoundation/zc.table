from setuptools import setup, find_packages

setup(
    name="zc.table",
    version="0.8.1",
    url="http://pypi.python.org/pypi/zc.table/",
    install_requires=[
        'setuptools',
        'zc.resourcelibrary >= 0.6',
        'zope.app.form',
        'zope.app.testing',
        'zope.cachedescriptors',
        'zope.component',
        'zope.formlib',
        'zope.i18n',
        'zope.interface',
        'zope.schema',
        'zope.testing',
    ],
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
