import tixte
import asyncio

async def main():
    client = tixte.Client('your-master-token', 'your-domain')
    file = tixte.File('this_image.png')

    upload = await client.upload_file(file)  # Upload file
    print(f'Uploaded file {upload.url} - {upload.filename}')
    
    # Delete the file now
    response = await upload.delete()
    print(f'Deleted file: {response.message}')

asyncio.run(main())
