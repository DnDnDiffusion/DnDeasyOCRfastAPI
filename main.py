# pylint: disable=missing-function-docstring
import io
import logging
import re

from fastapi import FastAPI, APIRouter, Request, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
import easyocr
from fastapi.middleware.cors import CORSMiddleware

import PIL
from PIL import Image, ImageOps
import numpy
import json




app = FastAPI()
router = APIRouter()
ocr = easyocr.Reader(["en"])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    colours = ["(Black Dragon Ancestry)", "(Blue Dragon Ancestry)", "(Brass Dragon Ancestry)", "(Bronze Dragon Ancestry)", "(Copper Dragon Ancestry)", "(Gold Dragon Ancestry)", "(Green Dragon Ancestry)", "(Red Dragon Ancestry)", "(Silver Dragon Ancestry)", "(White Dragon Ancestry)"]
    pattern = '|'.join(colours)
    match = re.search(pattern, ocrtext, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return "Not a Dragonborn"
    
# look through the text and return what the background is
def background(ocrtext):
    backgrounds = ["Acolyte", "Charlatan", "Criminal", "Entertainer", "Folk Hero", "Guild Artisan", "Hermit", "Noble", "Outlander", "Sage", "Sailor", "Soldier", "Urchin", "Anthropologist", "Archaeologist", "Black Fist Double Agent", "City Watch", "Clan Crafter", "Cloistered Scholar", "Courtier", "Criminal Spy", "Dissenter", "Dragon Casualty", "Earthspur Miner", "Faction Agent", "Far Traveler", "Firefighter", "Fist of Hextor", "Gate Urchin", "Gladiator", "Harper", "Haunted One", "House Agent", "Inheritor", "Initiate", "Inquisitor", "Iron Route Bandit", "Knight of the Order", "Mercenary Veteran", "Mulmaster Aristocrat", "Noble Duelist", "Order of the Gauntlet", "Outcast", "Pirate"]
    pattern = '|'.join(backgrounds)
    match = re.search(pattern, ocrtext, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return "Not a Background"

# look through the text and return what Armor is Worn
def armor_worn(ocrtext):
    pattern = r"Armor Worn:\s*(\w+)"
    # Search for the pattern in the string
    match = re.search(pattern, ocrtext)
    # Extract the matched substring
    if match:
        substring = match.group(1)
        if substring == "none":
            return "clothes"
        return substring
    else:
        return "No Armor"

def weapon(ocrtext):
    weapons = ["Club", "Dagger", "Greatclub", "Handaxe", "Javelin", "Light Hammer", "Mace", "Quarterstaff","Sickle", "Spear", "Crossbow, light", "Dart", "Shortbow", "Sling", "Battleaxe", "Flail", "Glaive", "Greataxe", "Greatsword", "Halberd", "Lance", "Longsword", "Maul", "Morningstar","Pike", "Rapier", "Scimitar", "Shortsword", "Trident", "War pick", "Warhammer", "Whip", "Blowgun", "Crossbow, hand", "Crossbow, heavy", "Longbow", "Net"]
    pattern = '|'.join(weapons)
    match = re.search(pattern, ocrtext, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return "No weapon"
    
def mood_and_tone(ocrtext):
    alignments = ['Lawful Good', 'Neutral Good', 'Chaotic Good', 'Lawful Neutral', 'True Neutral', 'Chaotic Neutral', 'Lawful Evil', 'Neutral Evil', 'Chaotic Evil']
    pattern = '|'.join(alignments)
    match = re.search(pattern, ocrtext, re.IGNORECASE)
    if match:
        return match.group()
    else:
        return "No alignment"

@app.get("/")
async def root():
    return {"message": "Hello World"}


# @router.post("/ocr")
@app.post("/ocr")
async def do_ocr(request: Request, file: UploadFile = File(...)):
    if file is not None:
        try:
            imgFile = numpy.array(PIL.Image.open(file.file).convert("RGB"))
            res = ocr.readtext(imgFile)
            ocrtext = str(res)
            result = {"ocrtext": ocrtext,"dragonborn_colour": dragonborn_colour(ocrtext),"class_level": class_level(ocrtext),"background": background(ocrtext),"armor_worn": armor_worn(ocrtext),"weapon": weapon(ocrtext),"mood_and_tone": mood_and_tone(ocrtext)}
            return json.dumps(result)
        except Exception as e:
            print(e)
            return {"error": "OCR failed."}
    else:
        return {"error": "missing file"}


app.include_router(router)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
