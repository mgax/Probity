from setuptools import setup, find_packages

setup(
    name="Probity",
    description="Files and folders integrity checking tool.",
    version="0.1",
    url="http://github.com/alex-morega/probity",
    license="BSD License",
    author="Alex Morega",
    author_email="public@grep.ro",
    packages=find_packages(),
    install_requires=['PyYAML'],
    setup_requires=['nose>=0.11'],
    test_suite="nose.collector",
    entry_points={
        'console_scripts': [
            'probity = probity.cmd:main',
        ],
    },
)
