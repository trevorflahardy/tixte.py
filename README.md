# tixte.py
[![Documentation Status](https://readthedocs.org/projects/tixtepy/badge/?version=latest)](https://tixtepy.readthedocs.io/en/latest/?badge=latest)

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

## Installing Master Branch
```python
python -m pip install git+https://github.com/NextChai/tixte.py
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

Documentation is available [here](https://tixtepy.readthedocs.io/en/latest/). 

Please note the layout and style for the documentation and all
of the source that goes along with it is directly from [Rapptz/discord.py](https://github.com/Rapptz/discord.py). 

All credit for the source of the documentation goes to Rapptz and his group is contributors. In my experience with sphinx, 
there is nothing close to how well put together this style of documentation is, it's a pleasure to work with it.
