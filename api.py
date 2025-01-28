from os import getenv

from flask import Blueprint, request

high_priority = getenv("HIGH_PRIORITY_QUEUE")
router = Blueprint("messages", __name__, url_prefix="/")

@router.post("/")
def post_message():
    message = request.json
