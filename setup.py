from setuptools import setup, find_packages

setup(
    name='nifi_flow_summary',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'ijson',
        'pyyaml',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'nifi-flow-summary = nifi_flow_summary.cli:main'
        ]
    }
)
