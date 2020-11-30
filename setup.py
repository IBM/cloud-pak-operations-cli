from setuptools import find_packages, setup

# https://setuptools.readthedocs.io/en/latest/setuptools.html

setup(
    name="dg",
    version="0.1.0",
    description="Data Gate CLI",
    url="https://github.ibm.com/Everest/dg",
    download_url="https://github.ibm.com/Everest/dg",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "asyncssh",
        "click",
        "colorama",
        "pyyaml",
        "requests",
        "semver",
        "tabulate",
        "tqdm",
        "urllib3 < 1.26.0",
    ],
    entry_points={"console_scripts": ["dg=dg.dg:cli"]},
    python_requires=">=3.9.0",
)
