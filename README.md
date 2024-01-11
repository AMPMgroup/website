# Antibody Antigen Database Website
The database aims to serve to obtain relevant data about antibodies and antigens, and their interactions.
Entries can be accessed using their respective PDB IDs.

# Requirements :
Install flask application 
### Windows 
```bash
  pip install flask
  pip3 install pipenv
  pipenv install
  pipenv shell
  pipenv install flask
```
Set up the flask environment -- in terminal under .virtualenvs
```bash
cd .virtualenvs\<your_env>
```
```bash
cd <your_directory>
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_RUN_HOST=127.0.0.1
set FLASK_RUN_PORT=5000
flask run
```

### Script files :
`app.py`
`search_form.html`
`results.html`
`about.html`
`documentaion.html`

# Connection string to database << edit the string accordingly in app.py >>
        host="localhost",
        user="root",
        password="divya",
        database="my_db"
### other files related to database: 
`Final diagram.mwb`

#### Usage :
Using visual studio code or any other compatible software
