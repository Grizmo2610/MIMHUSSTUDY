from fastapi import APIRouter
from typing import Optional
from Database import Database

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/search")
def search_documents(
    title: str,
    school: Optional[str] = None,
    faculty: Optional[str] = None,
    author: Optional[str] = None,
    course: Optional[str] = None,
    subject: Optional[str] = None
):
    db = Database()
    sql = """SELECT *
    FROM documents
    WHERE title ILIKE %s
      AND (%s IS NULL OR school = %s)
      AND (%s IS NULL OR faculty = %s)
      AND (%s IS NULL OR author ILIKE %s)
      AND (%s IS NULL OR course ILIKE %s)
      AND (%s IS NULL OR subject ILIKE %s)
    """
    params = (
        f"%{title}%", school, school,
        faculty, faculty,
        author, f"%{author}%" if author else None,
        course, f"%{course}%" if course else None,
        subject, f"%{subject}%" if subject else None
    )
    results = db.fetchall(sql, params)
    db.close()
    return {"results": results}
