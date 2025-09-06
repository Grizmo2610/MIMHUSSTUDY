from fastapi import APIRouter, Query
from typing import Optional
from Database import Database
from utils import *
router = APIRouter()

@router.get("/search")
def search_documents_endpoint(
    title: str,
    limit: int = Query(10, ge=5),
    offset: int = Query(0, ge=0),
):
    """
    Endpoint gọi trực tiếp Database.search_documents với filters động
    """
    db = Database()

    # Gọi method search_documents
    results = db.search_documents(text=title, 
                                #   filters=filters
                                  )

    # Paging: slice kết quả
    paged_results = results[offset:offset+limit]

    db.close()

    return {"results": result_formatter(paged_results)}