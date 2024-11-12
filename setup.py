from setuptools import setup, find_packages

setup(
    name='babelbase',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=4.2',  # specify Django version compatible with your package
    ],
    description='A Django app for ...',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/rollinger/babelbase',
    author='Philipp Rollinger',
    author_email='philipp.rollinger@protonmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
)
