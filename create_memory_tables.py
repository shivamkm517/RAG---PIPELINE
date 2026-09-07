from app.memory.database import Base, engine
from app.memory.models import Thread, Message


Base.metadata.create_all(bind=engine)

print("Memory tables created.")

