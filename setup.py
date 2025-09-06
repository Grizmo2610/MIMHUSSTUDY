from Database import init_db, Database
from utils import Tag
if __name__ == "__main__":
    init_db(reset=True)
    db = Database()
    
    for tag in Tag:
        db.new_tag(tag.value)