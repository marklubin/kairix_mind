from dotenv import load_dotenv
from os import getenv
from neomodel import config as neomodel_config
from neomodel import db

from kairix.types import SourceDocument
import logging

load_dotenv(verbose=True)


def get_or_raise(key: str):
    if getenv(key) is None:
        raise KeyError(f"Missiing required configuration for: {key}")
    return getenv(key)


# Setup Neo4j
neomodel_config.DATABASE_URL = get_or_raise("NEO4J_URL")

SourceDocument(
    uid="1", source_label="smoke-test", source_type="none"
).create_or_update()
db.install_all_labels()


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
