# bcrpy

[![](docs/img/bcrpy.png)](https://bcrpy.readthedocs.io/en/latest/)


Un cliente API para la extraccion, consulta y analisis de la base de datos [BCRPData](https://estadisticas.bcrp.gob.pe/estadisticas/series/) del [Banco Central de Reserva del Peru (BCRP)](https://www.bcrp.gob.pe/) escrito para Python. Este cliente es un _wrapper_ de la [API para Desarrolladores](https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api) del BCRP.

![](docs/img/bcrp.png)

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
