# Audio-collection-simplifier
Audio collection simplifier is a desktop app that enables collecting voice data easier it displays a word the user records reading it and it stores that word with it's english translation and the relative path to the recorded audio and save this info in side data.csv.

![An image of the app](/screenshot2.png)

# requirements
- it works on python version 3.10.5
# Usage
- install all dependencies using `pip install -r requirements.txt`
- run `python base.py` to run it
to get started you need dictionary.csv file in the main body of the project the dictonary.csv file must have two columns that translate from `tigrnigna`(col_1) to `english`(col_2)

### dev
to check pep8 coding style `pycodestyle --config=pycodestyle.cfg *.py` 