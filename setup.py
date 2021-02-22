import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cursesman",
    version="0.0.1",
    author="David Williams, Todd Perry, Robin Sanders",
    author_email="todd.perry@myport.ac.uk",
    description="Bomberman for the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rasengangstarr/cursesman",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyfiglet==0.8.post1',
        'playsound==1.2.2'
    ],
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts':
        ['cursesman=cursesman:main',
         'cursesman_server=cursesman.server:main'],
    })
