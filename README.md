# tixte.py
The async wrapper for the Tixte API.

# Installing
Recommended Python 3.5.3 or higher

To install the library you can do the following
```
# Linux / MacOS
python -m pip install tixte

# Windows
py -m pip install tixte
```

# Getting a Master Token
A master token is a token given by Tixte to allow applications
to access and make requests to the API. It can be obtained by:

1. Going to the [Tixte dashboard](https://tixte.com/dashboard/browse)
2. Pressing `Control + Shift + I` to open the developer console
3. Entering the following command:
```
localStorage.getItem("sessionToken")
```
4. The response outputted into the console is your master token.

# Documentation
[![Documentation Status](https://readthedocs.org/projects/tixtepy/badge/?version=latest)](https://tixtepy.readthedocs.io/en/latest/?badge=latest)