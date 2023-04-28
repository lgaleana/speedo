BASE = "tasks/prompts"

with open(f"{BASE}/chat.txt") as p:
    chat_prompt = p.read()
    p.close()


with open(f"{BASE}/flights.txt") as p:
    flights_prompt = p.read()
    p.close()


with open(f"{BASE}/flights_api.txt") as p:
    flights_api_prompt = p.read()
    p.close()
