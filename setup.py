from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="p2i",
    version="1.0.0",
    description="PDF & Image Processing Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Naveen Vasudevan",
    author_email="naveenovan@gmail.com",
    url="https://github.com/kuroonai/p2i",  # Replace with your actual repository URL
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.9',  # Specify minimum Python version
    install_requires=[
        "pdf2image>=1.16.3",
        "Pillow>=9.0.0",
        "tqdm>=4.64.1",
        "pypdfium2>=3.3.0",
        "reportlab>=3.6.0",
        "PyPDF2>=2.0.0",
        "tkinterdnd2>=0.3.0",  # For drag and drop functionality
    ],
    entry_points={
        "console_scripts": ["p2i=p2i.main:main"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Editors",
        "Topic :: Office/Business",
    ],
    keywords="pdf, image, conversion, processing, tkinter",
    project_urls={
        "Bug Reports": "https://github.com/kuroonai/p2i/issues",
        "Source": "https://github.com/kuroonai/p2i",
    },
)