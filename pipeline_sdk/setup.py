import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt') as fp:
    install_requires = fp.read()

setuptools.setup(
    name='pipeline_sdk',
    version='0.1.0',
    author='Paweł Pęczek',
    author_email='pawel.m.peczek@gmail.com',
    description='The SDK toolkit to ease development of services features.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PawelPeczek/ModelAsAService',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)