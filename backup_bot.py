import json
import os
import requests
import shutil

import praw

from slack_python_logging import slack_logger


class BackupBot:
    "Bot for saving the state of the sub"

    def __init__(self, reddit, subreddit):
        self.reddit = reddit
        self.subreddit = reddit.subreddit(subreddit)
        self.logger = slack_logger.initialize(
            app_name = 'backup_bot',
            stream_loglevel = 'INFO',
            slack_loglevel = 'CRITICAL',
        )
        self.logger.info('Backup bot is online')

    def get_bans(self):
        self.logger.debug('Getting bans')
        return [user.name for user in self.subreddit.banned(limit=None)]

    def get_flairs(self):
        self.logger.debug('Getting flairs')
        flairs = []
        for flair in self.subreddit.flair(limit=None):
            user = flair['user'].name
            flair_css_class = flair['flair_css_class']
            flair_text = flair['flair_text']
            flairs.append({
                'user': user,
                'flair_css_class': flair_css_class,
                'flair_text': flair_text
            })
        return flairs

    def get_wiki(self):
        self.logger.debug('Getting wiki')
        wiki = []
        for page in self.subreddit.wiki:
            wiki.append({page.name: page.content_md})
        return wiki

    def get_contributors(self):
        self.logger.debug('Getting contributors')
        return [user.name for user in self.subreddit.contributor(limit=None)]

    def save_stylesheet_images(self):
        self.logger.debug('Saving stylesheet images')
        try:
            os.mkdir('backup/images', mode=0o773)
        except FileExistsError:
            pass
        for image in self.subreddit.stylesheet().images:
            filename = os.path.join('backup/images', image['link'][6:-3])
            response = requests.get(image['url'], stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
            else:
                self.logger.error('Unable to download stylesheet image')

    def run(self):
        self.logger.info('Beginning backup')
        if self.reddit.user.me(self) not in self.subreddit.moderator():
            self.logger.critical('Not a mod! Cancelling backup.')
            return
        bans = self.get_bans()
        flairs = self.get_flairs()
        wiki = self.get_wiki()
        contributors = self.get_contributors()
        backup = [bans, flairs, wiki, contributors]
        try:
            os.mkdir('backup', mode=0o773)
        except FileExistsError:
            pass
        with open('backup/complete.json', 'w') as f:
            json.dump(backup, f)
        self.save_stylesheet_images()
        self.logger.info('Backup complete')

