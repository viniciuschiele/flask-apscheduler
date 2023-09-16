from setuptools import setup

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Flask-APScheduler",
    version="1.13.0",
    packages=["flask_apscheduler"],
    url="https://github.com/viniciuschiele/flask-apscheduler",
    license="Apache 2.0",
    author="Vinicius Chiele",
    author_email="vinicius.chiele@gmail.com",
    description="Adds APScheduler support to Flask",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    keywords=["apscheduler", "scheduler", "scheduling", "cron"],
    python_requires=">=3.8",
    install_requires=["flask>=2.2.5,<3.0.0", "apscheduler>=3.2.0,<4.0.0", "python-dateutil>=2.4.2"],
    package_data={"Flask-APScheduler": ["LICENSE"]},
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
    ]
)
