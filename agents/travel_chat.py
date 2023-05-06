import agents as a
import tasks as t
from llm_watch.lib import chain_watch, validate_with_user_feedback
from services.flights import get_routes
from utils.io import user_input, print_assistant, print_system


@chain_watch(prompt=t.chat.PROMPT, validator=validate_with_user_feedback)
def chat():
    conversation = []

    while True:
        assistant_action = t.chat.next_action(conversation)

        assistant_message = assistant_action["message"]
        conversation.append({"role": "assistant", "content": assistant_message})
        print_assistant(assistant_message)

        if assistant_action["action"] != "SEARCH_THE_INTERNET":
            user_message = user_input()
            conversation.append({"role": "user", "content": user_message})
        else:
            print_system("\n[Searching...]\n")
            request, flights = a.flights_searcher.search(conversation)
            conversation.append(
                {
                    "role": "system",
                    "content": f"SEARCH REQUEST: {request}",
                }
            )

            print_system("\n[Found flights. Processing...]")
            flights_summary = t.flights_summary.summarize(get_routes(flights))

            # for json, flight in zip(flights, flights_summary):
            #     print_assistant(f"\n{flight}\nURL: {json['deep_link']}")
            # else:
            #     print_assistant("Sorry. I was unable to find any flights.")
            conversation.append(
                {
                    "role": "system",
                    "content": f"SEARCH RESULTS: {flights_summary}",
                }
            )

            print_assistant(t.chat.next_action(conversation)["message"])
            break
