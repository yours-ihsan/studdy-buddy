import db

CARDS = [
    ("operating systems", "What is a process?",
     "A running instance of a program with its own memory space."),
    ("operating systems", "What is a thread?",
     "A unit of execution inside a process; threads share its memory."),
    ("operating systems", "What is a deadlock?",
     "Processes waiting on each other forever, so none can proceed."),
    ("networking", "What does TCP guarantee?",
     "Reliable, ordered delivery of a byte stream."),
    ("networking", "What is DNS?",
     "The system that maps domain names to IP addresses."),
]

if __name__ == "__main__":
    db.init_db()
    added = 0
    with db.get_conn() as conn:
        for topic, question, answer in CARDS:
            exists = conn.execute(
                "SELECT 1 FROM flashcards WHERE topic = ? AND question = ?",
                (topic, question),
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO flashcards (topic, question, answer) VALUES (?, ?, ?)",
                    (topic, question, answer),
                )
                added += 1
    print(f"Added {added} card(s).")
    