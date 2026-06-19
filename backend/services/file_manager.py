from typing import Optional
import aiofiles
import hashlib
from pathlib import Path
from config import FILES_DIR
from services.portal_client import portal_client


async def download_file(order_id: int, filename: str, url: str) -> Optional[str]:
    """
    Downloads a file and stores it at FILES_DIR/{order_id}/{filename}.
    Returns local relative path or None on failure.
    """
    order_dir = FILES_DIR / str(order_id)
    order_dir.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ").strip()
    if not safe_name:
        safe_name = hashlib.md5(filename.encode()).hexdigest()

    local_path = order_dir / safe_name

    # Skip if already downloaded
    if local_path.exists() and local_path.stat().st_size > 0:
        return str(local_path.relative_to(FILES_DIR.parent))

    content = await portal_client.download_file(url)
    if content is None:
        return None

    async with aiofiles.open(local_path, "wb") as f:
        await f.write(content)

    return str(local_path.relative_to(FILES_DIR.parent))


def get_local_file_path(relative_path: str) -> Optional[Path]:
    path = FILES_DIR.parent / relative_path
    if path.exists():
        return path
    return None
