# pylint: disable=missing-function-docstring
import io
import logging
import re

from fastapi import FastAPI, APIRouter, Request, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
import easyocr

import PIL
from PIL import Image, ImageOps
import numpy

app = FastAPI()
router = APIRouter()
ocr = easyocr.Reader(["en"])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr")

# look through the ocrtext and return the class and level
def class_level(ocrtext):
    classes = ["Ranger", "Fighter", "Rogue", "Wizard", "Cleric", "Barbarian", "Monk", "Paladin", "Druid", "Sorcerer", "Bard", "Warlock", "Artificer"]
    pattern = '|'.join(classes)
    match = re.search(pattern, ocrtext, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return "Not a Class"
# look through the text and return what colour the dragonborn is
def dragonborn_colour(ocrtext):
    classes = ["(Black Dragon Ancestry)", "(Blue Dragon Ancestry)", "(Brass Dragon Ancestry)", "(Bronze Dragon Ancestry)", "(Copper Dragon Ancestry)", "(Gold Dragon Ancestry)", "(Green Dragon Ancestry)", "(Red Dragon Ancestry)", "(Silver Dragon Ancestry)", "(White Dragon Ancestry)"]
    pattern = '|'.join(classes)
    match = re.search(pattern, ocrtext, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return "Not a Dragonborn"



@app.get("/")
async def root():
    return {"message": "Hello World"}


# @router.post("/ocr")
@app.post("/ocr")
async def do_ocr(request: Request, file: UploadFile = File(...)):
    if file is not None:
        # res = ocr.readtext(await file.read())
        # res = ocr.readtext(file.file)
        # via pil
        imgFile = numpy.array(PIL.Image.open(file.file).convert("RGB"))
        res = ocr.readtext(imgFile)
        ocrtext = str(res)
        # return array of strings
        return [dragonborn_colour(ocrtext),class_level(ocrtext)]
        # probable_text = "\n".join((item[1] for item in res))
        # return StreamingResponse(
        #     io.BytesIO(probable_text.encode()), media_type="text/plain"
        # )

    return {"error": "missing file"}


@app.post("/ocr_form")
async def do_ocr_form(request: Request, file: UploadFile = File(...)):
    # form = await request.form()
    # file = form.get("file", None)
    if file is not None:
        # res = ocr.readtext(await file.read())
        res = ocr.readtext(file.file.read())
        return [item[1] for item in res]

    return {"error": "missing file"}


app.include_router(router)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
