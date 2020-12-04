# Pizza Project

Pizza Project is a project where user can create pizza of different type and size and also add multiple topping according to your taste. In this project you do following things -

  - add  pizza.
  - delete pizza.
  - update pizza.
  - add new size of pizza at any moment of time while creating pizza.
  - add new toppings in pizza at any moment of time while creating pizza.
 

# Setup Virtual Environment
  - firstly check if python is not installed in your system then install python.
  - then find the requirements.txt file which is in project outer directory.
  - then create virtual environment using virtualenv myvenv  
  - if virtualenv is not already install in your system then first install virtualenv.
  - then run command " pip install -r requirements.txt " in directory where manage.py file is available.
  
### Activate the Virtualenv 
###### In windows( directory in which myvenv are present)
- myvenv/Scripts/activate

###### In Linux( directory in which myvenv are present)
- source myvenv/bin/activate



## Set up a database

There's a lot of different database software that can store data for your site. We'll use postgressql

you change the set up in this part of your `pizza_project/settings.py` file:


```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_name',                      
        'USER': 'db_user',
        'PASSWORD': 'db_user_password',
        'HOST': '',
        'PORT': 'db_port_number',
    }
}
```

To create a database for our pizza project, let's run the following in the console: `python manage.py migrate` (we need to be in the `PizzaProject` directory that contains the `manage.py` file). If that goes well, you should see something like this:


```
(myvenv) ~/PizzaProject$ python manage.py migrate
Operations to perform:
  Apply all migrations: auth, admin, contenttypes, sessions
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying sessions.0001_initial... OK
```

And we're done! Time to start the web server and see if our website is working!

## Starting the web server

You need to be in the directory that contains the `manage.py` file (the `PizzaProject` directory). In the console, we can start the web server by running `python manage.py runserver`:


```
(myvenv) ~/PizzaProject python manage.py runserver
```

If you are on a Chromebook, use this command instead:


```
(myvenv) ~/PizzaProject$ python manage.py runserver 0.0.0.0:8080
```

If you are on Windows and this fails with `UnicodeDecodeError`, use this command instead:


```
(myvenv) ~/PizzaProject$ python manage.py runserver 0:8000
```


Now you need to check that your website is running. Open your browser (Firefox, Chrome, Safari, Internet Explorer or whatever you use) and enter this address:


```
http://127.0.0.1:8000/
```

If you're using a Chromebook and Cloud9, instead click the URL in the pop-up window that should have appeared in the upper right corner of the command window where the web server is running. The URL will look something like:


```
https://<a bunch of letters and numbers>.vfs.cloud9.us-west-2.amazonaws.com
```


## All Important urls
base_url = http://127.0.0.1:8000

- for pizza create     -- base_url/add_pizza
- for pizza edit       -- base_url/edit_pizza/pizza_id
- for pizza delete     -- base_url/delete_topping/pizza_id
- for list all pizza   -- base_url

 
## All api urls 

api_base_url = http://127.0.0.1:8000/api/pizza

- for list all pizza   -- base_url
- for pizza create     -- base_url/create
- for pizza detail     -- base_url/pizza_id
- for pizza edit       -- base_url/pizza_id/update/
- for pizza delete     -- base_url/pizza_id/delete/









 


