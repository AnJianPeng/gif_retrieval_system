# gif_retrieval_system
# How to use the environment
Install **conda** first; use yml file corresponding to your OS
## set up
```shell
conda environment create -f environment_mac.yml
```
## update
```shell
conda environment update -f environment_mac.yml
```

## apply new environment
```shell
source activate gif_retrieval
```

# How to run the Django server
- Change your working directory to *src/retrieval*
- run `python manage.py runserver`

# Change the default Redis address in retrieval/settings.py
Change the default IP address of redis server 127.0.0.1 to the correct one before test the code.
