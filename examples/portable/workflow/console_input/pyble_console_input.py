# SPDX-License-Identifier: MIT
"""Type one short answer into the PyBLE Console.

Purpose:
    Ask one question, read one answer, and then finish.
Prerequisites:
    PyBLE board software v0.6.0 and a Console that can send typed input.
Settings:
    There are no source settings to change. When asked, type only ``red`` or
    ``blue``. Never type your name, password, or another private word.
Before you run:
    Soft-reboot the board, open the Console, and tap Run. Wait until you see the
    question before sending your answer.
Wiring:
    You do not need any wires.
Persistent effects:
    This lesson does not save files. Your typed answer appears on screen and may
    stay briefly in the Python program's input history.
Expected:
    Your short answer appears once. The Console says whether it knows the color
    without printing your answer a second time.
Try this:
    Enter ``red``. Soft-reboot, run again, and enter ``blue`` after the question.
Stop and cleanup:
    If the program is still waiting after two minutes, press Stop. There is
    nothing to switch off or close.
Validation:
    Run and Stop must still be checked on all five board types before release.

Technical note:
    ``input()`` has no timer and echoes before this source can check the answer.
    ASCII means basic keyboard characters, such as English letters. Four of
    these characters keep all Console writes inside the Pico's first-send
    limit. A soft reboot clears old input that may still be waiting.
"""


# ANSWERS AND SAFETY LIMIT - leave these values unchanged.
ALLOWED_CHOICES = ("red", "blue")
MAX_RESPONSE_CHARS = 4


def is_short_printable_text(response):
    """Say whether the answer is short printable ASCII text."""
    return len(response) <= MAX_RESPONSE_CHARS and not any(
        ord(character) < 32 or ord(character) > 126 for character in response
    )


def response_message(response):
    """Describe recognition without repeating the user's input value."""
    is_known = response.strip().lower() in ALLOWED_CHOICES
    if is_short_printable_text(response) and is_known:
        return "Recognized one of the two colors."
    return "Response received, but it was not a listed color."


def main():
    """Warn, prompt once, and report without repeating the response."""
    print(
        "Type only red or blue. Do not type your name, password, or a secret. "
        "What you type appears on screen."
    )
    response = input("Type red or blue: ")
    print(response_message(response))


if __name__ == "__main__":
    main()
