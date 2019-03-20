import setuptools

import castero

install_requires = [
    'requests',
    'cjkwrap',
    'beautifulsoup4',
    'python-vlc',
    'python-mpv'
]

tests_require = [
    'pytest',
    'coverage',
    'codacy-coverage'
]

extras_require = {
    'test': tests_require
}


def long_description():
    with open("README.md") as readme:
        return readme.read()


setuptools.setup(
    name=castero.__title__,
    version=castero.__version__,
    description=castero.__description__,
    long_description=long_description(),
    long_description_content_type='text/markdown',
    keywords=castero.__keywords__,
    url=castero.__url__,
    author=castero.__author__,
    author_email=castero.__author_email__,
    license=castero.__license__,
    packages=[
        'castero', 'castero.perspectives', 'castero.players', 'castero.menus'
    ],
    package_data={
        'castero': ['templates/*', 'templates/migrations/*'],
    },
    python_requires='>=3',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    entry_points={'console_scripts': ['castero=castero.__main__:main']},
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console :: Curses',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Topic :: Terminals'
    ],
)
