import setuptools

setuptools.setup(
    name='avm2',
    version='0.1',
    author='Pavel Perestoronin',
    author_email='eigenein@gmail.com',
    description="A small example package",
    long_description=open('README.md', 'rt').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eigenein/python-avm2',
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=[],
    extras_require={},
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Disassemblers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
