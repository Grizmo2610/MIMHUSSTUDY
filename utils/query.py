import re

def split_search_text(text: str):
    """
    Split text theo space nhưng giữ nguyên các chuỗi trong dấu ""
    """
    # regex: ".*?" → match các chuỗi trong "", \S+ → match các từ không phải space
    pattern = r'"(.*?)"|(\S+)'
    matches = re.findall(pattern, text)

    # re.findall trả về list tuple (group1, group2)
    tokens = [m[0] if m[0] else m[1] for m in matches]
    return tokens