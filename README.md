# Audio-collection-simplifier

Audio collection simplifier is a desktop app that enables collecting voice data easier it displays a word the user records reading it and it stores that word with it's english translation and the relative path to the recorded audio and save this info in side data.csv.

![An image of the app](/screenshot2.png)

# requirements

- it works on python version 3.10.5 (not tested on other versions)

# Usage

- clone the `git clone https://github.com/Shakir-ahmed1/Auido-collection-simplifier.git YOUR_NAME`
- install venv `pip install venv`
- create a new environment `python -m venv venv`
- activate the environment `venv/scripts/activate`
- install all dependencies using `pip install -r requirements.txt`
- run `python base.py` to run it
  to get started you need data.csv file in the main body of the project the dictonary.csv file must have two columns called `id`(col_1) to `text`(col_2)

### dev

to check pep8 coding style `pycodestyle --config=pycodestyle.cfg *.py`
