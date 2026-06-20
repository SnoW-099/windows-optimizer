# Windows Optimizer

Optimizador de Windows en terminal, hecho en Python.

By snow.

## Estructura

```text
.
├── src/                         Codigo principal
├── scripts/                     Scripts de mantenimiento
├── dist/                        ZIP generado para compartir
├── snow.cmd                     Comando de terminal
├── Abrir Snow Optimizer Python.bat
├── Abrir Snow Optimizer Python Admin.bat
├── instalar_comando_snow.bat
└── README.md
```

## Abrir la app

Opcion normal:

```bat
Abrir Snow Optimizer Python.bat
```

Opcion administrador:

```bat
Abrir Snow Optimizer Python Admin.bat
```

Usa administrador para punto de restauracion, limpieza completa y ajustes del sistema.

## Instalar el comando `snow`

1. Abre `instalar_comando_snow.bat`.
2. Cierra la terminal.
3. Abre una terminal nueva.
4. Ejecuta:

```bat
snow
```

## Crear ZIP para compartir

Abre:

```bat
scripts\crear_release_zip.bat
```

Se generara:

```bat
dist\Snow-Windows-Flow-By-snow.zip
```

## Subir a GitHub

El repo ya esta conectado a GitHub. Si necesitas reconfigurarlo:

```bat
scripts\subir_a_github.bat
```

## Funciones

- Analizador del PC con recomendaciones.
- Snapshot del sistema.
- Optimizacion rapida.
- Limpieza de temporales.
- Vaciar papelera.
- Refresco de red.
- Procesos con mas consumo.
- Elementos de inicio.
- Punto de restauracion.
- Accesos a herramientas de Windows.
- Gaming Boost.
- Logs locales en `src\logs\`.

## Requisito

Python instalado en Windows.

Si no funciona, instala Python desde:

```text
https://www.python.org/downloads/
```

Marca `Add python.exe to PATH` durante la instalacion.
