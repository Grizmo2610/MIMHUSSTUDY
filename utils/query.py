import re
from .intances import Document
from dataclasses import asdict

def split_search_text(text: str):
    """
    Split text theo space nhưng giữ nguyên các chuỗi trong dấu ""
    """
    # regex: ".*?"-> match các chuỗi trong "", \S+ -> match các từ không phải space
    pattern = r'"(.*?)"|(\S+)'
    matches = re.findall(pattern, text)

    # re.findall trả về list tuple (group1, group2)
    tokens = [m[0] if m[0] else m[1] for m in matches]
    return tokens

def result_formatter(rows: list):
    documents = []
    for row in rows:
        doc_obj = Document.from_db_row(row)
        
        doc_dict = asdict(doc_obj)
        
        documents.append(doc_dict)
        
    return documents
