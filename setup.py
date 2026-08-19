from setuptools import setup

setup(
    name='defhunter',
    version='2.0',
    description='DerdliAsiq Otonom Default Credential ve Zafiyet Avcısı',
    author='DerdliAsiq',
    py_modules=['defhunter'],
    install_requires=[
        'paramiko',
        'requests',
        'pymysql',
        'ldap3'
    ],
    entry_points={
        'console_scripts': [
            'defhunter=defhunter:main',
        ],
    },
)