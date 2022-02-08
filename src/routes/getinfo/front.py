from sanic.response import raw
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from config import DEFAULT_GETINFO_BACKGROUND
from IMAGES import IMAGE_CONFIG
from utils.text_wrap import TextWrapper
from utils.text_cleanse import cleanse
import aiohttp


class Route:
    PATH = "/getinfo/front"
    METHODS = ("GET", )

    def __init__(self):
        self.header1 = ImageFont.truetype("fonts/TovariSans.ttf", 100)
        self.header2 = ImageFont.truetype("fonts/TovariSans.ttf", 50)
       # self.header3 = ImageFont.truetype("fonts/cartoonist/TovariSans.ttf", 90)
        self.header4 = ImageFont.truetype("fonts/TovariSans.ttf", 40)
        self.header5 = ImageFont.truetype("fonts/TovariSans.ttf", 30)

        self.session = None

    async def handler(self, request):
        background   = request.args.get("background")
        background   = background if background != "null" and IMAGE_CONFIG.get(background, {}).get("paths", {}).get("getinfo", {}).get("front") else DEFAULT_GETINFO_BACKGROUND

        banned       = request.args.get("banned") == "true"
        username     = request.args.get("username")
        display_name = request.args.get("display_name") if not banned else ""
        description  = cleanse(request.args.get("description", "")) or "No description available."
        headshot     = request.args.get("headshot")
        overlay      = request.args.get("overlay")
        roblox_id    = request.args.get("id")
        roblox_age   = request.args.get("age")

        if banned:
            background = "black"

        background_config = IMAGE_CONFIG[background]
        background_path = background_config["paths"]["getinfo"]["front"]
        background_props = background_config.get("props", {})
        background_hexes = background_config.get("hexes", {})

        primary_color = background_hexes.get("primary_color", (240, 191, 60))

        # image storage for closing
        headshot_image = None

        # buffer storage
        headshot_buffer = None

        if not self.session:
            self.session = aiohttp.ClientSession()

        first_font_size = self.header1
        second_font_size = self.header2

        adjusted_name_pos_1 = 290
        adjusted_name_pos_2 = 370

        if len(username) >= 20:
            username = f"{username[:20]}..."

        if len(display_name) >= 20:
            display_name = f"{display_name[:20]}..."

        if len(username) >= 10 or len(display_name) >= 10:
            first_font_size = self.header2
            second_font_size = self.header2
            adjusted_name_pos_1 = 320
            adjusted_name_pos_2 = 370

        # TODO: if bg is deleted, then revert to default

        with Image.open(background_path) as background_image:
            image = Image.new("RGBA", (background_image.width, background_image.height))

            if headshot:
                async with self.session.get(headshot) as resp:
                    moon_prop = background_props.get("moon", "moon.png")
                    moon_outline = background_props.get("moon_outline", "moon_outline.png")

                    with Image.open(f"./assets/props/{moon_prop}") as moon_image:
                        with Image.open("./assets/props/moon_outline.png") as moon_outline_image:
                            headshot_buffer = BytesIO(await resp.read())

                            headshot_image  = Image.open(headshot_buffer)
                            headshot_image  = headshot_image.resize((220, 220))

                            if moon_prop:
                                image.paste(moon_image, (0, 0), moon_image)

                            image.paste(headshot_image, (160, 70), headshot_image)
                            image.paste(background_image, (0, 0), background_image)

                            if moon_outline:
                                image.paste(moon_outline_image, (0, 0), moon_outline_image)


            if overlay:
                with Image.open(f"./assets/props/overlays/{overlay}.png") as overlay_image:
                    image.paste(overlay_image, (0, 0), overlay_image)

            draw = ImageDraw.Draw(image)

            if username:
                username = f"@{username}"

                if display_name:
                    if username[1:] == display_name:
                        # header is username. don't display display_name
                        width_username = draw.textsize(username, font=first_font_size)[0]

                        draw.text(
                            ((image.size[0]-width_username) / 2, adjusted_name_pos_1),
                            username,
                            (255, 255, 255),
                            font=first_font_size
                        )
                    else:
                        # show both username and display name
                        width_display_name  = draw.textsize(display_name, font=first_font_size)[0]
                        draw.text(
                            ((image.size[0]-width_display_name) / 2, adjusted_name_pos_1),
                            display_name,
                            primary_color,
                            font=first_font_size)

                        width_username = draw.textsize(username, font=second_font_size)[0]
                        draw.text(
                            ((image.size[0]-width_username) / 2, adjusted_name_pos_2),
                            username,
                            (255, 255, 255),
                            font=second_font_size)

                else:
                    width_username = draw.textsize(username, font=first_font_size)[0]

                    draw.text(
                        ((image.size[0]-width_username) / 2, adjusted_name_pos_1),
                        username,
                        (255, 255, 255),
                        font=first_font_size
                    )

            roblox_id_age_offset = 10 if not overlay else 40

            if roblox_age:
                draw.text(
                    (10, roblox_id_age_offset),
                    f"Minted {roblox_age}",
                    primary_color,
                    font=self.header5
                )

            if roblox_id:
                draw.text(
                    (10, roblox_id_age_offset+25),
                    f"#{roblox_id}",
                    primary_color,
                    font=self.header5
                )

            if description:
                if len(description) > 500:
                    description = f"{description[:500]}..."

                wrapper = TextWrapper(description, self.header5, image.width-70)

                # import time
                # avg_1 = []
                # for i in range(1000):
                #     start = time.time()
                #     wrapped_text = wrapper.wrapped_text1()
                #     end = time.time()
                #     time_delta = end-start
                #     avg_1.append(time_delta)

                # print(sum(avg_1)/len(avg_1))

                # avg_2 = []
                # for i in range(1000):
                #     start = time.time()
                #     wrapped_text = wrapper.wrapped_text2()
                #     end = time.time()
                #     time_delta = end-start
                #     avg_2.append(time_delta)

                # print(sum(avg_2)/len(avg_2))

                wrapped_text = wrapper.wrapped_text()

                draw.text(
                    (40, 505),
                    wrapped_text,
                    (255, 255, 255),
                    font=self.header5
                )

            if banned:
                width_banned = draw.textsize("This user is banned.", font=self.header4)[0]
                draw.text(
                    ((image.size[0]-width_banned) / 2, 400),
                    "This user is banned.",
                    (255, 0, 0),
                    font=self.header4
                )

        try:
            with BytesIO() as bf:
                image.save(bf, "PNG", quality=70)
                image.seek(0)

                return raw(bf.getvalue())

        finally:
            if headshot_buffer:
                headshot_buffer.close()

            if image:
                image.close()

            if headshot_image:
                headshot_image.close()
