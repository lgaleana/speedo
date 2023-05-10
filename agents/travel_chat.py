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

        # Display chat response
        assistant_message = assistant_action["message"]
        conversation.append({"role": "assistant", "content": assistant_message})
        print_assistant(assistant_message)

        if assistant_action["action"] != "SEARCH_THE_INTERNET":
            # Continue chatting with the user
            user_message = user_input()
            conversation.append({"role": "user", "content": user_message})
        else:
            # Search for flights
            print_system("\n[Searching...]\n")
            _, flights = a.flights_searcher.search(conversation)

            if flights:
                print_system("\n[Found flights. Processing...]")
                flights_summary = t.flights_summary.summarize(flights)

                for json, flight in zip(flights, flights_summary):
                    print_assistant(f"\n{flight}\nBooking: {json['deep_link']}")
            else:
                print_assistant("Sorry. I was unable to find any flights.")

            break
