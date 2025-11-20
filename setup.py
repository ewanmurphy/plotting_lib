from setuptools import setup, find_packages


setup(
    name="plotting_lib",
    version="0.2.0",
    description="A library for plotting data",
    author="Ewan Murphy",
    author_email="ewan.murphy@inria.fr",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"plotting_lib": ["journal_styles/*"]},
    entry_points={
        "console_scripts": [
            "threshold_plot=plotting_lib.threshold_plot:main"
        ]
    },
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "pandas",
        "typer",
        "PyQt5", 
        "PySide2"
    ],
)
