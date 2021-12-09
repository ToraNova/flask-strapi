from setuptools import find_packages, setup

_version = '0.0.1'

setup(
    name='flask-strapi',
    version=_version,
    description='a flask module to work with strapi-cms',
    packages=find_packages(),
    author='Chia Jason',
    author_email='chia_jason96@live.com',
    url='https://github.com/toranova/flask-strapi/',
    download_url='https://github.com/ToraNova/flask-strapi/archive/refs/tags/v%s.tar.gz' % _version,
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    keywords = ['Flask', 'Strapi', 'CMS'],
    install_requires=[
        'flask',
        'requests'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
)
