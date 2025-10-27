from fastapi import APIRouter, UploadFile, File, HTTPException
import cloudinary.uploader as uploader

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """מעלה תמונה ל-Cloudinary ומחזיר כתובת URL"""
    try:
        result = uploader.upload(
            await file.read(),
            folder="cloud-news-aggregator",
            resource_type="image",
            public_id=file.filename.rsplit(".", 1)[0],
            overwrite=True,
        )
        return {
            "url": result["secure_url"],
            "thumb": result["secure_url"].replace(
                "/upload/", "/upload/c_fill,w_300,h_200,q_auto,f_auto/"
            ),
            "public_id": result["public_id"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
