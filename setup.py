from setuptools import setup

setup(
    name="dashwellviz",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Tools for Transform 2020 Dash_Well_Viz project",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/WesleyTheGeolien/t20-Dash_Well_Viz",
    author="Transform 2020 Hackathon Dash_Well_Viz contributors",
    packages=["dashwellviz"],
    install_requires=["plotly", "dash", "pandas", "seaborn"],
)
