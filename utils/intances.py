from enum import Enum
from typing import Optional
from datetime import datetime
import uuid
from dataclasses import dataclass

class Tag(Enum):
    MIDTERM = "midterm"
    FINAL = "final"
    REFERENCE = "reference"
    EXERCISE = "exercise"
    TEXTBOOK = "textbook"
    REVISION = "revision"
    PERSONAL = "personal"

@dataclass
class Document:
    uuid: uuid.UUID
    path: str
    school: str
    faculty: str
    title: str
    description: Optional[str]
    author: Optional[str]
    created_at: datetime
    last_updated: datetime
    subject: str
    course: Optional[str]
    language: str
    file_size: Optional[int]
    uploaded_by: Optional[int]
    access_level: str
    download_count: int

    @classmethod
    def from_db_row(cls, row: tuple):
        return cls(
            uuid=row[1],
            path=row[2],
            school=row[3],
            faculty=row[4],
            title=row[5],
            description=row[6],
            author=row[7],
            created_at=row[8],
            last_updated=row[9],
            subject=row[11],
            course=row[12],
            language=row[13],
            file_size=row[15],
            uploaded_by=row[16],
            access_level=row[17],
            download_count=row[18]
        )