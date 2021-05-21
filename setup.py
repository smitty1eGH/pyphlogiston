from setuptools import setup, find_packages

setup(
    name="pyphlogiston",
    version="0.1",
    py_modules=["pyphlogiston"],
    packages=find_packages(),
    install_requires=["Click"],
    entry_points={'console_scripts':['pyphlogiston=pyphlogiston:main',],}
)
