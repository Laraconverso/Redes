# File Trasfer 

Este proyecto implementa un sistema de transferencia de archivos entre un cliente y un servidor, soportando distintos protocolos de recuperación de errores como GBN y SW.

## ¿Cómo correr el programa?

Una vez descargado, hay que ubicarse en la carpeta src/ del proyecto.
Desde ahí, se pueden lanzar tanto el servidor como el cliente utilizando los siguientes comandos.

## Servidor

El comando para levantar un servidor tiene la siguiente estructura:

start-server [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [- s DIRPATH ] [ - r protocol ]

Argumentos: 
```
-h , -- help, ayuda
-v , -- verbose, aumenta la verbosidad
-q , -- quiet, reducr la verbosidad
-H , -- host, direccion IP del servidor 
-p , -- puerto del servidor
-s , -- ruta de almacenamiento de archivos
-r , -- protocolo de recuperacion
```

Por ejemplo si quiero levantar un servidor con el protocolo stop and wait en mi localhost y el puerto 12345

``` bash 
python start-server.py -q -H localhost -p 12345 -s ./lib -r gbn
```

## Cliente

El cliente soporta comandos de subida (upload) y descarga (download).
Cada uno se ejecuta con su respectivo comando:

### Upload (subida)

Estructura: 
upload [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - s FILEPATH ] [ - n FILENAME ] [ - r
protocol ]

Argumentos: 
```
-h , -- help, ayuda
-v , -- verbose, aumenta la verbosidad
-q , -- quiet, reduce la verbosidad
-H , -- host, direccion IP del servidor
-p , -- puerto del servidor
-s , -- ruta del archivo local
-n , -- nombre del archivo
-r , -- protocolo de recuperacion de errores (puede ser [sw] stop and wait o [gbn] go back n)
```

Ejemplo con stop and wait: 

```
python upload.py -q -H localhost -p 12345 -s ./lib/ -n 8bit_cat.png -r sw
```

### Download (bajada)

Estructura: 
download [ - h ] [ - v | -q ] [ - H ADDR ] [ - p PORT ] [ - d FILEPATH ] [ - n FILENAME ] [ - r
protocol ]

Argumentos:
```
-h , -- help, ayuda
-v , -- verbose, aumenta la verbosidad
-q , -- quiet, reduce la verbosidad
-H , -- host, direccion IP del servidor
-p , -- puerto del servidor
-d , -- dst ruta de destino
-n , -- nombre del archivo
-r , -- protocol de recuperacion de errores
```

Ejemplo con go back N: 

```
python download.py -q -H localhost -p 12345 -d ./lib/img -n 8bit_cat.png -r gbn
```

⚠️ El host y el puerto del cliente deben coincidir con los del servidor. 

---
Extra: 

Para correr la topologia de mininet, con una perdida de 10%. 

Desde la carpeta src/

```
python topology.py
```