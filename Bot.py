import csv
import requests
import traceback
import json
import datetime
#from fpdf import FPDF
from bs4 import BeautifulSoup
from time import sleep
import re
import random
from enum import Enum
from selenium import webdriver
from HTMLConstructor import*
from Constants import*

class Strategy(Enum):
    NORMAL = 1
    LAST = 2
    RANDOM = 3


class Bot:
    def __init__(self):
        self.session = requests.Session()
        self.username = None    #needed to save data and for 'log_in' and 'safe_log_in'
        self.password = None    #needed for log_in' not for 'safe_log_in'
        self.id = None
        self.authenticated = False
        self.stop_bool = False
        self.ready = True

    def log_in(self):
        self.session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
        req = self.session.get(BASE_URL)
        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})
        login_data = {'username': self.username, 'password': self.password}
        login = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        login_text = json.loads(login.text)
        if login_text.get('authenticated') and login.status_code == 200:
            print("logged in")
            self.authenticated = True
            self.session.headers.update({'user-agent': CHROME_WIN_UA})
            self.id = self.session.cookies['ds_user_id']
        else:
            print("not logged in")

    # if not using GUI consider using 'new_log_in=True' if you are not logged in
    def safe_log_in(self,data_path,webdriver_path,headless=False,new_log_in=False):
        my_options = webdriver.ChromeOptions()
        my_options.add_argument("--user-data-dir="+data_path)
        if headless:
            my_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=webdriver_path,options=my_options)
        driver.get("https://instagram.com")
        if new_log_in:
            sleep(30)
        sleep(3)
        for cookie in driver.get_cookies():
            c = {cookie['name']: cookie['value']}
            self.session.cookies.update(c)
        self.session.headers.update({'X-CSRFToken': self.session.cookies['csrftoken']})
        try:
            self.id = self.session.cookies['ds_user_id']
            print("logged in")
            self.authenticated = True
            self.session.headers.update({'user-agent': CHROME_WIN_UA})
            driver.close()
        except:
            print("please log in and close Chrome and press the key again :)")

    def follow(self, user_id: str) -> int:
        r = self.session.post('https://www.instagram.com/web/friendships/{0}/follow/'.format(user_id))
        return r.status_code

    def unfollow(self, user_id: str) -> int:
        r = self.session.post('https://www.instagram.com/web/friendships/{0}/unfollow/'.format(user_id))
        return r.status_code

    def like(self, post_id: str) -> int:
        r = self.session.post('https://www.instagram.com/web/likes/{0}/like/'.format(post_id))
        return r.status_code

    # returns '0' if stopped
    def get_user_id(self, username: str) -> str:
        while True:
            if self.stop_bool:
                return '0'
            req = self.session.get('https://www.instagram.com/{0}/'.format(username))
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0,600):
                    if self.stop_bool:
                        return '0'
                    sleep(1)
        doc = BeautifulSoup(req.text, "html.parser")
        script_tag = doc.find('script', text=re.compile('window\._sharedData'))
        shared_data = script_tag.string.partition('=')[-1].strip(' ;')
        response = json.loads(shared_data)
        return response.get('entry_data').get('ProfilePage')[0].get('graphql').get('user').get("id")

    def get_profile_pic_url(self, username: str) -> str:
        req = requests.get('https://www.instagram.com/{0}/'.format(username),
                           headers={'user-agent': CHROME_WIN_UA})
        doc = BeautifulSoup(req.text, "html.parser")
        script_tag = doc.find('script', text=re.compile('window\._sharedData'))
        shared_data = script_tag.string.partition('=')[-1].strip(' ;')
        response = json.loads(shared_data)
        user = response.get('entry_data').get('ProfilePage')[0].get('graphql').get('user')
        return user.get('profile_pic_url')

    # returns [(user_id, username)]
    def get_followers(self, user_id: str, debug=False) -> list:
        followers = []
        params = {
            'query_hash': FOLLOWERS_QUERY_HASH,
            'variables': '{"id":"' + user_id + '","include_reel":true,"fetch_mutual":true,"first":500}'
        }
        while True:
            if self.stop_bool:
                return followers
            req = self.session.get("https://www.instagram.com/graphql/query/", params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0,600):
                    if self.stop_bool:
                        return followers
                    sleep(1)
        json_content = json.loads(req.text)
        has_next_page = False
        has_next_page = json_content.get("data").get("user").get(
            "edge_followed_by").get("page_info").get("has_next_page")
        after = ""
        if has_next_page:
            after = json_content.get("data").get("user").get("edge_followed_by").get("page_info").get("end_cursor")
            if debug:
                print(after)

        followers_json = json_content.get("data").get("user").get("edge_followed_by").get("edges")
        for follower in followers_json:
            if self.stop_bool:
                 
                #print("stopped")
                return followers
            followers.append((follower.get("node").get("id"), follower.get("node").get("username")))
        while has_next_page:
            if self.stop_bool:
                 
                #print("stopped")
                return followers
            params = {
                'query_hash': FOLLOWERS_QUERY_HASH,
                'variables': '{"id":"' + user_id
                             + '","include_reel":false,"fetch_mutual":false,"first":500, "after":"' + str(after) + '"}'
            }
            while True:
                if self.stop_bool:
                    return followers
                req = self.session.get("https://www.instagram.com/graphql/query/", params=params)
                if req.status_code == 200:
                    break
                elif req.status_code == 429:
                    print("too many requests\nsleeping..")
                    for i in range(0, 600):
                        if self.stop_bool:
                            return followers
                        sleep(1)
            json_content = json.loads(req.text)
            has_next_page = json_content.get("data").get("user").get(
                "edge_followed_by").get("page_info").get("has_next_page")
            if has_next_page:
                after = json_content.get("data").get("user").get("edge_followed_by").get("page_info").get("end_cursor")
                if debug:
                    print(after)

            followers_json = json_content.get("data").get("user").get("edge_followed_by").get("edges")
            for follower in followers_json:
                if self.stop_bool:
                     
                    #print("stopped")
                    return followers
                followers.append((follower.get("node").get("id"), follower.get("node").get("username")))
        return followers

    # returns [(user_id, username)]
    def get_followees(self, user_id: str, debug=False) -> list:
        followees = []
        params = {
            'query_hash': FOLLOWEES_QUERY_HASH,
            'variables': '{"id":"' + user_id + '","include_reel":true,"fetch_mutual":true,"first":500}'
        }
        while True:
            if self.stop_bool:
                return followees
            req = self.session.get("https://www.instagram.com/graphql/query/", params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return followees
                    sleep(1)
        json_content = json.loads(req.text)
        has_next_page = False
        has_next_page = json_content.get("data").get("user").get(
            "edge_follow").get("page_info").get("has_next_page")
        after = ""
        if has_next_page:
            after = json_content.get("data").get("user").get("edge_follow").get("page_info").get("end_cursor")
            if debug:
                print(after)
        followees_json = json_content.get("data").get("user").get("edge_follow").get("edges")
        for followee in followees_json:
            if self.stop_bool:
                 
                #print("stopped")
                return followees
            followees.append((followee.get("node").get("id"), followee.get("node").get("username")))
        while has_next_page:
            if self.stop_bool:
                 
                #print("stopped")
                return followees
            params = {
                'query_hash': FOLLOWEES_QUERY_HASH,
                'variables': '{"id":"' + user_id
                             + '","include_reel":false,"fetch_mutual":false,"first":500, "after":"' + str(after) + '"}'
            }
            while True:
                if self.stop_bool:
                    return followees
                req = self.session.get("https://www.instagram.com/graphql/query/", params=params)
                if req.status_code == 200:
                    break
                elif req.status_code == 429:
                    print("too many requests\nsleeping..")
                    for i in range(0, 600):
                        if self.stop_bool:
                            return followees
                        sleep(1)
            json_content = json.loads(req.text)
            has_next_page = json_content.get("data").get("user").get(
                "edge_follow").get("page_info").get("has_next_page")
            if has_next_page:
                after = json_content.get("data").get("user").get("edge_follow").get("page_info").get("end_cursor")
                if debug:
                    print(after)

            followees_json = json_content.get("data").get("user").get("edge_follow").get("edges")
            for followee in followees_json:
                if self.stop_bool:
                     
                    #print("stopped")
                    return followees
                followees.append((followee.get("node").get("id"), followee.get("node").get("username")))
        return followees

    def tags(self, log_file: str, tags: list,maximum=500, difference=100, how_many_tags=3, how_much_per_tag=25,
             check_likers=False, likers_per_post=5, how_many_likes_per_user=3, follow_if_private=False, debug=False):
        if not self.authenticated:
            print("can not do tags if user is not logged in :(")
            return
        errors = 0
        for i in range(0, how_many_tags):
            if self.stop_bool:
                 
                #print("stopped")
                return
            try:
                self.session.headers.update({'X-CSRFToken': self.session.cookies['csrftoken']})
            except:
                pass
            posts = []
            tag = tags[random.randint(0, len(tags) - 1)]
            print("---------------------" + tag + "-----------------------")
            params = {
                '__a': '1'
            }
            while True:
                if self.stop_bool:
                    return
                req = self.session.get('https://www.instagram.com/explore/tags/{0}/'.format(tag), params=params)
                if req.status_code == 501:
                    print("Hashtag page is not working :(")
                    return
                elif req.status_code == 200:
                    break
                elif req.status_code == 429:
                    print("too many requests\nsleeping..")
                    for i in range(0, 600):
                        if self.stop_bool:
                            return
            # get information from the tag
            response = json.loads(req.text)
            posts_from_tag = response.get('graphql').get('hashtag').get('edge_hashtag_to_media').get('edges')
            for post in posts_from_tag:
                if self.stop_bool:
                     
                    #print("stopped")
                    return
                posts.append((post.get('node').get('shortcode'),  # post_link
                              post.get('node').get('owner').get('id')  # user_id
                              # ,post.get('node').get('id'))#post_id
                              ))
            for i in range(0, how_much_per_tag):
                if self.stop_bool:
                     
                    #print("stopped")
                    return
                try:
                    sleep_time = random.randint(20,45)
                    for i in range(0, sleep_time):
                        if self.stop_bool:
                             
                            #print("stopped")
                            return
                        sleep(1)
                    random_index = random.randint(0, len(posts) - 1)
                    post_link = posts[random_index][0]
                    user_id = posts[random_index][1]

                    # get username from the post
                    print("link: " 'https://www.instagram.com/p/{0}/'.format(post_link))

                    variables = '{"shortcode":"' + post_link + '","include_reel":true,"include_logged_out":false}'
                    params = {
                        'query_hash': POSTS_QUERY_HASH,
                        'variables': variables
                    }
                    while True:
                        if self.stop_bool:
                            return
                        req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
                        if req.status_code == 501:
                            print("Hashtag page is not working :(")
                            return
                        elif req.status_code == 200:
                            break
                        elif req.status_code == 429:
                            print("too many requests\nsleeping..")
                            for i in range(0, 600):
                                if self.stop_bool:
                                    return
                    response = json.loads(req.text)
                    username = response.get('data').get('shortcode_media').get('owner').get('reel').get('owner').get(
                        'username')

                    sleep_time = random.randint(10, 20)
                    for i in range(0, sleep_time):
                        if self.stop_bool:
                             
                            #print("stopped")
                            return
                        sleep(1)
                    result = self.check_user(username, user_id, maximum, difference, log_file, follow_if_private)
                    code = result[2]
                    if code == 429:
                         
                        return
                    if check_likers:
                        print("checking likes! ;)")
                        likers = self.get_likers(post_link, how_much=likers_per_post * 2, debug=debug)
                        for i in range(0, likers_per_post):
                            if self.stop_bool:
                                #print("stopped")
                                return
                            sleep_time = random.randint(10, 20)
                            for i in range(0, sleep_time):
                                if self.stop_bool:
                                     
                                    #print("stopped")
                                    return
                                sleep(1)
                            random_index = random.randint(0, len(likers) - 1)
                            user_id = likers[random_index][0]
                            username = likers[random_index][1]
                            user_result = self.check_user(username, user_id, maximum, difference, log_file,
                                                          follow_if_private)
                            followed = user_result[0]
                            is_private = user_result[1]
                            code = user_result[2]
                            if code == 429:
                                 
                                return
                            if followed and not is_private:
                                    print("liking users posts")
                                    code = self.like_posts(user_id, how_many_likes_per_user, debug=debug)
                                    if code == 429:
                                         
                                        return
                except:
                    if debug:
                        traceback.print_exc()
                    errors = errors + 1
                    if errors == 3:
                        print("3 errors occurred in current session :(\nbetter stop before getting banned ;)")
                        return
                    print(
                        "something went wrong :(\nPost or user might have been removed or is not public anymore\ntrying "
                        "another post :)")

    def explore(self,log_file: str, maximum=500, difference=100, how_many_pages=3, how_many_posts_per_explore=20
                , likers_per_post=5, how_many_likes_per_user=3, follow_if_private=False, debug=False, display_images=False):
        if not self.authenticated:
            print("can not explore if user is not logged in :(")
            return
        errors = 0
        posts = []
        for i in range(0, how_many_pages):
            while True:
                if self.stop_bool:
                    return
                req = self.session.get(
                    'https://www.instagram.com/explore/grid/?is_prefetch=false&omit_cover_media=false&module=explore_popular&use_sectional_payload=true&cluster_id=explore_all%3A0&include_fixed_destinations=true&max_id=' + str(
                        i))
                if req.status_code == 200:
                    break
                elif req.status_code == 501:
                    print("Explore page is not working :(")
                    return
                elif req.status_code == 429:
                    print("too many requests\nsleeping..")
                    for i in range(0, 600):
                        if self.stop_bool:
                            return
            response = json.loads(req.text)
            medias = response.get("sectional_items")[1].get('layout_content').get('medias')
            for media in medias:
                if self.stop_bool:
                     
                    #print("stopped")
                    return
                post_id = media.get('media').get('pk')
                post_link = media.get('media').get('code')
                user_id = media.get('media').get('user').get('pk')
                username = media.get('media').get('user').get('username')
                posts.append((post_link, post_id, user_id, username))
        for i in range(0, how_many_posts_per_explore):
            if self.stop_bool:
                 
                #print("stopped")
                return
            try:
                sleep_time = random.randint(20, 45)
                for i in range(0, sleep_time):
                    if self.stop_bool:
                         
                        #print("stopped")
                        return
                    sleep(1)
                random_index = random.randint(0, len(posts) - 1)
                post_link = posts[random_index][0]
                post_id = posts[random_index][1]
                user_id = posts[random_index][2]
                username = posts[random_index][3]

                print("link: " 'https://www.instagram.com/p/{0}/'.format(post_link))
                result = self.check_user(username, user_id, maximum, difference, log_file,follow_if_private)
                code = result[2]
                if code == 429:
                     
                    return
                print("checking likes! ;)")
                likers = self.get_likers(post_link, how_much=likers_per_post*2,debug=debug)
                for i in range(0, likers_per_post):
                    if self.stop_bool:
                         
                        #print("stopped")
                        return
                    sleep_time = random.randint(10, 20)
                    for i in range(0, sleep_time):
                        if self.stop_bool:
                             
                            #print("stopped")
                            return
                        sleep(1)
                    random_index = random.randint(0, len(likers) - 1)
                    user_id = likers[random_index][0]
                    username = likers[random_index][1]
                    user_result = self.check_user(username, user_id, maximum, difference, log_file,follow_if_private)
                    followed = user_result[0]
                    is_private = user_result[1]
                    code = user_result[2]
                    if code == 429:
                         
                        return
                    if followed and not is_private:
                        print("liking users posts")
                        code = self.like_posts(user_id,how_many_likes_per_user,debug=debug, display_images=display_images)
                        if code == 429:
                             
                            return

            except:
                if debug:
                    traceback.print_exc()
                errors = errors + 1
                if errors == 3:
                    print("3 errors occurred in current session :(\nbetter stop before getting banned ;)")
                    return
                print(
                    "something went wrong :(\nPost or user might have been removed or is not public anymore\ntrying "
                    "another post :)")

    #returns (followed: bool, is_private: bool, status_code: int)
    def check_user(self, username: str, user_id: str, maximum: int, difference: int, log_file: str, follow_if_private=False) -> tuple:
        followed = False
        is_private = False
        print("user: ", 'https://www.instagram.com/{0}/'.format(username))
        req = requests.get('https://www.instagram.com/{0}/'.format(username),headers={'user-agent': CHROME_WIN_UA})
        code = req.status_code
        if req.status_code == 429:
            print("too much for this session\nlets try again later before getting banned ;)")
            return (followed, is_private, code)

        doc = BeautifulSoup(req.text, "html.parser")
        script_tag = doc.find('script', text=re.compile('window\._sharedData'))
        shared_data = script_tag.string.partition('=')[-1].strip(' ;')
        response = json.loads(shared_data)
        user = response.get('entry_data').get('ProfilePage')[0].get('graphql').get('user')
        is_private = user.get('is_private')
        if is_private:
            print("user is private")
        followers = int(user.get('edge_followed_by').get('count'))
        print("followers: ", followers)
        followees = int(user.get('edge_follow').get('count'))
        print("followees: ", followees)
        sleep_time = random.randint(10, 20)
        for i in range(0, sleep_time):
            if self.stop_bool:
                 
                #print("stopped")
                return (followed, is_private,0)
            sleep(1)
        if is_private and not follow_if_private:
            print("no follow!")
            print("----------------------------------------")
            return (followed, is_private,0)
        if followers <= maximum or (followers - followees < difference):
            code = self.follow(user_id)
            print("follow: ", code)
            if code == 200:
                followed = True
                with open(log_file, "a", encoding="utf-8") as file:
                    file.write(str(username) + " | followers: " + str(followers) + " | followees: " + str(
                        followees) + "\n")
                file.close()
            elif code == 429:
                print("too much for this session\nlets try again later before getting banned ;)")
                return (followed, is_private, code)
        else:
            print("no follow!")
        print("----------------------------------------")
        return (followed, is_private, code)

    # returns [(post_link: str, post_id: str, is_viedo: bool, url: str )] #how_much=0 -> all
    def get_posts(self, user_id: str, debug=False, how_much=0,is_private=True) -> list:
        posts = []
        variables = '{"id":"' + user_id + '","first":500}'
        params = {
            'query_hash': USER_POSTS_QUERY_HASH,
            'variables': variables
        }
        while True:
            if self.stop_bool:
                return posts
            if is_private:
                req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
            else:
                req = requests.get('https://www.instagram.com/graphql/query/', params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return posts
                    sleep(1)
        response = json.loads(req.text)
        count = int(response.get('data').get('user').get('edge_owner_to_timeline_media').get('count'))
        if count == 0:
            print("user has no posts :(")
            return posts
        has_next_page = False
        has_next_page = response.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info').get(
            'has_next_page')
        if has_next_page:
            after = response.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info').get(
                'end_cursor')
            if debug:
                print(after)
        medias = response.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        for media in medias:
            if self.stop_bool:
                 
                #print("stopped")
                return posts
            post_id = media.get('node').get('id')
            post_link = media.get('node').get('shortcode')
            is_video = media.get('node').get('is_video')
            if is_video:
                url = media.get('node').get('video_url')
            else:
                url = media.get('node').get('display_url')
            posts.append((post_link, post_id,is_video,url))
            if not how_much == 0:
                if len(posts) == how_much:
                    return posts
        while has_next_page:
            variables = '{"id":"' + user_id + '","first":500, "after": "' + after + '"}'
            params = {
                'query_hash': USER_POSTS_QUERY_HASH,
                'variables': variables
            }
            while True:
                if self.stop_bool:
                    return posts
                if is_private:
                    req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
                else:
                    req = requests.get('https://www.instagram.com/graphql/query/', params=params)
                if req.status_code == 200:
                    break
                elif req.status_code == 429:
                    print("too many requests\nsleeping..")
                    for i in range(0, 600):
                        if self.stop_bool:
                            return posts
                        sleep(1)
            response = json.loads(req.text)
            has_next_page = response.get('data').get('user').get('edge_owner_to_timeline_media').get(
                'page_info').get('has_next_page')
            if has_next_page:
                after = response.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info').get(
                    'end_cursor')
                if debug:
                    print(after)
            medias = response.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
            for media in medias:
                if self.stop_bool:
                     
                    #print("stopped")
                    return posts
                post_id = media.get('node').get('id')
                post_link = media.get('node').get('shortcode')
                is_video = media.get('node').get('is_video')
                if is_video:
                    url = media.get('node').get('video_url')
                else:
                    url = media.get('node').get('display_url')
                posts.append((post_link, post_id,is_video,url))
                if not how_much == 0:
                    if len(posts) == how_much:
                        return posts
        return posts

    # returns [(is_viedo: bool, url: str)] #how_much=0 -> all
    def get_highlights(self, user_id: str, how_much=0) -> list:
        highlights = []
        variables = '{"user_id":"'+user_id+'","include_chaining":true,"include_reel":true,"include_suggested_users":false,"include_logged_out_extras":false,"include_highlight_reels":true,"include_live_status":true}'
        params = {
            'query_hash': USER_HIGHTLIGHTS_QUERY_HASH,
            'variables': variables
        }
        while True:
            if self.stop_bool:
                return highlights
            req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return highlights
                    sleep(1)
        response = json.loads(req.text)
        reels = response.get('data').get('user').get('edge_highlight_reels').get('edges')
        for reel in reels:
            if self.stop_bool:
                 
                #print("stopped")
                return highlights
            id = reel.get('node').get('id')
            variables = '{"reel_ids":[],"tag_names":[],"location_ids":[],"highlight_reel_ids":["' + id + '"],"precomposed_overlay":false,"show_story_viewer_list":true,"story_viewer_fetch_count":50,"story_viewer_cursor":"","stories_video_dash_manifest":false}'
            params = {
                'query_hash': USER_HIGHTLIGHTS_REELS_QUERY_HASH,
                'variables': variables
            }
            while True:
                if self.stop_bool:
                    return highlights
                req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
                if req.status_code == 200:
                    break
                elif req.status_code == 429:
                    print("too many requests\nsleeping..")
                    for i in range(0, 600):
                        if self.stop_bool:
                            return highlights
                        sleep(1)
            reels_response = json.loads(req.text)
            items = reels_response.get('data').get('reels_media')[0].get('items')
            for item in items:
                if self.stop_bool:
                     
                    #print("stopped")
                    return highlights
                is_video = item.get('is_video')
                if not is_video:
                    display_url = item.get('display_url')
                    highlights.append((is_video,display_url))
                    if not how_much == 0:
                        if len(highlights) == how_much:
                            return highlights
                else:
                    video_resources = item.get('video_resources')
                    url = video_resources[0].get('src')
                    highlights.append((is_video,url))
                    if not how_much == 0:
                        if len(highlights) == how_much:
                            return highlights
        return highlights

    # returns [(is_viedo: bool, url: str)] #how_much=0 -> all
    def get_stories(self, user_id: str, how_much=0) -> list:
        stories = []
        variables = '{"reel_ids":["'+user_id+'"],"tag_names":[],"location_ids":[],"highlight_reel_ids":[],"precomposed_overlay":false,"show_story_viewer_list":true,"story_viewer_fetch_count":50,"story_viewer_cursor":"","stories_video_dash_manifest":false}'
        params = {
            'query_hash': USER_STORIES_QUERY_HASH,
            'variables': variables
        }
        while True:
            if self.stop_bool:
                return stories
            req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return stories
                    sleep(1)
        response = json.loads(req.text)
        reels = response.get('data').get('reels_media')
        for reel in reels:
            items = reel.get('items')
            for item in items:
                is_video = item.get('is_video')
                if not is_video:
                    display_url = item.get('display_url')
                    stories.append((is_video,display_url))
                    if not how_much == 0:
                        if len(stories) == how_much:
                            return stories
                else:
                    video_resources = item.get('video_resources')
                    url = video_resources[0].get('src')
                    stories.append((is_video,url))
                    if not how_much == 0:
                        if len(stories) == how_much:
                            return stories
        return stories

    # returns [(username, stories: [(is_viedo: bool, url: str)])] #how_much=0 -> all, #how_much_per_user=0 -> all
    def get_todays_stories(self, how_much=0, how_much_per_user=0) -> list:
        result_stories = []
        variables =  '{"only_stories":true,"stories_prefetch":false,"stories_video_dash_manifest":false}'
        params = {
            'query_hash': TODAYS_STORIES_QUERY_HASH,
            'variables': variables
        }
        while True:
            if self.stop_bool:
                return result_stories
            req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return result_stories
                    sleep(1)
        response = json.loads(req.text)
        stories = response.get('data').get('user').get('feed_reels_tray').get('edge_reels_tray_to_reel').get('edges')
        for story in stories:
            username = story.get('node').get('owner').get('username')
            user_id = story.get('node').get('id')
            print("getting user stories")
            user_stories = self.get_stories(user_id,how_much_per_user)
            result_stories.append((username,user_stories))
            if not how_much == 0:
                if len(result_stories) == how_much:
                    return result_stories
        return result_stories

    # returns [(user_id, username, profile_pic_url)] #how_much=0 -> all
    def get_likers(self, post_link: str, debug=False, how_much=0) -> list:
        likers = []
        params = {
            'query_hash': LIKES_QUERY_HASH,
            'variables': '{"shortcode":"' + post_link + '","include_reel":true,"first":500}'
        }
        while True:
            if self.stop_bool:
                return likers
            req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return likers
                    sleep(1)
        response = json.loads(req.text)
        likers_count = response.get('data').get('shortcode_media').get('edge_liked_by').get('count')
        if int(likers_count) > 0:
            has_next_page = False
            has_next_page = response.get('data').get('shortcode_media').get('edge_liked_by').get('page_info').get(
                'has_next_page')
            if has_next_page:
                after = response.get('data').get('shortcode_media').get('edge_liked_by').get('page_info').get(
                    'end_cursor')
                if debug:
                    print(after)
            users = response.get('data').get('shortcode_media').get('edge_liked_by').get('edges')
            for user in users:
                if self.stop_bool:
                    return likers
                user_id = user.get('node').get('id')
                username = user.get('node').get('username')
                profile_pic_url = user.get('node').get("profile_pic_url")
                likers.append((user_id, username,profile_pic_url))
                if not how_much == 0:
                    if len(likers) == how_much:
                        return likers
            while has_next_page:
                params = {
                    'query_hash': LIKES_QUERY_HASH,
                    'variables': '{"shortcode":"' + post_link + '","include_reel":true,"first":500,"after":"' + after + '"}'
                }
                while True:
                    if self.stop_bool:
                        return likers
                    req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
                    if req.status_code == 200:
                        break
                    elif req.status_code == 429:
                        print("too many requests\nsleeping..")
                        for i in range(0, 600):
                            if self.stop_bool:
                                return likers
                            sleep(1)
                response = json.loads(req.text)
                has_next_page = response.get('data').get('shortcode_media').get('edge_liked_by').get('page_info').get(
                    'has_next_page')
                if has_next_page:
                    after = response.get('data').get('shortcode_media').get('edge_liked_by').get('page_info').get(
                        'end_cursor')
                    if debug:
                        print(after)
                users = response.get('data').get('shortcode_media').get('edge_liked_by').get('edges')
                for user in users:
                    if self.stop_bool:
                        return likers
                    user_id = user.get('node').get('id')
                    username = user.get('node').get('username')
                    profile_pic_url = user.get('node').get("profile_pic_url")
                    likers.append((user_id, username, profile_pic_url))
                    if not how_much == 0:
                        if len(likers) == how_much:
                            return likers
        return likers

    def get_likes_count(self, post_link: str) -> int:
        params = {
            'query_hash': LIKES_QUERY_HASH,
            'variables': '{"shortcode":"' + post_link + '","include_reel":true,"first":500}'
        }
        while True:
            if self.stop_bool:
                return 0
            req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return 0
                    sleep(1)
        response = json.loads(req.text)
        likers_count = response.get('data').get('shortcode_media').get('edge_liked_by').get('count')
        return int(likers_count)

    # returns [(username, comment_text, post_link, profile_pic_url)]
    def get_commenters(self, post_link: str, debug=False,is_private=True) -> list:
        commenters = []
        params = {
            'query_hash': COMMENTS_QUERY_HASH,
            'variables': '{"shortcode":"' + post_link + '","first":500}'
        }
        while True:
            if self.stop_bool:
                return commenters
            if is_private:
                req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
            else:
                req = requests.get('https://www.instagram.com/graphql/query/', params=params)
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return commenters
                    sleep(1)
        response = json.loads(req.text)
        has_next_page = False
        has_next_page = response.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get(
            'page_info').get('has_next_page')
        if has_next_page:
            after = response.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get(
                'page_info').get('end_cursor')
            if debug:
                print(after)
        comments = response.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get('edges')
        for comment in comments:
            comment_text = comment.get('node').get('text')
            comment_owner = comment.get('node').get('owner').get('username')
            profile_pic_url = comment.get('node').get('owner').get('profile_pic_url')
            commenters.append((comment_owner, comment_text, 'https://www.instagram.com/p/{0}/'.format(post_link),profile_pic_url))
        while has_next_page:
            params = {
                'query_hash': COMMENTS_QUERY_HASH,
                'variables': '{"shortcode":"' + post_link + '","first":500,"after":"' + after + '"}'
            }
            while True:
                if self.stop_bool:
                    return commenters
                if is_private:
                    req = self.session.get('https://www.instagram.com/graphql/query/', params=params)
                else:
                    req = requests.get('https://www.instagram.com/graphql/query/', params=params)
                if req.status_code == 200:
                    break
                elif req.status_code == 429:
                    print("too many requests\nsleeping..")
                    for i in range(0, 600):
                        if self.stop_bool:
                            return commenters
                        sleep(1)
            response = json.loads(req.text)
            has_next_page = response.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get(
                'page_info').get('has_next_page')
            if has_next_page:
                after = response.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get(
                    'page_info').get('end_cursor')
                if debug:
                    print(after)
            comments = response.get('data').get('shortcode_media').get('edge_media_to_parent_comment').get('edges')
            for comment in comments:
                comment_text = comment.get('node').get('text')
                comment_owner = comment.get('node').get('owner').get('username')
                profile_pic_url = comment.get('node').get('owner').get('profile_pic_url')
                commenters.append((comment_owner, comment_text, 'https://www.instagram.com/p/{0}/'.format(post_link),
                                   profile_pic_url))
        return commenters

    def download_file(self, path: str, url: str, type: str):
        while True:
            if self.stop_bool:
                return
            response = self.session.get(url)
            if response.status_code == 200:
                break
            elif response.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        return
                    sleep(1)
        with open(path + "." + type, "wb") as file:
            file.write(response.content)

    def check_if_allowed(self):
        response = self.session.get("https://raw.githubusercontent.com/JadKHaddad/JadKHaddad/master/SmartFollower.txt")
        list = response.text.split("\n")
        if self.number in list:
            return True
        else:
            return False
        return False

    # helpers

    # how_much=0 -> all
    def download_posts(self, user_id: str, path: str, how_much=0,photos=True,videos=True,debug=False,is_private=True):
        posts = self.get_posts(user_id,debug=debug,how_much=how_much,is_private=is_private)
        index = 1
        for post in posts:
            if self.stop_bool:
                print("download stopped")
                return
            if post[2]:
                if videos:
                    self.download_file(path+str(index), post[3], 'mp4')
            else:
                if photos:
                    self.download_file(path+str(index), post[3], 'jpg')
            index = index + 1

    def download_highlights(self, user_id: str, path: str, how_much=0,photos=True,videos=True,debug=False):
        highlights = self.get_highlights(user_id,how_much=how_much)
        index = 1
        for highlight in highlights:
            if self.stop_bool:
                 
                print("download stopped")
                return
            if highlight[0]:
                if videos:
                    self.download_file(path+str(index), highlight[1], 'mp4')
            else:
                if photos:
                    self.download_file(path+str(index), highlight[1], 'jpg')
            index = index + 1

    def download_stories(self, user_id: str, path: str, how_much=0,photos=True,videos=True,debug=False):
        stories = self.get_stories(user_id,how_much=how_much)
        index = 1
        for story in stories:
            if self.stop_bool:
                print("download stopped")
                return
            if story[0]:
                if videos:
                    self.download_file(path+str(index), story[1], 'mp4')
            else:
                if photos:
                    self.download_file(path+str(index), story[1], 'jpg')
            index = index + 1

    def download_todays_stories(self,path: str, how_much=0,how_much_per_user=0,photos=True,videos=True,debug=False):
        stories = self.get_todays_stories(how_much=how_much,how_much_per_user=how_much_per_user)
        for story in stories:
            download_path = os.path.join(path, story[0])
            path_exists = os.path.exists(os.path.join(path, story[0]))
            if not path_exists:
                os.mkdir(os.path.join(path, story[0]))
            print("downloading..")
            index = 1
            for user_story in story[1]:
                if self.stop_bool:
                    print("download stopped")
                    return
                if user_story[0]:
                    if videos:
                        self.download_file(os.path.join(download_path,str(datetime.datetime.now().timestamp())+"_"+story[0]+str(index)), user_story[1], 'mp4')
                else:
                    if photos:
                        self.download_file(os.path.join(download_path,str(datetime.datetime.now().timestamp())+"_"+story[0]+str(index)), user_story[1], 'jpg')
                index = index + 1

    def display_image(self, url: str, how_long=3):
        pass

    def write_not_followers(self, path: str,debug=False):
        followees = self.get_followees(self.id,debug=debug)
        followers = self.get_followers(self.id,debug=debug)
        if self.stop_bool:
            return
        with open(path, "w", encoding='utf8') as file:
            for x in followees:
                if x not in followers:
                    file.write(x[1] + "\n")

    # returns [username]
    def load_not_followers(self, path: str) -> list:
        list = []
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='-', quotechar='"')
            for row in reader:
                list.append(row[0].strip())
        return list

    def unfollow_all(self, path: str, exceptions: list):
        if not self.authenticated:
            print("can not unfollow if user is not logged in :(")
            return False
        not_followers = self.load_not_followers(path)
        if len(not_followers) == 0:
            return True
        for username in not_followers:
            if self.stop_bool:
                 
                #print("stopped")
                return
            unfollow = True
            for i in range(0, 5):
                if self.stop_bool:
                     
                    #print("stopped")
                    return
                sleep(1)
            if self.stop_bool:
                 
                #print("stopped")
                return
            print("username: ", username)
            if username in exceptions:
                unfollow = False
                print("username in Exceptions")
            if unfollow:
                user_id = self.get_user_id(username)
                print("id: ", user_id)
                while True:
                    code = self.unfollow(user_id)
                    print("code: ", code)
                    if code == 200:
                        break
                    elif code == 429:
                        print("too many requests\nsleeping..")
                        for i in range(0, 600):
                            if self.stop_bool:
                                #print("stopped")
                                return
                            sleep(1)
                    else:
                        print("code: ", code)
                        return
                print("-----------------------")

            if code == 200 or not unfollow:
                with open(path, "w", encoding='utf8') as file:
                    for i in not_followers:
                        if i != username:
                            file.write(i + "\n")
                file.close()
                not_followers = not_followers[1:]
                if len(not_followers) == 0:
                    return

    def unfollow_all_with_chrome(self,data_path,webdriver_path, path: str, exceptions: list, headless=False,new_log_in=False,):
        not_followers = self.load_not_followers(path)
        my_options = webdriver.ChromeOptions()
        my_options.add_argument("--user-data-dir=" + data_path)
        if headless:
            my_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=webdriver_path, options=my_options)
        driver.get("https://instagram.com")
        if new_log_in:
            sleep(30)
        sleep(3)
        for username in not_followers:
            random_int = random.randint(5,10)
            for i in range(0, random_int):
                if self.stop_bool:
                    return
                sleep(1)
            print("username: ", username)
            if username in exceptions:
                unfollow = False
                print("username in Exceptions")
            driver.get("https://instagram.com/"+ username +"/")
            random_int = random.randint(2,5)
            for i in range(0, random_int):
                if self.stop_bool:
                    return
                sleep(1)
            driver.find_element_by_xpath("/html//div[@id='react-root']/section/main[@role='main']/div//section[@class='zwlfE']/div[@class='nZSzR']/div[1]/div/div[2]/div/span/span[1]/button") \
                .click()
            random_int = random.randint(1, 3)
            for i in range(0, random_int):
                if self.stop_bool:
                    return
                sleep(1)
            driver.find_element_by_xpath(
                "/html/body/div[@role='presentation']/div[@role='dialog']//button[.='Nicht mehr folgen']") \
                .click()
            with open(path, "w", encoding='utf8') as file:
                for i in not_followers:
                    if i != username:
                        file.write(i + "\n")
            file.close()
            not_followers = not_followers[1:]
            if len(not_followers) == 0:
                return
    #prints link, code
    #how_much=0 -> all
    #returns
    #   0 if stopped
    #   1 if excuted successfully
    #   429 if too many requests
    # be careful when using LAST or RANDOM. you will have to get all the posts that the user has(not implemented)
    def like_posts(self, user_id: str, how_much=0, strategy=Strategy.NORMAL, sleep_time=5, debug=True, display_images=False) -> int:
        if not self.authenticated:
            print("can not like if user is not logged in :(")
            return 1
        if strategy == Strategy.NORMAL:
            posts = self.get_posts(user_id, debug=debug,how_much=how_much)
            for post in posts:
                if self.stop_bool:
                    #print("stopped")
                    return 0
                for i in range(0, sleep_time):
                    if self.stop_bool:
                        #print("stopped")
                        return 0
                    sleep(1)
                if display_images:
                    if not post[2]:
                        self.display_image(post[3])
                code = self.like(post[1])
                print(('https://www.instagram.com/p/{0}/'.format(post[0])), code)
                if code == 429:
                    return code

            print("----------------------------------------")
            return 1
        return 1

    #used all together (dont use)
    def save_posts(self, user_id: str, path: str):
        posts = self.get_posts(user_id, debug=True)
        with open(path, "w", encoding='utf8') as file:
            for post in posts:
                file.write(post[0] + "\n")
    def analyse_posts_for_likes(self, posts_path: str, likers_path: str):
        posts = []
        with open(posts_path, "r", encoding='utf8') as file:
            for line in file:
                posts.append(line.strip())
        post_number = 1
        for post in posts:
            print("post number: ", post_number)
            likers = self.get_likers(post, debug=True)

            with open(likers_path, "a", encoding='utf8') as file:
                for liker in likers:
                    file.write(liker[1] + "\n")

            with open(posts_path, "w", encoding='utf8') as file:
                for i in posts:
                    if i != post:
                        file.write(i + "\n")
            posts = posts[1:]
            post_number = post_number + 1
    def show_likers(self, likers_path: str):
        people = {}
        with open(likers_path, "r", encoding='utf8') as file:
            for line in file:
                username = line.strip()
                if username in people:
                    people[username] = people[username] + 1
                else:
                    people[username] = 1
        list_view = [(value, key) for key, value in people.items()]
        list_view.sort(reverse=True)
        for likes_username in list_view:
            print(likes_username)
    def anylyse_posts_for_likes_and_show(self,user_id: str, path1: str,path2: str):
        self.save_posts(user_id, path1)
        self.analyse_posts_for_likes(path1, path2)
        self.show_likers(path2)

    def export_messages(self,path: str, target_username: str, target_date: datetime.date, debug=False):
        if self.stop_bool:
            return

        target_pic_url = ""
        target_profile_url = "https://www.instagram.com/"+target_username+"/"
        pic_url = ""
        profile_url = "https://www.instagram.com/"+self.username+"/"

        # writes in file
        # returns True if date is reached, False if not
        def write(item,file,target_username,target_date):
            timestamp = item.get('timestamp')
            date = datetime.datetime.utcfromtimestamp(int(timestamp / 1000000))
            current_date = date.date()
            if current_date < target_date:
                return True
            str_date = date.strftime('%Y-%m-%d %H:%M:%S')
            user_id = item.get('user_id')

            item_type = item.get('item_type')
            if item_type == 'text':
                text = item.get('text')
                if str(user_id) == self.id:
                    file.write(construct_body("right",self.username,pic_url,profile_url,text,str(date)))
                else:
                    file.write(construct_body("left",target_username,target_pic_url,target_profile_url,text,str(date)))

            elif item_type == 'media':
                if str(user_id) == self.id:
                    file.write(construct_body("right",self.username,pic_url,profile_url,"sent a photo/video",str(date)))
                else:
                    file.write(construct_body("left",target_username,target_pic_url,target_profile_url,"sent a photo/video",str(date)))

            elif item_type == 'media_share':
                post_link = item.get('media_share').get('code')
                if str(user_id) == self.id:
                    file.write(
                        construct_body("right", self.username, pic_url, profile_url, '<a href="https://www.instagram.com/p/' + post_link + '/">post</a>', str(date)))

                else:
                    file.write(construct_body("left",target_username,target_pic_url,target_profile_url,'<a href="https://www.instagram.com/p/' + post_link + '/">post</a>',str(date)))

            elif item_type == 'profile':
                username = item.get('profile').get('username')
                if str(user_id) == self.id:
                    file.write(
                        construct_body("right", self.username, pic_url, profile_url,
                                       '<a href = "https://www.instagram.com/' + username + '/">profile</a>', str(date)))
                else:
                    file.write(construct_body("left", target_username, target_pic_url, target_profile_url,
                                              '<a href = "https://www.instagram.com/' + username + '/">profile</a>',
                                              str(date)))
            elif item_type == 'voice_media':
                if str(user_id) == self.id:
                    file.write(construct_body("right",self.username,pic_url,profile_url,"sent a voice note",str(date)))
                else:
                    file.write(construct_body("left",target_username,target_pic_url,target_profile_url,"sent a voice note",str(date)))


            elif item_type == 'story_share':
                if str(user_id) == self.id:
                    file.write(construct_body("right",self.username,pic_url,profile_url,"shared a story",str(date)))
                else:
                    file.write(construct_body("left",target_username,target_pic_url,target_profile_url,"shared a story",str(date)))
            return False

        self.session.headers.update({'user-agent': API})
        while True:
            if self.stop_bool:
                self.session.headers.update({'user-agent': CHROME_WIN_UA})
                return
            req = self.session.get(
                'https://i.instagram.com/api/v1/direct_v2/inbox/?persistentBadging=true&folder=&limit=1000&thread_message_limit=10')
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        self.session.headers.update({'user-agent': CHROME_WIN_UA})
                        return
                    sleep(1)
        response = json.loads(req.text)
        #get the target thread
        thread_id = None
        threads = response.get('inbox').get('threads')
        for thread in threads:
            if self.stop_bool:
                self.session.headers.update({'user-agent': CHROME_WIN_UA})
                return
            this_thread_id = thread.get('thread_id')
            this_username = thread.get('users')[0].get('username')
            if this_username == target_username:
                thread_id = this_thread_id
                break
        if debug:
            print("fetching profile pics")
        target_pic_url = self.get_profile_pic_url(target_username)
        pic_url = self.get_profile_pic_url(self.username)
        if thread_id == None:
            print("user not found")
        else:
            if debug:
                print("thread id:", thread_id)
        while True:
            if self.stop_bool:
                self.session.headers.update({'user-agent': CHROME_WIN_UA})
                return
            req = self.session.get('https://i.instagram.com/api/v1/direct_v2/threads/' + thread_id + '/')
            if req.status_code == 200:
                break
            elif req.status_code == 429:
                print("too many requests\nsleeping..")
                for i in range(0, 600):
                    if self.stop_bool:
                        self.session.headers.update({'user-agent': CHROME_WIN_UA})
                        return
                    sleep(1)
        response = json.loads(req.text)
        file = open(path, "w", encoding="utf-8")
        file.write(get_header(target_username))
        items = response.get('thread').get('items')
        for item in items:
            if self.stop_bool:
                self.session.headers.update({'user-agent': CHROME_WIN_UA})
                file.write(get_footer())
                file.close()
                return
            if write(item,file,target_username,target_date):
                self.session.headers.update({'user-agent': CHROME_WIN_UA})
                file.write(get_footer())
                file.close()
                return

        has_older = response.get('thread').get('has_older')
        if has_older:
            prev_cursor = response.get('thread').get('prev_cursor')
            if debug:
                print("cursor:", prev_cursor)
        while has_older:
            if self.stop_bool:
                self.session.headers.update({'user-agent': CHROME_WIN_UA})
                file.write(get_footer())
                file.close()
                return
            params = {
                'cursor': prev_cursor
            }
            while True:
                if self.stop_bool:
                    self.session.headers.update({'user-agent': CHROME_WIN_UA})
                    file.write(get_footer())
                    file.close()
                    return
                req = self.session.get('https://i.instagram.com/api/v1/direct_v2/threads/' + thread_id + '/',
                                       params=params)
                if req.status_code == 200:
                    break
                elif req.status_code == 429:
                    print("too many requests\nsleeping..")
                    for i in range(0, 600):
                        if self.stop_bool:
                            self.session.headers.update({'user-agent': CHROME_WIN_UA})
                            file.write(get_footer())
                            file.close()
                            return
                        sleep(1)
            response = json.loads(req.text)
            items = response.get('thread').get('items')
            for item in items:
                if self.stop_bool:
                    self.session.headers.update({'user-agent': CHROME_WIN_UA})
                    file.write(get_footer())
                    file.close()
                    return
                if write(item, file, target_username, target_date):
                    self.session.headers.update({'user-agent': CHROME_WIN_UA})
                    file.write(get_footer())
                    file.close()
                    return
            has_older = response.get('thread').get('has_older')
            if has_older:
                prev_cursor = response.get('thread').get('prev_cursor')
                if debug:
                    print("cursor:", prev_cursor)
        self.session.headers.update({'user-agent': CHROME_WIN_UA})
        file.write(get_footer())
        file.close()

    def analyse_posts_for_comments(self, user_id: str,target_username:str,console=True, save_html=False,path=None,is_private=True,debug=False):
        if save_html:
            file = open(path,"w",encoding="utf-8")
            file.write(get_header(target_username))
            pictures = {}
        people = {}
        if debug:
            print("fetching posts..")
        posts = self.get_posts(user_id, debug=debug,is_private=is_private)
        if debug:
            print("analysing posts..")
        for post in posts:
            commenters = self.get_commenters(post[0],debug=debug,is_private=is_private)
            for commenter in commenters:
                username = str(commenter[0]).strip()
                comment = str(commenter[1]).strip()
                post = str(commenter[2]).strip()
                pic_url = str(commenter[3]).strip()
                if save_html:
                    pictures[username] = pic_url
                if username in people:
                    l = people[username]
                    l.append(comment + ": " + post)
                    people[username] = l
                else:
                    l = []
                    l.append(comment + ": " + post)
                    people[username] = l
        list_to_sort = []
        for person in people:
            list_to_sort.append((len(people[person]), person, people[person]))
        list_to_sort.sort(reverse=True)
        if debug:
            print("writing file..")
        for person in list_to_sort:
            number = str(person[0])
            name = person[1]
            if save_html:
                pic_url = pictures[name]
            profile_url = 'https://instagram.com/'+name+'/'
            message = ""
            if console:
                print(person[0], person[1], ":")
            for comment in person[2]:
                if save_html:
                    l = comment.split(":")
                    message = message +'<a href="https:'+l[2]+'">'+l[0]+'</a><br>'
                if console:
                    print(comment)
                    print("-----------------------------------------------")
            if save_html:
                if name != target_username:
                    file.write(construct_body("left",name,pic_url,profile_url,message,number))
                else:
                    file.write(construct_body("right", name, pic_url, profile_url, message, number))
            if console:
                print("###############################################")
        if save_html:
            file.write(get_footer())
            file.close()

    def get_most_liked_posts(self, user_id: str, debug=False, is_private=True) -> list:
        most_liked_posts = []
        posts = self.get_posts(user_id,debug,0,is_private)
        for post in posts:
            if self.stop_bool:
                return most_liked_posts
            likers_count = self.get_likes_count(post[0])
            most_liked_post = (likers_count,) + post #tuple addition
            most_liked_posts.append(most_liked_post)
        most_liked_posts.sort(reverse=True)
        return most_liked_posts

    def analyse_most_liked_posts(self,username: str, debug=False, console=True, save_html=False,path=None,is_private=True):
        if debug:
            print("getting user id")
        user_id = self.get_user_id(username)
        if debug:
            print("getting posts")
        most_liked_posts = self.get_most_liked_posts(user_id, debug, is_private)
        if console:
            for post in most_liked_posts:
                print(post[0], 'https://www.instagram.com/p/'+post[1]+'/')
        if save_html:
            if debug:
                print("getting user profile pic")
            profile_pic_url = self.get_profile_pic_url(username)
            if debug:
                print("writing")
            with open(path,"w",encoding="utf-8") as file:
                file.write(get_header(username))
                text = ""
                for post in most_liked_posts:
                    text = text + '<a href="https://www.instagram.com/p/'+post[1]+'/">'+str(post[0])+'</a><br>'
                profile_link = 'https://www.instagram.com/'+username+'/'
                file.write(construct_body("right",username,profile_pic_url,profile_link,text,""))
                file.write(get_footer())

    def analyse_most_likers(self,username: str, debug=False,console=True, save_html=False,path=None,is_private=True):
        if debug:
            print("getting user id")
        user_id = self.get_user_id(username)
        posts = self.get_posts(user_id,debug,0,is_private)
        people = {}
        if debug:
            print("analysing")
        for post in posts:
            likers = self.get_likers(post[0],debug,0)
            for liker in likers:
                if liker in people:
                    people[liker] = people[liker] + 1
                else:
                    people[liker] = 1
        list_view = [(value, key) for key, value in people.items()]
        list_view.sort(reverse=True)
        if save_html:
            file = open(path,"w",encoding="utf-8")
            file.write(get_header(username))
        for person in list_view:
            number = str(person[0])
            name = person[1][1]
            profile_pic_url = person[1][2]
            profile_url = "https://instagram.com/"+name+"/"
            if console:
                print(number, profile_url)
            if save_html:
                if name == username:
                    file.write(construct_body("right",name,profile_pic_url,profile_url,number,""))
                else:
                    file.write(construct_body("left",name,profile_pic_url,profile_url,number,""))
        if save_html:
            file.write(get_footer())
            file.close()

def unf(): # unfollows given users using chrome
    bot = Bot()
    bot.username = 'usename'
    bot.unfollow_all_with_chrome("username/", "path_to_chrome_driver","usename_not_followers.txt",[],False,False)

# test
if __name__ == "__main__":
    #unf()
    pass
