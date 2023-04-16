with open("prompts/chat.txt") as p:
    chat_prompt = p.read()
    p.close()


with open("prompts/flights.txt") as p:
    flights_prompt = p.read()
    p.close()


with open("prompts/flights_summary.txt") as p:
    flights_summary_prompt = p.read()
    p.close()