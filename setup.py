from setuptools import find_packages, setup

# https://setuptools.readthedocs.io/en/latest/setuptools.html

setup(
    name="dg",
    version="0.1.0",
    description="Data Gate CLI",
    url="https://github.com/IBM/data-gate-cli",
    download_url="https://github.com/IBM/data-gate-cli",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "asyncssh",
        "click<=8",
        "colorama",
        "click-option-group",
        "netifaces",
        "pyyaml",
        "requests",
        "semver",
        "tabulate",
        "tqdm",
        "urllib3",
    ],
    entry_points={"console_scripts": ["dg=dg.dg:cli"]},
    python_requires=">=3.8.0",
)
