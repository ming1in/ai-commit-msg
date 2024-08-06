from __future__ import annotations

import subprocess
from prepare_commit_msg_hooks.openai_service import OpenAiService
from typing import Sequence

def execute_cli_command(cmd_string_list, cwd=None):
    try:
        result = subprocess.run(
            cmd_string_list,
            cwd=cwd,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60  # timeout in 1m/60s
        )
        return result
    except subprocess.CalledProcessError as e:
        cmd_string = " ".join(cmd_string_list)
        error_msg = f"🚨 Total failure to call: {cmd_string}\n{e.stderr}"
        raise Exception(error_msg)

def get_staged_diff():
    script_directory =  execute_cli_command(['git', 'rev-parse', '--git-dir']).stdout.rstrip()


    # git diff --cached is used to get the staged changes to give to the AI to generate commit message
    return execute_cli_command(['git', 'diff', '--staged'], script_directory)

def generate_commit_message():
    staged_diff = get_staged_diff()

    COMMIT_MSG_SYSTEM_MESSAGE = '''
You will be provided with a set of code changes in diff format.
Your task is to read each file and explain every major change in a concise way.

Be sure to include details of major changes

You don't need to add any punctuation or capitalization.

Instead of and, use a comma to save characters.
Only respond with a short sentence no longer than 50 characters that I can use for my commit message
    '''

    ai_gen_commit_msg = OpenAiService().chat_with_openai([
        {"role": "system", "content": COMMIT_MSG_SYSTEM_MESSAGE},
        {"role": "user", "content": staged_diff.stdout},
    ])

    return ai_gen_commit_msg.strip()

def main(argv: Sequence[str] | None = None) -> str:
    commit_message = generate_commit_message()

    print("✨AI: " + commit_message)

    script_directory =  execute_cli_command(['git', 'rev-parse', '--git-dir']).stdout.rstrip()
    print("script_directory: " + script_directory)

    # open COMMIT_EDITMSG file to add the generated commit message



    with open(script_directory + '/COMMIT_EDITMSG', 'w') as file:
        file.write(commit_message)



    return 0

if __name__ == '__main__':
    raise SystemExit(main())
