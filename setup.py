from setuptools import setup, find_packages

setup(
    name="peertube_uploader",
    version="0.1.0",
    packages=find_packages(),
    # Include the top-level CLI module
    py_modules=["upload_folder_peertube"],
    install_requires=[
        "requests>=2.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        'dev': ['pytest'],
    },
    entry_points={
        "console_scripts": [
            "upload-folder-peertube=upload_folder_peertube:main",
        ],
    },
)