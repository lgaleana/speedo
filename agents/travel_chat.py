from concurrent.futures import ThreadPoolExecutor

import agents as a
import tasks as t
from llm_watch.lib import chain_watch, validate_with_user_feedback
from utils.io import user_input, print_assistant, print_system


@chain_watch(prompt=t.chat.PROMPT, validator=validate_with_user_feedback)
def chat():
    conversation = []

    while True:
        with ThreadPoolExecutor() as executor:
            # In parallel, continue the chat and check if the conversation is diverging.
            f_assistant_action = executor.submit(t.chat.next_action, conversation)
            f_conversation_diverged = executor.submit(
                t.keep_context.conversation_diverges, conversation
            )
            assistant_action = f_assistant_action.result()
            conversation_diverged = f_conversation_diverged.result()

        if conversation_diverged:
            # Finish the loop
            print_system(
                "\nI'm sorry. This conversation is going off topic. Please try again. Thanks!"
            )
            break

        conversation.append(
            {
                "role": "assistant",
                "action": assistant_action["action"],
                "message": assistant_action["message"],
            }
        )

        if assistant_action["action"] == "CHAT":
            # Continue chatting with the user
            print_assistant(assistant_action["message"])

            user_message = user_input()
            conversation.append({"role": "client", "message": user_message})
        elif assistant_action["action"] == "SEARCH":
            # Search for flights
            itinerary = assistant_action["message"]
            print_system(f"Searching for: {itinerary}...")

            flights_request, flights = a.flights_searcher.search(itinerary)

            if flights:
                print_system("Found flights. Processing...")
                flights_summary = t.flights_summary.summarize(flights)
            else:
                flights_summary = []

            conversation.append(
                {
                    "role": "system",
                    "message": f"You used this request: {flights_request} and you found these flights: {flights_summary}",
                }
            )
        else:
            print_system(assistant_action["message"])
            break
