Realizar despliegue de aplicación de Django en Heroku Cloud
===========================================

### Tabla de contenidos
- [Supuestos](#supuestos)
- [Configuración](#setup)
    - [Instalación de Heroku CLI](#instalar-heroku-cli)
    - [Entorno virtual](#entorno-virtual)
    - [Archivo de procesos para heroku](#crear-un-procfile)
    - [Uso de variables de entorno](#variables-de-entorno)
- [Configuración de la base de datos](#configuracion-adicional)
- [Archivos estáticos y multimedia](#static-and-media-files)
- [Especificación de runtime de python](#specifying-your-python-runtime)
- [Crear una aplicación Heroku y desplegar un proyecto Django](#creating-heroku-app-and-deploying-django-project)
    - [Añadir configuraciones a la aplicación Heroku](#adding-configurations-to-your-heroku-app)
    - [Pushing Project To Heroku](#pushing-project-to-heroku)
    - [Migración de la base de datos]("database-migrations)
    - [Despliegue de Postgres local a Heroku](#pushing-local-postgres-database-to-heroku)
    - [Ejecución de pruebas en heroku](#confirming-that-tests-run-on-heroku)
- [Errores de despliegue y problemas comunes](#why-am-i-getting-errors)
- [Recursos adicionales](#resources)

## Supuestos
* Se tienen los archivos del proyecto a desplegar.
* Se tiene instalado Python 3.9.+ y el entorno preparado.
* Se conoce cómo trabajar con entornos virtuales.

### Versión de django utilizada
* Django 3.2.8

## Lista de comprobación
- [ ] Procfile
- [ ] Añadir las configuraciones al los archivos settings.py y url.py
- [ ] Configurar la url de la base de datos.
- [ ] Configurar Whitenoise para archivos estáticos.
- [ ] Crear un archivo requirements.txt
- [ ] Crear un archivo runtime.txt para indicar a heroku la versión de python a utilizar.
- [ ] Crear una aplicación heroku y una instancia postgres.
- [ ] Desplegar.

## Setup
### Instalar heroku CLI
Crea una cuenta en heroku si no se tiene una, [Regístrate](https://signup.heroku.com/).

Instalar [Heroku Toolbelt](https://toolbelt.heroku.com/). Es una herramienta de línea de comandos para gestionar aplicaciones Heroku

Después de instalar Heroku Toolbelt, abrir un terminal y entrar en la cuenta:
```bash
$ heroku login
```

### Entorno virtual
- Trabajar en un entorno virtual
```bash
cd directoriodelproyecto
python3 -m venv virtual_env
source virtual/bin/activate
```
- A continuación, se instalan las bibliotecas necesarias especificadas en el archivo requirements.txt 
```bash
pip install -r requirements.txt
```

### Crear un Procfile
Las aplicaciones Heroku incluyen un `Procfile` que especifica los comandos que son ejecutados por los dynos de la aplicación. 

Para más información: [documentación de heroku](https://devcenter.heroku.com/articles/procfile).

Se debe instalar gunicorn, un servidor HTTP WSGI de Python como nuestro servidor de producción. 

```bash
pip install gunicorn 
```

Crea un archivo llamado `Procfile` en la raíz del proyecto con el siguiente contenido:
```
web: gunicorn nombre_del_proyecto.wsgi --log-file -
```

### Variables de entorno
- Las variables de entorno limitan la necesidad de modificar y voler a desplegar la aplicación debido a cambios en la configuración.

### Configuración adicional
- Para poder iniciar el servidor se hará uso de ciertas variables de entorno. 
- A continuación, instalar la bilbioteca que permitirá leer fácilmente las variables de entorno.
```bash
pip install python-decouple
```

- Ahora se debe reemplazar la configuración en `settings.py` con
```python
...
DEBUG = False
ALLOWED_HOSTS = ['*']
...
```


### Configuración de la base de datos
- La librería `dj-database-url` permite generar la configuración de la base de datos a partir de una url de base de datos.
- También instalar `psycopg2` para la base de datos (PostgreSQL).
```bash
pip install dj-database-url psycopg2
```
- Ahora se debe reemplazar la configuración para la base de datos en `settings.py` con
```python
# primero importar la url de la base de datos dj en la parte superior del archivo settings.py
import dj_database_url
from decouple import config
...

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
...
```


### Archivos estáticos y multimedia
> Django no soporta servir archivos estáticos en producción. Sin embargo, el la bilbioteca WhiteNoise fue diseñada con este propósito.
- Instalar whitenoise
```bash
pip install whitenoise
```
- Actualizar el archivo requirements.txt 
```bash 
pip freeze > requirements.txt
```

- Añadir whitenoise a la aplicación como middleware en `settings.py`.
```python
#settings.py
MIDDLEWARE_CLASSES = (
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
```
- Luego añadir la configuración para los archivos estáticos de django y los archivos multimedia, en `settings.py`. Lo más probable es que al final de `settings.py`, `STATIC_URL` ya esté ahí.

```python
#Archivo settings.py

# Archivos estáticos (CSS, JavaScript, Imágenes)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Lugares extra para que collectstatic encuentre archivos estáticos.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Configuración para la compresión de archivos estáticos.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

#Multimedia
MEDIA_URL = '/media'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

- En el archivo `urls.py` (el principal) agregar las siguientes líneas de código, esto con la finalidad de poder utilizar los archivos estáticos.
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

## Especificación del runtime de python

- Este archivo contiene la versión de python que heroku usará.
- crear el archivo `runtime.txt` en la raíz del proyecto y añadir la versión de python con el siguiente formato
```
python-3.9.12
```
- Lista de runtime de python soportados en heroku: [Heroku Python Runtimes](https://devcenter.heroku.com/articles/python-runtimes).


## Creando la aplicación Heroku y desplegando el proyecto Django.

- En el directorio raíz del proyecto (donde está `manage.py`)

- A continuación, se crea la aplicación heroku desde el terminal, habiendo iniciado sesión en heroku y teniendo heroku cli instalado:
```bash
heroku create nombre-de-la-app
```
- Crear el add-on de postgres para la aplicación heroku
```bash
heroku addons:create heroku-postgresql:hobby-dev
```
- Ligamos el repositorio la app en heroku.
```bash
heroku git:remote -a <nombre-de-la-app>
```

- Se procede realizando el despliegue desde la terminal en heroku.
```bash
git push heroku <repositorio-local>:master
```
- Si todo está bien se puede proceder a ejecutar todas las migraciones.
```bash
heroku run python manage.py migrate
```

- Ahora puede abrir la aplicación en su navegador visitando `https://nombre-de-la-app.herokuapp.com`.

### Añadiendo configuraciones a la aplicación Heroku a través del Dashboard
- Entrar a [heroku dashboard](https://dashboard.heroku.com/apps), seleccionar la aplicación e ir a la pestaña de configuración. Hacer clic en el menú de configuración y luego en el botón `Reveal Config Vars`
- A continuación añadir todas las variables de entorno, por defecto se tiene la configuración `DATABASE_URL` creada después de instalar postgres en heroku.
- Las variables de entorno a añadir son las mismas que las siguientes:

<img src="https://imgur.com/a/pGyiHaU" alt="Heroku config vars" width="400" height="300">


- Luego, generar un nuevo archivo llamado `settings_production.py` y colocar el siguiente código:
```python
import dj_database_url
from decouple import config

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}
```

- En el archivo `settings.py`, colocar nuevamente las configuraciones para la base de datos de forma local como por ejemplo:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```


- Una vez con las variables, nuevamente, modificar el archivo `settings.py`. Sustituir las líneas de código.:

```python
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='La llave default que proporciona Django')
...
...
# En la última línea del archivo agregar el siguiente código:
if config('DJANGO_PRODUCTION', default=False, cast=bool):
    from .settings_production import *
```



## Recursos adicionales
* [Guía alternativa en español](https://codigofacilito.com/articulos/deploy-django-heroku)

### Documentación Heroku
* [Heroku Postgres](https://devcenter.heroku.com/articles/heroku-postgresql)
* [Archivos estáticos en Heroku y Whitenoise](https://devcenter.heroku.com/articles/django-assets)
* [Heroku python Runtimes](https://devcenter.heroku.com/articles/python-runtimes)
* [Heroku Procfile](https://devcenter.heroku.com/articles/procfile)
* [Heroku empezando con python](https://devcenter.heroku.com/articles/getting-started-with-python#introduction)
* [Heroku Deploying python](https://devcenter.heroku.com/articles/deploying-python)
* [Heroku Django App configuration](https://devcenter.heroku.com/articles/django-app-configuration)
* [Heroku Gunicorn](https://devcenter.heroku.com/articles/python-gunicorn)

