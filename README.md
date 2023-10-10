# Annotation Interface 2

## NSF Project Title: III: Medium: Spatial Sound Scene Description

## Note: I closed the AWS account for storing audio files

Please create a postgresql database beforehand and change the path in server/db_tables.py line 6 the current database path

And please create the Recording, Recording_Joint_Source, and Source tables first before launching the website

Link to the [Headphone Check Code](https://github.com/mcdermottLab/HeadphoneCheck)

Terminal Commands for setting up virtual environemnt to run the program:

```
virtualenv env

source env/bin/activate

pip3 install flask

pip3 install sqlalchemy

pip3 install psycopg2-binary

python3 server/main.py
```
or if you are using conda:

```
conda config --append channels conda-forge

conda create --name <env_name_here> --file requirements.txt

conda activate <env_name_here>

python3 server/main.py
```
