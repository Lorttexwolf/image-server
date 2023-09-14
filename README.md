# Bloxlink Image Server

Generates beautiful images of Roblox characters!

## Generating Images

You can generate horizontal image cards following this format:

```sh
curl --location --request GET '{HOST}/card' \
--header 'Authorization: {KEY}' \
--header 'Content-Type: application/json' \
--data '{
    "background": "merch_storm",
    "joined_at": "2023-09-13T16:17:40.078Z",
    "avatar_url": "https://tr.rbxcdn.com/dc6ae7d91aab1ea9430c5de505413b27/720/720/Avatar/Png" 
}'
```

When requesting an image, you may specify different `background` images such as [breezy_meadows](assets/backgrounds/card/whole/breezy_meadows.png) and [merch_storm](assets/backgrounds/card/whole/merch_storm.png). You
can view all images under [assets](assets) depending on the route.

_See codebase to use other routes_.

## Development

The Bloxlink image-server utilizes poetry to manage Python packages along with the [Sanic Framework](https://sanic.dev/en/) to run the web server.

```sh
poetry install && poetry run python src/main.py
```

### 🚧 Incomplete Features

- [ ] Card images are not configured with props nor do prop assets match card ratio.
- [ ] Simplify and solidify [image configurations](src/IMAGES.py) schema along with functions to access configurations.
- [ ] Revise codebase and integrate future libraries.
