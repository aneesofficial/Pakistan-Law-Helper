from utils.rag import answer_question

print("TEST 1: Article 5")
ans, src = answer_question('What does Article 5 of the Constitution of Pakistan say about loyalty to the State and obedience to the Constitution and law? Explain both clauses in simple language and cite the exact Article.', 'Federal')
print(f"Top Source: {src[0]['section_number'] if src else 'None'}")
print(f"Answer snippet: {ans[:200]}")
print("\n" + "="*50 + "\n")

print("TEST 2: Article 8")
ans, src = answer_question('Explain Article 8 of the Constitution of Pakistan in detail. What happens to laws inconsistent with or in derogation of Fundamental Rights? Explain the sub-clauses in simple language.', 'Federal')
print(f"Top Source: {src[0]['section_number'] if src else 'None'}")
print(f"Answer snippet: {ans[:200]}")
print("\n" + "="*50 + "\n")

print("TEST 3: Freedom of Speech")
ans, src = answer_question('What constitutional protection is provided for freedom of speech and expression?', 'Federal')
print(f"Top Source: {src[0]['section_number'] if src else 'None'}")
print(f"Answer snippet: {ans[:200]}")
print("\n" + "="*50 + "\n")

print("TEST 4: Unknown Law (PECA)")
ans, src = answer_question('What is the punishment for cyber terrorism under PECA?', 'Federal')
print(f"Top Source: {src[0]['section_number'] if src else 'None'}")
print(f"Answer snippet: {ans[:200]}")
print("\n" + "="*50 + "\n")
