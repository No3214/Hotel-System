"""Menu QR Code Generator - Kozbeyli Konagi"""
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
import io

router = APIRouter(tags=["qr"])

MENU_URL = "https://kozbeylikonagi.com.tr"


@router.get("/qr/menu")
async def get_menu_qr(
    size: int = Query(default=300, ge=100, le=1000),
    format: str = Query(default="png", regex="^(png|svg)$"),
):
    """Generate QR code for the menu page."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(MENU_URL)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        color_mask=SolidFillColorMask(
            back_color=(10, 10, 15),
            front_color=(196, 151, 42),
        ),
    )

    # Resize
    img = img.resize((size, size))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=kozbeyli-menu-qr.png"},
    )


@router.get("/qr/menu-info")
async def get_qr_info():
    """Get QR code metadata."""
    return {
        "url": MENU_URL,
        "qr_endpoint": "/api/qr/menu",
        "sizes": [200, 300, 500, 800],
        "description": "Kozbeyli Konagi Menu QR Kodu - Masalara yerlestirmek icin",
    }
