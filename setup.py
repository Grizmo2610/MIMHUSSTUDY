from Database import init_db, Database

if __name__ == "__main__":
    init_db(reset=True)
    tags = [
    "midterm",
    "final",
    "reference",
    "exercise",
    "textbook",
    "revision",
    "personal"
    ]
    db = Database()
    
    for tag in tags:
        db.new_tag(tag)