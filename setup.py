from setuptools import setup, find_packages

import os

here = os.path.abspath(os.path.dirname(__file__))
info = {}
with open(
        os.path.join(here, "zucleus", "__init__.py")) as f:
    exec(f.read(), None, info)

setup(name='zucleus',
        version=info["__version__"],
        description='Zucleus',
        packages=find_packages(),
        author=info["__author__"],
        author_email=info["__author_email__"],
        package_dir={'zucleus': 'zucleus'},
        install_requires=[
            "flask-restful"],
        entry_points={
            'console_scripts': [
                'zuserver = zucleus.server.zuserver:main',
                'zutest = zucleus.console.zutest:main'
                ]
            }
        )
