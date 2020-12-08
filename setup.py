import setuptools

with open("README.md", "r") as f:
        long_description = f.read()

setuptools.setup(
        name='sinterbot',
        version='0.1.1',
        author='cristoper',
        author_email='chris@catswhisker.xyz',
        url='https://github.com/cristoper/sinterbot',
        packages=['sinterbot', 'bin'],
        entry_points={
                'console_scripts': [
                        'sinterbot=bin.sinterbot:main',
                        ],
                },
        license='license.txt',
        description='A program to manage secret santa assignments.',
        long_description_content_type='text/markdown',
        long_description=long_description,
        python_requires='>=3.4',
        classifiers=[
                'Development Status :: 4 - Beta',
                'License :: OSI Approved :: MIT License',
                'Programming Language :: Python :: 3.5',
                ],
        extras_require={
                'dev': ['mypy']
                },
        )
