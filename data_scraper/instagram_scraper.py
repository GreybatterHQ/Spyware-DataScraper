import __init__
import pandas as pd
import json
from utils.http_utils import request_handler
from utils.excel_utils import save_dataFrame_to_excel

class InstagramScraper:
    header = {}
    file_name = 'instagram_output.xlsx'
    output_directory = 'output'

    def __init__(self, url, config_path):
        self.url = url
        self.init_api_auth(config_path)
        self.hashtag_df = pd.DataFrame()
        self.posts_df = pd.DataFrame()
        self.users_df = pd.DataFrame()

    def init_api_auth(self, config_path):
        with open(config_path,"r") as config_file:
            config = json.load(config_file)
        self.header = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Basic "+ config["social_media_auth_token"]
        }

    def scrape_hashtag_data(self, hashtag):
        payload = {
            "target": "instagram_graphql_hashtags",
            "query": hashtag,
        }
        try:
            response_json = request_handler(self.url, 'POST', payload, self.header)
        except Exception as e:
            print(f'An error occurred while fetching hashtag data {e}')
            return
        hashtag_info = response_json['results'][0]['content']['data']['hashtag']
        hashtag_name = hashtag_info['name']
        posts = hashtag_info['edge_hashtag_to_media']['edges']

        # Creating lists using list comprehension
        post_details = [{
            'id': post['node']['id'],
            'text': post['node']['edge_media_to_caption']['edges'][0]['node']['text'],
            'shortcode': post['node']['shortcode'],
            'timestamp': post['node']['taken_at_timestamp'],
            'image_url': post['node']['display_url'],
            'is_video': post['node']['is_video'],
            'dimension': f"{post['node']['dimensions']['width']} x {post['node']['dimensions']['height']}",
            'hashtag': hashtag_name,
            'user': post['node']['owner']['id']
        } for post in posts]

        users = [post['node']['owner']['id'] for post in posts]
        print('users list:', users)
        self.posts_df = self.posts_df.append(pd.DataFrame(post_details))
        users

    def scrape_data(self):
        print('initialized instagram scraper')
        users_ids = self.scrape_hashtag_data('pizza')
        save_dataFrame_to_excel(self.file_name, 'posts', self.posts_df, self.output_directory)