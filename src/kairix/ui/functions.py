import json
import uuid
from typing import Optional
import logging

from kairix.types import SourceDocument


logger = logging.getLogger(__name__)

running_output = ""


def log_info(msg: str) -> None:
    global running_output
    logger.info(msg)
    running_output += "\n" + msg
    return running_output


def parse_mapping(mapping: dict) -> Optional[str]:
    if type(mapping) is not dict:
        return None

    if "message" not in mapping:
        return None

    message = mapping["message"]
    if type(message) is not dict or "content" not in message:
        return None

    content = message["content"]
    if type(content) is not dict or "parts" not in content:
        return None

    parts = content["parts"]
    if type(parts) is not list:
        return None

    text = "\n".join(parts)

    sender, timestamp = ("unknown", "unknown")

    if "author" in message.keys():
        author = message["author"]

        if "role" in author.keys():
            sender = author["role"]
    if "create_time" in message.keys():
        timestamp = message["create_time"]

    return f"({timestamp})-{sender}: {text}\n"


def load_from_file(file_name: str | list[str]):
    documents = []
    if isinstance(file_name, list):
        if not file_name:
            yield log_info("No file selected")
            return
        file_name = file_name[0]
    yield (f"Loading {file_name}")
    with open(file_name, "r") as f:
        data = json.load(f)
        yield log_info(f"Loaded {len(data)} conversations.")
        for d in data:
            title = d["title"]
            id_to_mapping = d["mapping"]
            if id_to_mapping is None:
                yield log_info(f"Skipping convo {title} with no messages.")

            yield log_info(f"Processing conversation: {title}")
            yield log_info(f"# of mappings: {len(id_to_mapping)}")

            messages = []
            for key, mapping in id_to_mapping.items():
                text = parse_mapping(mapping)
                if text is not None:
                    messages.append(text)

            yield log_info(
                f"Writing graph db record for {title}, # of messages: {len(messages)}"
            )
            doc = SourceDocument(
                uid=uuid.uuid4().urn,
                source_label=title,
                source_type="chatgpt",
                content="\n".join(messages),
            )
            doc.save()
            documents.append(doc)

            yield log_info(
                "finished! Wrote Source Docuemnts:"
                + "\n".join([d.source_label for d in documents])
            )
