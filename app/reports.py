# [
#     {
#         "role": "user",
#         "content": "start"
#     },
#     {
#         "role": "assistant",
#         "content": "Hello there! I'm an AI assistant and I'm here to help you with anything you need. Let's get started! What can I help you with today?"
#     },
#     {
#         "role": "user",
#         "content": "Whats is the quantile?"
#     },
#     ...
# ]

import os
from typing import List, Tuple

from config.paths import REPORTS_PATH


def generate_report(users: dict) -> Tuple[List[str], int]:
    """
    Generate a report from the user's conversation history.
    Report - is a HTML file with the conversation formatted as a chat.

    Args:
        user: A dictionary containing user data.

    Returns:
        The path to the report.
    """

    edited_files, bytes_written = [], 0

    for user in users:
        conversation = user.get('conversation')

        if not conversation:
            continue

        report_path = REPORTS_PATH + f"{user.get('id')}.html"

        if not os.path.exists(REPORTS_PATH):
            os.makedirs(REPORTS_PATH)

        with open(report_path, 'w') as report:
            report.write('placeholder')

        edited_files.append(report_path)
        bytes_written += os.path.getsize(report_path)

    return edited_files, bytes_written