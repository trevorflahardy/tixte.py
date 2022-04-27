import tixte
import asyncio


async def main():
    client = tixte.Client('your-master-token')
    file = tixte.File('this_image.png')

    uploaded_file = await client.upload_file(file=file)  # Upload file
    print(uploaded_file.id)
    print(uploaded_file.filename)
    print(uploaded_file.url)
    print(str(uploaded_file))

    await uploaded_file.delete()  # Delete the file.


asyncio.run(main())
