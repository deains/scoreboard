from setuptools import setup


setup(
    name='scoreboard',
    install_requires=[
        'channels>=3.0,<4.0',
        'Django>=3.2,<3.3',
        'django-redis>=5.0,<6.0',
        'gpiozero>=1.6,<2.0',
    ],
)
