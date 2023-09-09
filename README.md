
<a href="https://bcrpy.vercel.app/"><img src="docs/img/bcrp_poly_logo.png" 
        alt="Picture" 
        width="300" 
        style="display: block; margin: 0 auto" /></a>

<h2 align="center">bcrpy</h2>

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](https://raw.githubusercontent.com/andrewrgarcia/voxelmap/main/LICENSE)[![Documentation Status](https://readthedocs.org/projects/bcrpy/badge/?version=latest)](https://bcrpy.readthedocs.io/en/latest/?badge=latest)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Un cliente API para la extraccion, consulta y analisis de la base de datos [BCRPData](https://estadisticas.bcrp.gob.pe/estadisticas/series/) del [Banco Central de Reserva del Peru (BCRP)](https://www.bcrp.gob.pe/) escrito para Python. Este cliente es un _wrapper_ de la [API para Desarrolladores](https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api) del BCRP.



## Vinculos 

[Documentación en linea (readthedocs)](https://bcrpy.readthedocs.io/en/latest/) 

[Manual bcrpy (pdf)](https://raw.githubusercontent.com/andrewrgarcia/bcrpy/main/bcrpy.pdf)

[pip package index](https://pypi.org/project/bcrpy/) 

# Instalacion

En su sistema local (laptop o computadora) bcrpy puede ser instalada con el comando pip install bcrpy. Aun asi, se
recomienda instalar bcrpy dentro de un ambiente virtual virtualenv. El protocolo para aquel seria el siguiente:


```ruby
virtualenv venv
source venv/bin/activate
pip install bcrpy
```

bcrpy ha sido desarrollado con un protocolo de programación orientada a objetos (tambien conocido como *Object
Oriented Programming (OOP)*) lo cual se reduce a que objetos pueden ser usados a almacenar metodos (funciones),
datos, y su manejo de aquellos.


[![](docs/img/colaboratory.svg)](https://colab.research.google.com/drive/1YdyCYeU0S98428WgBg4n9Ad9auKrurQZ?usp=sharing)
