import io

import httpx
from httpx import Response


async def upload_image(file_name: str, file_bytes: bytearray, todoist_token: str) -> Response:
    upload_img_url = f"https://api.todoist.com/sync/v9/uploads/add?&file_name={file_name}"
    header = {"Authorization": f"Bearer {todoist_token}"}
    files = {"file": (file_name, io.BytesIO(file_bytes), 'image/jpeg')}
    async with httpx.AsyncClient() as client:
        return await client.post(upload_img_url, headers=header, files=files)
