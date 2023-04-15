from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from fastapi.params import Query
from src import database as db

router = APIRouter()

@router.get("/movies/{line_id}", tags=["lines"])
def get_lines(line_id: int):
    return 0

def get_conversation():
    return 0

def lines():
    return 0
