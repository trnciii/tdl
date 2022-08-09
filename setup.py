from setuptools import setup, find_packages

setup(
	name='tver-dl',
	version='0.0.1',
	url='https://github.com/trnciii/tdl',
	packages=find_packages(),
	install_requires=[
		'requests',
		'youtube-dl',
	],
	entry_points={
		'console_scripts':['tver-dl = tver_dl:main']
	}
)