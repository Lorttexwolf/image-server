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

When requesting an image, you may specify different `background` images. You
can view all images under [assets](assets) depending on the route.

_See codebase to use other routes_.

## Development

The Bloxlink image-server utilizes poetry to manage Python packages.

```sh
poetry install && poetry run python src/main.py
```
