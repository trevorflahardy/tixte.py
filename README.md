[![Documentation Status](https://readthedocs.org/projects/tixtepy/badge/?version=latest)](https://tixtepy.readthedocs.io/en/latest/?badge=latest)

![Banner_Thin](https://github.com/NextChai/tixte.py/assets/75498301/c55cbe5f-bd79-4131-86ba-9386b541678c)


```python
import asyncio
import tixte

async def main():
    client = tixte.Client('your-master-token', 'your-domain')
    file = tixte.File('this_image.png')
    
    async with client:
        upload = await client.upload(file)  # Upload file
        print(f'Uploaded file {upload.url} - {upload.filename}')

asyncio.run(main())
```

# Installing
Recommended Python 3.8.0 or higher

To install the library you can do the following
```
# Linux / MacOS
python -m pip install tixte.py

# Windows
py -m pip install tixte.py
```

## Installing Master Branch
```python
python -m pip install git+https://github.com/NextChai/tixte.py
```

# Obtaining Your Master Token
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
