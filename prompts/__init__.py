with open("prompts/chat_instructions.txt") as p:
    chat_prompt = p.read()
    p.close()


with open("prompts/flights_instructions.txt") as p:
    flights_prompt = p.read()
    p.close()