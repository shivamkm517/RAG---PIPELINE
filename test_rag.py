from app.chains.rag_chain import rag_chain


query = "What is the main topic of the document?"

answer = rag_chain(query)

print("\nANSWER:\n")
print(answer)