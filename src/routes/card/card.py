from sanic.response import raw
from PIL import Image, ImageFont, ImageDraw, UnidentifiedImageError, ImageOps, ImageEnhance, ImageFilter
from io import BytesIO
from config import DEFAULT_GETINFO_BACKGROUND, ERROR_WEBHOOK, DEBUG_MODE
from IMAGES import IMAGE_CONFIG
from typing import Optional, Tuple, List
from utils.text_wrap import TextWrapper
from utils.text_cleanse import cleanse
import aiohttp
import datetime
import traceback
import logging


def make_shadow(img: Image.Image) -> Image.Image:
    # There MUST be a better way to do this, I'm not knowledgeable enough in this field.  
    # Using ImageOps.colorize with white highs and transparent lows?
    img = ImageEnhance.Brightness(img).enhance(100)
    img = ImageEnhance.Contrast(img).enhance(0.8)
    return img.filter(ImageFilter.MaxFilter(3))

class Route:
    PATH = "/card"
    METHODS = ("GET", )
    
    AVATAR_SIZE = (888, 888)
    AVATAR_POSITION = (-90, 25)

    def __init__(self):
        self.header1 = ImageFont.truetype("fonts/TovariSans.ttf", 35)
        self.header2 = ImageFont.truetype("fonts/TovariSans.ttf", 80)
        self.bloxlink_head_image = Image.open("assets/clear_logo.png").resize((100, 150))
        self.session: aiohttp.ClientSession = None

    async def handler(self, request):
        if self.session == None:
            self.session = aiohttp.ClientSession()
        
        json_data: dict = request.json
        background_name = json_data.get("background")
        background_name = background_name if background_name and IMAGE_CONFIG.get(background_name, {}).get("paths", {}).get("card", {}).get("whole") else DEFAULT_GETINFO_BACKGROUND
        joined_at = json_data.get("joined_at")
        joined_at = datetime.datetime.fromisoformat(joined_at) if joined_at else None
        avatar_url: str = json_data.get("full_avatar_url")
        overlay = json_data.get("overlay", None)
        
        background_config = IMAGE_CONFIG[background_name]
        background_path = background_config["paths"]["card"]["whole"]
        
        has_prop_outline = background_config.get("props", {}).get("card", {}).get("outline", False)
        
        # background_props = background_config.get("props", ("moon.png", "HEADSHOT", "BACKGROUND", "moon_outline.png"))
        # background_hexes = background_config.get("hexes", {})

        try:
            with Image.open(background_path) as background_image:
                image = Image.new("RGBA", (background_image.width, background_image.height))
                
                # Paste the background image.
                image.paste(background_image, (0, 0))
                image.paste(self.bloxlink_head_image, (1530, 10), self.bloxlink_head_image) 
                
                if avatar_url:                
                    # Load, then paste the avatar image.
                    async with self.session.get(avatar_url) as resp:
                        try:
                            data = BytesIO(await resp.read())
                            avatar_image  = Image.open(data)
                            shadow_avatar: Optional[Image.Image] = None
                            if has_prop_outline:
                                shadow_avatar = make_shadow(avatar_image)       
                                                     
                        except UnidentifiedImageError as ex:
                            logging.error(ex)
                            pass 
                        else:
                            shadow_scalar = 2
                            
                            # Resize the avatar image to fit our needs.
                            if shadow_avatar:
                                shadow_avatar = shadow_avatar.resize((self.AVATAR_SIZE[0] + 10 * shadow_scalar, self.AVATAR_SIZE[1] + 5 * shadow_scalar))
                            avatar_image = avatar_image.resize(self.AVATAR_SIZE)
                                                                            
                            # Paste the avatar and shadow image.
                            if shadow_avatar:
                                image.paste(shadow_avatar, (self.AVATAR_POSITION[0] - 5 * shadow_scalar, self.AVATAR_POSITION[1] - 5), shadow_avatar)
                                # image.paste(shadow_avatar, (self.AVATAR_POSITION[0] + 200, self.AVATAR_POSITION[1] - 14), shadow_avatar)
                            image.paste(avatar_image, self.AVATAR_POSITION, avatar_image)
                            
                            # Dispose of the data related to the images to prevent leaks.
                            avatar_image.close()
                            if shadow_avatar:
                                shadow_avatar.close()
                        
                # TODO: Create card overlays
                # if overlay:
                #     with Image.open(f"./assets/props/overlays/{overlay}.png") as overlay_image:
                #         image.paste(overlay_image, (0, 0), overlay_image)

                # Create a drawing context so we can write text.
                draw = ImageDraw.Draw(image)
                if joined_at:
                    draw.text((1280, 52), f"Joined {joined_at.strftime(f'%m/%d/%Y')}", (140, 140, 140), align="right", font=self.header1)
                
            with BytesIO() as bf:
                image.save(bf, "PNG", quality=70)
                image.seek(0)

                return raw(bf.getvalue(), content_type="image/png")

        except Exception as e:
            logging.error(e)

