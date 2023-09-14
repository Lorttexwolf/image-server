from sanic import Sanic
import os
from config import SERVER_HOST, SERVER_PORT, DEBUG_MODE
from middleware import auth
import importlib
import logging

logging.basicConfig()


def register_routes(app, path=None):
    path = path or ["src/routes"]
    files = os.listdir("/".join(path))

    for file_or_folder in files:
        if "__" not in file_or_folder:
            if os.path.isdir(f"{'/'.join(path)}/{file_or_folder}"):
                register_routes(app, path + [f"{file_or_folder}"])
            else:
                proper_path = "/".join(path) + "/" + file_or_folder
                import_name = proper_path.replace("/", ".").replace(".py", "").replace("src.", "")

                route_module = importlib.import_module(import_name)
                route = getattr(route_module, "Route")()

                logging.info(f"Registering route: {getattr(route, 'METHODS')} {getattr(route, 'PATH')}")
                app.add_route(
                    getattr(route, "handler"),
                    getattr(route, "PATH"),
                    getattr(route, "METHODS"),
                    name=getattr(route, "PATH"),
                )


app = Sanic("BloxlinkImageServer")
register_routes(app)
app.register_middleware(auth, "request")
app.static("/assets", "./assets")

if __name__ == "__main__":
    app.run(
        SERVER_HOST,
        SERVER_PORT,
        fast=not DEBUG_MODE,
        debug=DEBUG_MODE,
        access_log=DEBUG_MODE,
    )
