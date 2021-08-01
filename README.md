# Tixte
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

# How to get your master key
Getting the master key isn't that hard

- Go to [the Tixte Dashboard](https://tixte.com/dashboard/configurations)

- Go to the Console via pressing `Ctrl + Shift + I`
            
- Paste in `document.cookie.split("tixte_auth=")[1].split(";")[0]` at the bottom and press enter

- Your key should be outputted.

Note: **Do not share this mater key with anyone.**

# Examples
See all examples in the examples folder

Simple Example:
```python
import tixte
import asyncio


async def main():
    client = tixte.Client('your-mater-key')
    file = tixte.File('this_image.png')
    
    uploaded_file = await client.upload_file(file=file)  # Upload file
    print(uploaded_file.id)
    print(uploaded_file.filename)
    print(uploaded_file.url)
    print(str(uploaded_file))
    
    await uploaded_file.delete()  # Delete the file.
    
    
asyncio.run(main())
```

URL Example:
```python
import tixte
import asyncio

async def main():
    # The domain in Client is optional, the first domain
    # from the fetch_domains() func will be used unless
    # specified.

    client = tixte.Client('your-master-key', domain='your-domain.com')  

    url = 'https://nerdist.com/wp-content/uploads/2020/07/maxresdefault.jpg'
    file = await client.file_from_url(url=url, filename='notrickroll.png')

    uploaded_file = await client.upload_file(file=file)  # Upload the file
    print(str(uploaded_file))  # Print it's url

asyncio.run(main())
```

# Creds
Largs creds to [Rapptz](https://github.com/Rapptz) and his [discord.py](https://github.com/Rapptz/discord.py) lib:


> [file.py](https://github.com/NextChai/Tixte/blob/main/tixte/file.py) `File` class was taken from his lib

This was to  get rid of an additional dependency. Our library offers direct support for `discord.File` obj's, so it only made sense to have our `File` obj's be the same.

> [http.py](https://github.com/NextChai/Tixte/blob/main/tixte/http.py) `Route` class inspired from his lib

His Route route is a great idea, and makes a lib like this very easy to work on. It was a no brainer to use in this lib as well.

> Feel more credit it needed somewhere?

Open a PR and explain where and why! I'll be sure to add it no problem.
