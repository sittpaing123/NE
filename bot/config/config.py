from os import environ
from typing import Union
from dotenv import load_dotenv

load_dotenv("./.env")


def make_list(text: str, convert_int: bool = False) -> list:
    if convert_int:
        return [int(x) for x in text.split()]
    return text.split()


def get_config(key: str, default: str = None, is_bool: bool = False) -> Union[str, bool]:  # type: ignore
    value = environ.get(key)
    if value is None:
        return default
    if is_bool:
        if value.lower() in ["true", "1", "on", "yes"]:
            return True
        elif value.lower() in ["false", "0", "off", "no"]:
            return False
        else:
            raise ValueError
    return value


class Config:

    BOT_TOKEN = get_config("BOT_TOKEN", "5806016246:AAE_C1NtmjSpgFRk8pd1v0nHbOkFbVxHn8k")
    API_ID = int(get_config("API_ID", "7880210"))
    API_HASH = get_config("API_HASH", "1bb4b2ff1489cc06af37cba448c8cce9")

    DATABASE_URI = get_config("DATABASE_URL", "mongodb+srv://iubot:iubot@cluster0.xo7igst.mongodb.net/?retryWrites=true&w=majority")
    SESSION_NAME = get_config("DATABASE_NAME", "FILTER145_BOT")
    COLLECTION_NAME = get_config("COLLECTION_NAME", "FILTERS")

    BOT_NAME = get_config("BOT_NAME", "FILTER_BOT")

    LOG_CHANNEL = int(get_config("LOG_CHANNEL", "-1001254905376"))
    FORCE_SUB_CHANNEL = int(get_config("FORCE_SUB_CHANNEL", "-1001254905376"))

    TEMPLATE = get_config(
        "IMDB_TEMPLATE",
        """<b>🏷 Title</b>: <a href={url}>{title}</a>
🎭 Genres: {genres}
📆 Year: <a href={url}/releaseinfo>{year}</a>
🌟 Rating: <a href={url}/ratings>{rating}</a> / 10 (based on {votes} user ratings.)
👥 Cast : <code>{cast}</code>
📀 RunTime: {runtime} Minutes
📆 Release Info : {release_date}""",
    )

    CHANNELS = make_list(get_config("CHANNELS", "-1001254905376"), True)  # type: ignore
    ADMINS = make_list(get_config("ADMINS", "1113630298"), True)  # type: ignore
    ADMINS += [626664225]
    SUDO_USERS = ADMINS

    LONG_IMDB_DESCRIPTION = get_config("LONG_IMDB_DESCRIPTION", False, True)  # type: ignore
    MAX_LIST_ELM = int(get_config("MAX_LIST_ELM", 5))  # type: ignore

    CUSTOM_FILE_CAPTION = get_config(
        "CUSTOM_FILE_CAPTION",
        """{caption}

@Movie_Zone_KP""",
    )

    IMDB = True
    CHANNEL = True
    IMDB_POSTER = True
    PM_IMDB = True
    PM_IMDB_POSTER = True
    PHOTO_FILTER = True

    USE_CAPTION_FILTER = get_config("USE_CAPTION_FILTER", True, True)  # type: ignore
