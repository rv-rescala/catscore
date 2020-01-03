from setuptools import setup, find_packages

# https://github.com/pypa/sampleproject/blob/master/setup.py
setup(
    name='catscore',
    version='0.1',
    description='Core library for cats project',
    author='rv',
    author_email='yo-maruya@rescala.jp',
    keywords='sample setuptools development',
    install_requires=['requests','bs4', 'selenium' , 'lxml'],
    url='https://rescala.jp',
    license='MIT',
    packages=find_packages(exclude=('tests')),
    python_requires='>=3.5',
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/rv-rescala/catscore/issues',
        'Source': 'https://github.com/rv-rescala/catscore'
    }
)
