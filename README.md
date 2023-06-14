- [Dev project about creating the twitter using django, hive, aws etc.](#dev-project-about-creating-the-twitter-using-django-hive-aws-etc)
  - [How to start the project](#how-to-start-the-project)
  - [How to run the app](#how-to-run-the-app)
  - [How to install the framework and test](#how-to-install-the-framework-and-test)
  - [How to utilize the APIs](#how-to-utilize-the-apis)
    - [Friendship feature](#friendship-feature)
# Dev project about creating the twitter using django, hive, aws etc.

## How to start the project
- `docker-compose run --rm web sh -c "django-admin.py startproject twitter(pj-name)"`

## How to run the app
- Run the localhost django app.
  - `docker-compose up`
- Show the commands you can use in django framework
  - `docker-compose run --rm web sh -c "python3 manage.py"`

- Create the databse schema
  - `docker-compose run --rm web sh -c "python3 manage.py migrate"`

- Create the superuser in Django
  - `docker-compose run --rm web sh -c "python3 manage.py createsuperuser"` or write the shell script in provision.sh when vagrant up, that will be created automatically.

- Create the account api
  - `docker-compose run --rm web sh -c "python3 manage.py startapp accounts"`

- Update the database shema
 - `docker-compose run --rm web sh -c "python3 manage.py makemigrations"`
  - `docker-compose up --build`

## How to install the framework and test 
- Install the rest framework and config the relative setting.
You can refer the official [rest framework documentation](https://www.django-rest-framework.org/tutorial/quickstart/) 
  - Serializer means the change will be sync on the front rest framework webpage
  - View mean the data scheme you set on the backend

- Install the [debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html)
  - You can use the Toolbar to debug the webpage responding and the database query time.
- Create the Unittest
  - You can use the unittest to test the code.
    - `docker-compose run --rm web  sh -c "python3 manage.py test && flake8"` will test all the code in the project under the `./${project_folder}`.
  - Test the specific test function.
    - ```docker-compose run --rm web  sh -c "python3 manage.py test friendships.api.tests.FriendshipApiTests"```
- Rebuild the docker image
  - `docker-compose up --build`

## How to utilize the APIs

### Friendship feature
- Follow the other users
  - ```/api/friendships/{id}/follow/```
- Unfollow the other users
  - ```/api/friendships/{id}/unfollow/```
- List the login user's followers
  - ```/api/friendships/{id}/followers/```
- List the login user's followings
  - ```/api/friendships/{id}/followings/```
- Add the friendship at the admin page
  - ```http://localhost:8000/admin/```