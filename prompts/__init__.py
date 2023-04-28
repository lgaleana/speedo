with open("prompts/chat.txt") as p:
    chat_prompt = p.read()
    p.close()


with open("prompts/flights.txt") as p:
    flights_prompt = p.read()
    p.close()


with open("prompts/flights_api.txt") as p:
    flights_api_prompt = p.read()
    p.close()
