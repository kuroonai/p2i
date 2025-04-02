from setuptools import setup, find_packages

setup(
    name="p2i",
    version="1.0.0",
    description="Advanced PDF & Image Processing Tool",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pdf2image>=1.16.3",
        "Pillow>=9.0.0",
        "tqdm>=4.64.1",
        "pypdfium2>=3.3.0",
        "reportlab>=3.6.0",
        "PyPDF2>=2.0.0",
    ],
    entry_points={
        "console_scripts": ["p2i=p2i.main:main"],
    },
)