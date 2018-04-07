import setuptools
import castero

install_requires = [
    'requests'
]

tests_require = [

]

extras_require = {
}

setuptools.setup(
    name=castero.__title__,
    version=castero.__version__,
    description=castero.__description__,
    url=castero.__url__,
    author=castero.__author__,
    license=castero.__license__,
    packages=[
        'castero'
    ],
    package_data={
        'castero': ['templates/*'],
    },
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    entry_points={'console_scripts': ['castero=castero.__main__:main']}
)