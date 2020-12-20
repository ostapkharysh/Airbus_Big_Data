from setuptools import setup

with open("README.md") as f:
	long_description = f.read()

setup(
	name='Prediction',
	version='1.0',
	description='Prediction a flight delay with Spark',
	license='MIT',
	long_description=long_description,
	author='Lorenzo Framba, Ostap Kharysh, Federico Rodigari',
	author_email='lorenzo.framba@alumnos.upm.es, ostap.kharysh@alumnos.upm.es, federico.rodigari@alumnos.upm.es',
	install_requires=[
		'seaborn==0.11.0',
		'pyspark==3.0.1',
		'py4j==0.10.9',
		'plotly==4.5.4',
		'pandas==1.0.3',
		'matplotlib==3.1.1',
		'findspark==1.4.2'
	],
	scripts=[
		'main.py',
		'trainer.py',
		'getData.py',
		'visualization.py',
		'cleanData.py'
	]

)
