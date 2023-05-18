from setuptools import setup

setup(name='indiek-mockdb',
      python_requires='>=3.8',
      version='0.1.6',
      description='mock database for indiek',
      long_description='''This is an on-the-fly in-memory mock Database used by indiek-core
      for development and testing purposes.''',
      author='Adrian Ernesto Radillo',
      author_email='adrian.radillo@gmail.com',
      license='GNU Affero General Public License v3.0',
      packages=['indiek.mockdb'],
      install_require=['frozendict'],
      extras_require={'dev': ['pytest', 'pytest-pep8', 'pytest-cov']})
