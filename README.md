# awacs
Eyes in the sky and helps pull data on Concourse CI's github repos

# Requirements
* Python 3.6+ https://www.python.org/downloads/
* pip  https://pypi.org/project/pip/
* virtualenv https://virtualenv.pypa.io/en/latest/
* virtualenvwrapper https://virtualenvwrapper.readthedocs.io/en/latest/ 

# Steps
* Install requirements `pip install -r requirements.txt`
* Make a file called `settings.py` with the following consts:
  * `GH_KEY`: your personal github key as a string
  * `ORGANIZATION`: the name of the org for the repos you are scanning e.g. `concourse`
  * `REPOS`: a list of repo names as strings `[concourse, docs, ...]`
* Run `main.py`
