
# Kook_Live_Bot

This is a BiliBili live push bot for Kook .

![demo](assets/image.png)

![show all](assets/show.png)

## Features

- [x] Subscribe BiliBili live room
- [x] Unsubscribe BiliBili live room
- [x] Auto push live stream message to chat channel.
- [x] Show all Subscribed live rooms

## Getting Started

You should copy `.env.example` to `.env` and fill in the required values.

```bash
$ docker-compose up -d
```

### Prerequisites

`poetry` is required to install dependencies.

```bash
$ pip install poetry
```

And then install dependencies.

```bash
$ poetry install
```

## TODO

- [ ] Support multiple chat channels and multiple server or guild
- [ ] Add more live room info
- [ ] Support more live platform such as `Douyu` `Huya` `Bilibili` `Youtube` `Twitch``
- [ ] Add AI features to this bot, Maybe.

## Thanks

- [khl.py](https://github.com/TWT233/khl.py)
- [Harukubot](https://github.com/SK-415/HarukaBot/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.