import urllib.request
import json
import time

questions = [
    "What does Article 5 of the Constitution of Pakistan say about loyalty to the State and obedience to the Constitution and law? Explain both clauses in simple language and cite the exact Article.",
    "Explain Article 8 of the Constitution of Pakistan in detail. What happens to laws inconsistent with or in derogation of Fundamental Rights? Explain the sub-clauses in simple language.",
    "What constitutional protection is provided for freedom of speech and expression?",
    "What is the punishment for cyber terrorism under PECA?"
]

print("--- Testing GET /api/health ---")
try:
    health = urllib.request.urlopen('http://localhost:8000/api/health', timeout=10).read().decode()
    print("Health response:", health)
except Exception as e:
    print("Health check failed:", e)

for i, q in enumerate(questions, 1):
    print(f"\n--- Testing POST /api/ask (Question {i}) ---")
    print(f"Question: {q}")
    data = json.dumps({"question": q, "province": "Federal"}).encode('utf-8')
    req = urllib.request.Request('http://localhost:8000/api/ask', data=data, headers={'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(req, timeout=60)
        res_body = json.loads(response.read().decode('utf-8'))
        print(f"Status Code: {response.getcode()}")
        print(f"Answer snippet: {res_body.get('answer', '')[:200]}...")
        if res_body.get('sources'):
            print(f"Top Source: {res_body['sources'][0].get('section_number')}")
        else:
            print("Sources: None")
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code}")
        print(e.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    
    if i < len(questions):
        print("Sleeping 20 seconds to respect API rate limits...")
        time.sleep(20)
