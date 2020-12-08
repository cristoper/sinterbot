import setuptools

setuptools.setup(
        name='sinterbot',
        version='0.1.0',
        author_email='chris@catswhisker.xyz',
        packages=['sinterbot'],
        entry_points={
                'console_scripts': [
                        'sinterbot=bin.sinterbot:main',
                        ],
                },
        license='license.txt',
        description='A program to manage secret santa assignments.',
        long_description_content_type='text/markdown',
        long_description=open('readme.md').read(),
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
