from pydantic import BaseModel


class RenameSessionRequest(
    BaseModel
):

    title: str