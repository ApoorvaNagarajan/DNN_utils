from setuptools import setup, find_packages

setup(
    name = 'DNN_utils',
    version = '0.1.0',
    url = '',
    description = '',
    packages = find_packages(),
    include_package_data=True,
    install_requires = [
        # Github Private Repository - needs entry in `dependency_links`
        'DNN_utils'
    ],

    dependency_links=[
        # Make sure to include the `#egg` portion so the `install_requires` recognizes the package
        'git+ssh://git@github.com/ApoorvaNagarajan/DNN_utils.git#egg=DNN_utils'
    ]

)
