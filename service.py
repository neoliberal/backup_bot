"""turns discussion thread into service"""
import os

import praw

import backup_bot

def main():
    """main function"""
    reddit = praw.Reddit(
        client_id=os.environ["client_id"],
        client_secret=os.environ["client_secret"],
        refresh_token=os.environ["refresh_token"],
        user_agent="linux:backup_bot:v1.0 (by /u/jenbanim)"
    )
    BackupBot = backup_bot.BackupBot(
        reddit,
        "neoliberal"
    )

    BackupBot.run()

if __name__ == "__main__":
    main()
