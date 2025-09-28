# Trabajo Práctico 2 - Redes

El trabajo practico se puede ejecutar con la linea de comandos o con los scripts preparados.

Comandos
---  
Controlador:

Primero hay que copiar el archivo firewall.py y flow_builder.py en la carpeta de pox/ext. 

```python2 pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning firewall```

mininet: 
```sudo python3 topology.py [cant. switches] ```
 

Para correrlo en los scripts
----

Con ```chmod +xr ./*.sh``` se dan los permisos necesarios a los scripts

Para ejecutar POX 

```./start_pox.sh <1,2,..>```

Para Ejecutar Mininet

```./run_topo.sh <cant_switches>```


Comandos para testear: 
----

Conectar un servidor 

```<HOST> iperf -s [-u] -p ```
```
Argumentos: 
[-u] UDP, el default es TCP
```

Mandar informacion: 

```<HOST> iperf -c <ip destino> -u -p <puerto> [-t]```

```
Argumentos: 
[-u] UDP, el default es TCP
[-p] Puerto
[-t] Timery el tiempo que queremos que corra la prueba en segundos
```

Cuando queremos setear el puerto origen, 
primero seteamos el server que escuche en un puerto (bloqueado o no segun la regla)
```h3 iperf -p 22 -s &``` 

```h2 telnet 10.0.0.3 22```

Para visualizar las reglas instaladas en un switch especifico:

```sh ovs-ofctl dump-flows <SWITCH\>```

Limpieza de mininet ```sudo mn -c```

Para abrir una terminar especifica de un host en mininet ```xterm <host>```

---
Testeo de reglas especificas: 

Regla 1: Se deben descartar todos los mensajes cuyo puerto destino sea 80.
Establecemos como servidor al host h3 con el comando ```iperf -s -p 80``` y ejecutamos al cliente en el host h2 con el comando ```iperf -c 10.0.0.3 -p 80```.


Regla 2: Se deben descartar todos los mensajes que provengan del host 1, tengan como puerto destino el 5001, y estén utilizando el protocolo UDP.
Establecemos como servidor al host h2 con el comando ```iperf -s -u -p 5001``` y ejecutamos al cliente en el host h1 con el comando ```iperf -c 10.0.0.2 -u -p 5001```.

Regla 3: Se deben elegir dos hosts cualesquiera y los mismos no deben poder comunicarse de ninguna forma.
Establecemos como servidor al host h4 con el comando ``iperf -s`` y ejecutamos al cliente en el host h2 con el comando ``iperf -c 10.0.0.4``.

