from app.memory.database import SessionLocal
from app.memory.repository import create_thread
from app.chains.query_chain import answer_query


db = SessionLocal()

thread = create_thread(db, "RAG Conversation")

db.close()

print(f"Thread ID: {thread.id}")

print("\n--- Question 1 ---")
print(answer_query("What is WorkHub?", thread.id))

print("\n--- Question 2 ---")
print(answer_query("What are its main features?", thread.id))