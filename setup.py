from setuptools import setup, find_packages
  
setup(
    name='germanium',
    version='0.0.0',
    description='Helpful methods for Python Selenium',
    author='Lukas Rychtecky',
    author_email='lukas.rychtecky@gmail.com',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    include_package_data=True,
    zip_safe=False,
)
