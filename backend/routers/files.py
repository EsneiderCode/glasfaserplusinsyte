import mimetypes
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from config import FILES_DIR

router = APIRouter(prefix="/api/files")


@router.get("/{order_id}/{filename}")
def serve_file(order_id: int, filename: str):
    # Sanitize filename to prevent path traversal
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ")
    path = FILES_DIR / str(order_id) / safe_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    mime, _ = mimetypes.guess_type(str(path))
    return FileResponse(str(path), media_type=mime or "image/jpeg")
