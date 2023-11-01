# Backend test

Resolución de la prueba de backend https://github.com/onestic/interviews/tree/main/developer_junior_engineer/backend.

Autora: Gessica Paniagua

## Instalación y preparación

```shell
# clonar repositorio
git clone https://github.com/gpani/backend_test.git
cd backend_test

# preparar virtualenv
python3 -m venv venv
. venv/bin/activate

# instalar dependencias
pip install -r requirements.txt

# crear DB y modelos
python manage.py makemigrations
python manage.py migrate

# crear superuser (opcional)
python manage.py createsuperuser --email admin@example.com --username admin
# ingresar password cuando se solicite
```

## Tests y servidor de desarrollo

```shell
# ejecutar tests
python manage.py test

# ejecutar servidor de desarrollo
python manage.py runserver
# ctrl+c para finalizar

# ejecutar aplicación en container
# (se necesita docker y docker-compose)
docker-compose up
# ctrl+c para finalizar
```

## Prueba de la API

Instalar `httpie`. Subir los archivos al endpoint `/data/`:
```shell
http -f POST http://localhost:8000/data/ customers@/path/to/customers.csv products@/path/to/products.csv orders@/path/to/orders.csv
```

Obtener reportes haciendo clic en los siguientes links:
- http://localhost:8000/reports/1/
- http://localhost:8000/reports/2/
- http://localhost:8000/reports/3/ 

O bien mediante estos comandos:
```shell
http http://localhost:8000/reports/1/ # GET report 1
http http://localhost:8000/reports/2/ # GET report 2
http http://localhost:8000/reports/3/ # GET report 3
```

## Memoria

Comencé el desarrollo de esta aplicación con una estructura básica de Django y Django REST Framework. Conozco estos frameworks de proyectos anteriores y no me resultó complicado crear los modelos y vistas básicas para cargar la base de datos con el contenido de los archivos CSV. Me basé en [este post](https://baronchibuike.medium.com/how-to-read-csv-file-and-save-the-content-to-the-database-in-django-rest-256c254ef722) para verificar si mis vistas y serializers estaban correctos.

Ahora bien, el primer desafío interesante se dio al relacionar los productos con las órdenes. Una relación estándar de Django Many-to-Many no fue suficiente. Debí crear el modelo `OrderProduct` con un campo `count` ya que puede existir más de un mismo producto en cada orden. Para resolverlo tomé como referencia [esta pregunta en StackOverflow](https://stackoverflow.com/questions/7260716/way-to-allow-for-duplicate-many-to-many-entries-in-python-django).

El otro gran desafío fue generar las consultas para los distintos reportes. Si bien imaginé cómo resolverlo usando queries SQL, en este caso opté por la sintaxis del ORM de Django. Para ello leí [esta pregunta en StackOverflow](https://stackoverflow.com/questions/629551/how-to-query-as-group-by-in-django) y [esta otra](https://stackoverflow.com/questions/10340684/group-concat-equivalent-in-django) puntualmente para concatenar los IDs de clientes separados por un espacio. Usé el shell interactivo de Django (`python manage.py shell`) para probar las queries antes de implementarlas en la vista.

Escribí tests básicos para la API que verifica errores al no subir todos los archivos CSV requeridos y ejecuta una pequeña prueba funcional para verificar los cálculos realizados por las queries. Me basé en [esta pregunta en StackOverflow](https://stackoverflow.com/questions/24201676/how-can-i-test-binary-file-uploading-with-django-rest-frameworks-test-client) y en [esta otra](https://stackoverflow.com/questions/55708696/testing-django-fileresponse). Para verificar dichos cálculos los almacené en un `DataFrame`. Me basé en [la documentación de pandas](https://pandas.pydata.org/docs/reference/api/pandas.testing.assert_series_equal.html).

Finalmente implementé el _containerizado_ de la app. Tomando como referencia [este post](https://medium.com/backticks-tildes/how-to-dockerize-a-django-application-a42df0cb0a99) no me resultó difícil usando Docker y `docker-compose`.
