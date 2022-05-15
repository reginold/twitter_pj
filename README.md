### Dev project about create the twitter using django, hive, aws etc.

- Start the project
`django-admin.py startproject twitter(pj-name)`

- Show the commands you can use in django framework
`python manage.py`

- Create the databse schema
`python manage.py migrate`

- Run the server on localhost
`python manage.py runserver 0.0.0.0:8000`

- Create the superuser in Django
`python manage.py createsuperuser` or write the shell script in provision.sh when vagrant up, that will be created automatically.

- Create the account api
`python manage.py startapp accounts`

- Install the rest framework and config the relative setting.
You can refer the official [rest framework documentation](https://www.django-rest-framework.org/tutorial/quickstart/) 
  - Serializer means the change will be sync on the front rest framework webpage
  - View mean the data scheme you set on the backend

- Install the [debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html)
  - You can use the Toolbar to debug the webpage responding and the database query time.
- Create the Unittest
  - You can use the unittest to test the code.
  - `python manage.py test` will test all the code in the project under the `./${project_folder}`.
- Rebuild the docker image
  - `docker-compose up --build`