# handyman-API
handman api for home services and maintenance
### how to install on linux ubuntu

Suposed you have installed python3, virtual environment module and pip. 

```shell
handyman-backend$ python3 -m venv .venv
handyman-backend$ source .venv/bin/active
handyman-backend$ pip3 install -r requirements.txt
```
After that you have to update settings.py file to adjust database configration.


Then migrate database
```shell
handyman-backend$ python3 manage.py makemigrations
handyman-backend$ python3 manage.py migrate
handyman-backend$ python3 manage.py runserver
```
# Handyman API Swagger Documentation: 
[Handyman api!](http://handymancompany.pythonanywhere.com/swagger/ "Live demo")
