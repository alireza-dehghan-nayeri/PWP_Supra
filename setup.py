from setuptools import find_packages, setup

setup(
    name="food_manager",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "blinker==1.9.0",
        "click==8.1.8",
        "Flask==3.1.0",
        "Flask-SQLAlchemy==3.1.1",
        "itsdangerous==2.2.0",
        "MarkupSafe==3.0.2",
        "SQLAlchemy==2.0.37",
        "typing_extensions==4.12.2",
        "Werkzeug==3.1.3",
        "pytest==8.3.4",
        "flask_restful==0.3.10",
        "flask_Caching==2.3.1",
        "pylint==3.3.4",
        "jsonschema==4.17.3",
        "pytest==8.3.4",
        "flasgger==0.9.7.1",
        "pyyaml==6.0.2",

    ],
    entry_points={
        "console_scripts": [
            "foodmanager-dev = runserver:main",
        ]
    },
)
