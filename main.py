import pickle
import threading
import requests
from kivy.app import App
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import traceback
import os
import datetime
import keyboard

from Bot import Bot
from Settings import Settings


class MyGrid(GridLayout):
    def __init__(self, check=True,font_size=40,new_session=True,**kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.font_size = font_size
        self.new_session = new_session
        if self.new_session:
            self.second_session = MyGrid(check=False,font_size=20,new_session=False)
            self.popupWindow = Popup(title="New session", content=self.second_session, size_hint=(None, None), size=(600, 600))
        data = ("","")
        try:
            data = pickle.load(open(os.path.join(os.path.dirname(__file__),"data.data"), "rb" ))
        except:
            pass

        try:
            self.settings = pickle.load(open(os.path.join(os.path.dirname(__file__),"settings.data"), "rb" ))
        except:
            self.settings = Settings()


        self.bot = Bot()
        self.cols = 2

        self.add_widget(Label(text="username: ",height=30,size_hint=(.2,None)))
        self.username_text_input = TextInput(multiline=False,height=30,size_hint=(.2,None))
        self.add_widget(self.username_text_input)
        self.username_text_input.text = data[0]

        #self.add_widget(Label(text="password: ",height=30,size_hint=(.2,None)))
        #self.password_text_input = TextInput(multiline=False,password=True,height=30,size_hint=(.2,None))
        #self.add_widget(self.password_text_input)
        #self.password_text_input.text = data[1]

        self.log_in_button = Button(text="Login", font_size=font_size)
        self.log_in_button.bind(on_press=self.log_in_thread)
        self.add_widget(self.log_in_button)

        self.get_not_followers_button = Button(text="Get Notfollowers", font_size=font_size)
        self.get_not_followers_button.bind(on_press=self.get_not_followers_thread)
        self.add_widget(self.get_not_followers_button)

        self.unfollow_button = Button(text="Unfollow", font_size=font_size)
        self.unfollow_button.bind(on_press=self.unfollow_thread)
        self.add_widget(self.unfollow_button)

        self.explore_button = Button(text="Explore", font_size=font_size)
        self.explore_button.bind(on_press=self.exlpore_thread)
        self.add_widget(self.explore_button)

        self.tags_button = Button(text="Tags", font_size=font_size)
        self.tags_button.bind(on_press=self.tags_thread)
        self.add_widget(self.tags_button)

        self.settings_button = Button(text="Settings", font_size=font_size)
        self.settings_button.bind(on_press=self.open_settings)
        self.add_widget(self.settings_button)

        self.tags_exceptions_button = Button(text="Tags/Exceptions", font_size=font_size)
        self.tags_exceptions_button.bind(on_press=self.tags_exceptions)
        self.add_widget(self.tags_exceptions_button)

        self.medien_download_button = Button(text="Medien download", font_size=font_size)
        self.medien_download_button.bind(on_press=self.medien_download)
        self.add_widget(self.medien_download_button)

        self.analysis_button = Button(text="Analysis", font_size=font_size)
        self.analysis_button.bind(on_press=self.analysis)
        self.add_widget(self.analysis_button)

        self.export_messages_button = Button(text="Messages export", font_size=font_size)
        self.export_messages_button.bind(on_press=self.messages)
        self.add_widget(self.export_messages_button)

        self.new_session_button = Button(text="New session", font_size=font_size)
        self.new_session_button.bind(on_press=self.session)
        self.add_widget(self.new_session_button)

        self.stop_button = Button(text="Stop", font_size=font_size)
        self.stop_button.bind(on_press=self.stop_func)
        self.add_widget(self.stop_button)

        #self.check_bool = True
        #if self.settings.first_log_in:
            #self.check_bool = False
            #self.activate_button = Button(text="Activate", font_size=font_size)
            #self.activate_button.bind(on_press=self.activation_window)
            #self.add_widget(self.activate_button)

            #self.get_not_followers_button.disabled = True
            #self.unfollow_button.disabled = True
            #self.explore_button.disabled = True
            #self.tags_button.disabled = True
            #self.medien_download_button.disabled = True
            #self.analysis_button.disabled = True
            #self.export_messages_button.disabled = True

        #if self.check_bool:
            #if check:
                #self.check_if_allowed()

    def check(self):
        path_exists = False
        if not self.bot.username == str(self.username_text_input.text).strip():
            self.bot.authenticated = False
            self.bot.session = requests.Session()
        self.bot.username = str(self.username_text_input.text).strip()
        #self.bot.password = str(self.password_text_input.text).strip()
        if self.bot.username == "":
            print("username can not be empty :(")
            return False
        path_exists =  os.path.exists(os.path.join(os.path.dirname(__file__), self.bot.username))
        if not self.bot.authenticated:
            #self.log_in()
            if not path_exists:
                os.mkdir(os.path.join(os.path.dirname(__file__), self.bot.username))

            self.bot.safe_log_in(data_path=os.path.join(os.path.dirname(__file__),self.bot.username),webdriver_path=os.path.join(os.path.dirname(__file__),"chromedriver.exe"),new_log_in=False)
        if self.bot.authenticated:
            pickle.dump((self.bot.username, self.bot.password),
                        open(os.path.join(os.path.dirname(__file__), "data.data"), "wb"))
            return True

    def stop_func(self, instance):
        self.bot.stop_bool = True
        self.bot.ready = True

    def log_in_func(self):
        self.bot.username = str(self.username_text_input.text).strip()
        if self.bot.username == "":
            print("username can not be empty :(")
            return False
        path_exists = os.path.exists(os.path.join(os.path.dirname(__file__), self.bot.username))
        if not path_exists:
            os.mkdir(os.path.join(os.path.dirname(__file__), self.bot.username))
        self.bot.session = requests.Session()
        self.bot.safe_log_in(data_path=os.path.join(os.path.dirname(__file__), self.bot.username),
                             webdriver_path=os.path.join(os.path.dirname(__file__), "chromedriver.exe"),
                             new_log_in=False)
        #self.bot.log_in()
        self.bot.ready = True
        if self.bot.authenticated:
            pickle.dump((self.bot.username, self.bot.password),
                        open(os.path.join(os.path.dirname(__file__), "data.data"), "wb"))
            return True
        else:
            return False

    def log_in_thread(self, instance):
        if self.bot.ready:
            self.bot.stop_bool = False
            self.bot.ready = False
            thread = threading.Thread(target = self.log_in_func)
            thread.start()
        else:
            print("another task is running")

    def explore_func(self):
        try:
            settings = pickle.load(open(os.path.join(os.path.dirname(__file__),"settings.data"), "rb" ))
        except:
            settings = Settings()
        try:
            self.check()
            if not self.bot.authenticated:
                self.bot.ready = True
                return
            self.bot.explore(os.path.join(os.path.dirname(__file__),self.bot.username+"_"+"log.txt"),settings.maximum,settings.difference,
                         settings.how_many_pages,settings.how_many_posts_per_explore,
                         settings.likers_per_post, settings.how_many_likes_per_user,
                         settings.follow_if_private, settings.debug)
            print("explore finished")
            self.bot.ready = True
        except:
            if self.settings.debug:
                traceback.print_exc()
        finally:
            self.bot.ready = True

    def exlpore_thread(self, instance):
        if self.bot.ready:
            self.bot.stop_bool = False
            self.bot.ready = False
            thread = threading.Thread(target = self.explore_func)
            thread.start()
        else:
            print("another task is running")

    def tags_func(self):
        try:
            settings = pickle.load(open(os.path.join(os.path.dirname(__file__),"settings.data"), "rb" ))
        except:
            settings = Settings()
        try:
            data = pickle.load(open(os.path.join(os.path.dirname(__file__), "tags_exceptions.data"), "rb"))
            if len(data[0]) == 1:
                tags = ["me", "instagram"]
            else:
                tags = data[0]
        except:
            tags = ["me", "instagram"]
        try:
            self.check()
            if not self.bot.authenticated:
                self.bot.ready = True
                return
            self.bot.tags(os.path.join(os.path.dirname(__file__), self.bot.username+"_"+"log.txt"),tags,settings.maximum,
                      settings.difference,settings.how_many_tags,settings.how_much_per_tag,settings.tags_check_likers,
                      settings.likers_per_post,settings.how_many_likes_per_user,settings.follow_if_private,settings.debug)
            print("tags finished")
            self.bot.ready = True
        except:
            if self.settings.debug:
                traceback.print_exc()
        finally:
            self.bot.ready = True

    def tags_thread(self, instance):
        if self.bot.ready:
            self.bot.stop_bool = False
            self.bot.ready = False
            thread = threading.Thread(target=self.tags_func)
            thread.start()
        else:
            print("another task is running")

    def get_not_followers_func(self):
        try:
            settings = pickle.load(open(os.path.join(os.path.dirname(__file__),"settings.data"), "rb" ))
        except:
            settings = Settings()
        try:
            self.check()
            if not self.bot.authenticated:
                self.bot.ready = True
                return

            self.bot.write_not_followers(os.path.join(os.path.dirname(__file__), self.bot.username+"_"+"not_followers.txt"),debug=settings.debug)
            print("finished")
            self.bot.ready = True
        except:
            if self.settings.debug:
                traceback.print_exc()
        finally:
            self.bot.ready = True

    def get_not_followers_thread(self, instance):
        if self.bot.ready:
            self.bot.stop_bool = False
            self.bot.ready = False
            thread = threading.Thread(target=self.get_not_followers_func)
            thread.start()
        else:
            print("another task is running")

    def unfollow_func(self):
        try:
            data = pickle.load(open(os.path.join(os.path.dirname(__file__), "tags_exceptions.data"), "rb"))
            if len(data[1]) == 1:
                exceptions = ["jadkhaddad"]
            else:
                exceptions = data[1]
        except:
            exceptions = ["jadkhaddad"]
        try:
            self.check()
            if not self.bot.authenticated:
                self.bot.ready = True
                return
            self.bot.unfollow_all(os.path.join(os.path.dirname(__file__),self.bot.username+"_"+"not_followers.txt"),exceptions=exceptions)
            print("finished")
            self.bot.ready = True
        except:
            if self.settings.debug:
                traceback.print_exc()
        finally:
            self.bot.ready = True

    def unfollow_thread(self, instance):
        self.bot.stop_bool = True
        if self.bot.ready:
            self.bot.stop_bool = False
            self.bot.ready = False
            thread = threading.Thread(target=self.unfollow_func)
            thread.start()
        else:
            print("another task is running")

    def open_settings(self, instance):
        show = SettingsWindow()
        popupWindow = Popup(title="Settings", content=show, size_hint=(None, None), size=(530, 530))
        popupWindow.open()

    def tags_exceptions(self, instance):
        show = TagsExceptions()
        popupWindow = Popup(title="Tags/Exceptions", content=show, size_hint=(None, None), size=(530, 530))
        popupWindow.open()

    def medien_download(self, instance):
        show = MedienDownload(main=self)
        popupWindow = Popup(title="Medien download", content=show, size_hint=(None, None), size=(530, 530))
        popupWindow.open()

    def activation_window(self, instance):
        show = ActivationWindow(main=self)
        popupWindow = Popup(title="Medien download", content=show, size_hint=(None, None), size=(530, 530))
        popupWindow.open()

    def analysis(self, instance):
        show = Analysis(main=self)
        popupWindow = Popup(title="Analysis", content=show, size_hint=(None, None), size=(530, 530))
        popupWindow.open()

    def messages(self, instance):
        show = Messages(main=self)
        popupWindow = Popup(title="Messages export", content=show, size_hint=(None, None), size=(530, 530))
        popupWindow.open()

    def session(self, instance):
        if self.new_session:
            self.popupWindow.open()

    def check_if_allowed(self):
        response = requests.get(
            "https://raw.githubusercontent.com/JadKHaddad/JadKHaddad/master/SmartFollower.txt")
        list = response.text.split("\n")
        if self.settings.activation_key in list:
            print(":)")
        else:
            print("invalid activation key :(")
            self.settings.first_log_in = True

            self.get_not_followers_button.disabled = True
            self.unfollow_button.disabled = True
            self.explore_button.disabled = True
            self.tags_button.disabled = True
            self.medien_download_button.disabled = True

            self.activate_button = Button(text="Activate", font_size=self.font_size)
            self.activate_button.bind(on_press=self.activation_window)
            self.add_widget(self.activate_button)

class SettingsWindow(GridLayout):
    def __init__(self, **kwargs):
        super(SettingsWindow, self).__init__(**kwargs)
        try:
            self.settings = pickle.load(open(os.path.join(os.path.dirname(__file__), "settings.data"), "rb"))
        except:
            self.settings = Settings()

        self.cols = 2

        self.add_widget(Label(text="Maximum(number): "))
        self.maximum_text_input = TextInput(multiline=False)
        self.add_widget(self.maximum_text_input)
        self.maximum_text_input.text = str(self.settings.maximum)

        self.add_widget(Label(text="Difference(number): "))
        self.difference_text_input = TextInput(multiline=False)
        self.add_widget(self.difference_text_input)
        self.difference_text_input.text = str(self.settings.difference)

        self.add_widget(Label(text="How many pages(number): "))
        self.how_many_pages_text_input = TextInput(multiline=False)
        self.add_widget(self.how_many_pages_text_input)
        self.how_many_pages_text_input.text = str(self.settings.how_many_pages)

        self.add_widget(Label(text="How many tags(number): "))
        self.how_many_tags_text_input = TextInput(multiline=False)
        self.add_widget(self.how_many_tags_text_input)
        self.how_many_tags_text_input.text = str(self.settings.how_many_tags)

        self.add_widget(Label(text="How much per tag(number): "))
        self.how_much_per_tag_text_input = TextInput(multiline=False)
        self.add_widget(self.how_much_per_tag_text_input)
        self.how_much_per_tag_text_input.text = str(self.settings.how_much_per_tag)

        self.add_widget(Label(text="How many posts per explore(number): "))
        self.how_many_posts_per_explore_text_input = TextInput(multiline=False)
        self.add_widget(self.how_many_posts_per_explore_text_input)
        self.how_many_posts_per_explore_text_input.text = str(self.settings.how_many_posts_per_explore)

        self.add_widget(Label(text="Likers per post(number): "))
        self.likers_per_post_text_input = TextInput(multiline=False)
        self.add_widget(self.likers_per_post_text_input)
        self.likers_per_post_text_input.text = str(self.settings.likers_per_post)

        self.add_widget(Label(text="How many likes per user(number): "))
        self.how_many_likes_per_user_text_input = TextInput(multiline=False)
        self.add_widget(self.how_many_likes_per_user_text_input)
        self.how_many_likes_per_user_text_input.text = str(self.settings.how_many_likes_per_user)

        self.add_widget(Label(text='Follow if private'))
        self.follow_if_private_checkbox = CheckBox()
        self.add_widget(self.follow_if_private_checkbox)
        self.follow_if_private_checkbox.active = self.settings.follow_if_private

        self.add_widget(Label(text='Check likers in tags'))
        self.tags_check_likers_checkbox = CheckBox()
        self.add_widget(self.tags_check_likers_checkbox)
        self.tags_check_likers_checkbox.active = self.settings.tags_check_likers

        self.add_widget(Label(text='Debug'))
        self.debug_checkbox = CheckBox()
        self.add_widget(self.debug_checkbox)
        self.debug_checkbox.active = self.settings.debug

        self.save_button = Button(text="Save", font_size=20)
        self.save_button.bind(on_press=self.save)
        self.add_widget(self.save_button)

    def save(self, instance):
        try:
            self.settings.maximum = int(self.maximum_text_input.text)
            self.settings.difference = int(self.difference_text_input.text)
            self.settings.how_many_pages = int(self.how_many_pages_text_input.text)
            self.settings.how_many_tags = int(self.how_many_tags_text_input.text)
            self.settings.how_much_per_tag = int(self.how_much_per_tag_text_input.text)
            self.settings.how_many_posts_per_explore = int(self.how_many_posts_per_explore_text_input.text)
            self.settings.likers_per_post = int(self.likers_per_post_text_input.text)
            self.settings.how_many_likes_per_user = int(self.how_many_likes_per_user_text_input.text)
            self.settings.follow_if_private = bool(self.follow_if_private_checkbox.active)
            self.settings.tags_check_likers = bool(self.tags_check_likers_checkbox.active)
            self.settings.debug = bool(self.debug_checkbox.active)


            pickle.dump(self.settings,
                        open(os.path.join(os.path.dirname(__file__),"settings.data"), "wb"))
            print("saved")
            keyboard.press_and_release('esc')
        except:
            print("please check the fields")

class TagsExceptions(GridLayout):
    def __init__(self, **kwargs):
        super(TagsExceptions, self).__init__(**kwargs)
        try:
            tags = ["me","instagram"]
            exceptions = ["jadkhaddad"]
            data = pickle.load(open(os.path.join(os.path.dirname(__file__), "tags_exceptions.data"), "rb"))

            if len(data[0]) == 1:
                data = (tags,data[1])
            if len(data[1]) == 1:
                data = (data[0], exceptions)
        except:
            print("cant load")
            #traceback.print_exc()
            tags = ["me","instagram"]
            exceptions = ["jadkhaddad"]
            data = (tags,exceptions)

        self.cols = 2

        self.add_widget(Label(text="Tags: "))
        self.tags_text_input = TextInput(multiline=True)
        self.add_widget(self.tags_text_input)
        tags_text = ""
        for tag in data[0]:
            tags_text = tags_text + tag
            if tag != data[0][-1]:
                tags_text = tags_text + ","
        self.tags_text_input.text = tags_text

        self.add_widget(Label(text="Exceptions: "))
        self.exceptions_text_input = TextInput(multiline=True)
        self.add_widget(self.exceptions_text_input)
        exceptions_text = ""
        for exception in data[1]:
            exceptions_text = exceptions_text + exception
            if exception != data[1][-1]:
                exceptions_text = exceptions_text + ","
        self.exceptions_text_input.text = exceptions_text

        self.save_button = Button(text="Save", font_size=20)
        self.save_button.bind(on_press=self.save)
        self.add_widget(self.save_button)

    def save(self, instance):
        try:
            tags = str(self.tags_text_input.text).split(",")
            exceptions = str(self.exceptions_text_input.text).split(",")
            pickle.dump((tags,exceptions),
                        open(os.path.join(os.path.dirname(__file__), "tags_exceptions.data"), "wb"))
            print("saved")
            keyboard.press_and_release('esc')
        except:
            print("please check the fields")

class MedienDownload(GridLayout):
    def __init__(self, main:MyGrid,**kwargs):
        super(MedienDownload, self).__init__(**kwargs)
        self.main = main

        self.cols = 2

        self.add_widget(Label(text="From user: "))
        self.from_user_text_input = TextInput(multiline=False)
        self.add_widget(self.from_user_text_input)

        self.add_widget(Label(text='Is private'))
        self.is_private_checkbox = CheckBox()
        self.add_widget(self.is_private_checkbox)

        self.add_widget(Label(text='Stories'))
        self.stories_checkbox = CheckBox()
        self.add_widget(self.stories_checkbox)

        self.add_widget(Label(text='Highlights'))
        self.highlights_checkbox = CheckBox()
        self.add_widget(self.highlights_checkbox)

        self.add_widget(Label(text='Posts'))
        self.posts_checkbox = CheckBox()
        self.add_widget(self.posts_checkbox)

        self.add_widget(Label(text='Photos'))
        self.photos_checkbox = CheckBox()
        self.add_widget(self.photos_checkbox)

        self.add_widget(Label(text='Videos'))
        self.videos_checkbox = CheckBox()
        self.add_widget(self.videos_checkbox)

        self.download_button = Button(text="Download", font_size=20)
        self.download_button.bind(on_press=self.download_thread)
        self.add_widget(self.download_button)

        self.single_post_button = Button(text="Single post", font_size=20)
        self.single_post_button.bind(on_press=self.single_post)
        self.add_widget(self.single_post_button)

    def download_func(self):
        try:
            authenticated = False
            if not self.main.bot.authenticated:
                authenticated = self.main.check()
            else:
                authenticated = True
            if not authenticated:
                self.main.bot.ready = True
                print("ot downloading..")
                return
            authenticated = False
            photos = self.photos_checkbox.active
            videos = self.videos_checkbox.active
            user = str(self.from_user_text_input.text).strip()
            if (photos or videos) and (str(self.from_user_text_input.text).strip() != "") and (self.highlights_checkbox.active or self.posts_checkbox.active or self.stories_checkbox.active):
                path_exists = os.path.exists(os.path.join(os.path.dirname(__file__), user+"_media"))
                if not path_exists:
                    os.mkdir(os.path.join(os.path.dirname(__file__), user+"_media"))

                print("downloading..")
                user_id = self.main.bot.get_user_id(user)
                if self.stories_checkbox.active:
                    self.main.bot.download_stories(user_id=user_id,path=os.path.join(os.path.dirname(__file__),os.path.join(user+"_media",str(datetime.datetime.now().timestamp())+"_story_")),
                                                      photos=photos,videos=videos)
                    print("stories download finished")
                if self.posts_checkbox.active:
                    self.main.bot.download_posts(user_id=user_id, path=os.path.join(os.path.dirname(__file__),os.path.join(user+"_media",str(datetime.datetime.now().timestamp())+"_post_")), how_much=0,
                                 photos=photos,videos=videos,debug=False,is_private=self.is_private_checkbox.active)
                    print("posts download finished")
                if self.highlights_checkbox.active:
                    self.main.bot.download_highlights(user_id=user_id,path=os.path.join(os.path.dirname(__file__),os.path.join(user+"_media",str(datetime.datetime.now().timestamp())+"_highlight_")),
                                                      photos=photos,videos=videos)
                    print("highlights download finished")

                print("download finished")
            self.main.bot.ready = True
        except:
            if self.main.settings.debug:
                traceback.print_exc()
        finally:
            self.main.bot.ready = True

    def download_thread(self,instance):
        if self.main.bot.ready:
            self.main.bot.stop_bool = False
            self.main.bot.ready = False
            thread = threading.Thread(target=self.download_func)
            thread.start()
        else:
            print("another task is running")

    def single_post(self, instance):
        show = SinglePostDownload(main=self.main)
        popupWindow = Popup(title="Single post download", content=show, size_hint=(None, None), size=(530, 530))
        popupWindow.open()

class SinglePostDownload(GridLayout):
    def __init__(self, main:MyGrid,**kwargs):
        super(SinglePostDownload, self).__init__(**kwargs)
        self.main = main
        self.cols = 2
        self.add_widget(Label(text="From user: "))
        self.from_user_text_input = TextInput(multiline=False)
        self.add_widget(self.from_user_text_input)

        self.add_widget(Label(text='Is private'))
        self.is_private_checkbox = CheckBox()
        self.add_widget(self.is_private_checkbox)

        self.download_button = Button(text="Download", font_size=20)
        self.download_button.bind(on_press=self.download_thread)
        self.add_widget(self.download_button)

    def download_thread(self, instance):
        pass

    def downlad_func(self, instance):
        pass


class ActivationWindow(GridLayout):
    def __init__(self,main:MyGrid, **kwargs):
        super(ActivationWindow, self).__init__(**kwargs)
        self.main = main

        self.cols = 2

        self.add_widget(Label(text="Activation key: "))
        self.activation_key_text_input = TextInput(multiline=False)
        self.add_widget(self.activation_key_text_input)

        self.ok_button = Button(text="Ok", font_size=20)
        self.ok_button.bind(on_press=self.check)
        self.add_widget(self.ok_button)

    def check(self, instance):
        response = requests.get(
            "https://raw.githubusercontent.com/JadKHaddad/JadKHaddad/master/SmartFollower.txt")
        list = response.text.split("\n")
        if str(self.activation_key_text_input.text).strip() in list:
            print(":)")
            self.main.settings.first_log_in = False
            self.main.settings.activation_key = str(self.activation_key_text_input.text).strip()
            pickle.dump(self.main.settings,
                        open(os.path.join(os.path.dirname(__file__), "settings.data"), "wb"))
            self.main.get_not_followers_button.disabled = False
            self.main.unfollow_button.disabled = False
            self.main.explore_button.disabled = False
            self.main.tags_button.disabled = False
            self.main.medien_download_button.disabled = False
            self.main.analysis_button.disabled = False
            self.main.export_messages_button.disabled = False
            self.main.activate_button.disabled = True
        else:
            print("invalid activation key :(")

class Analysis(GridLayout):
    def __init__(self,main:MyGrid, **kwargs):
        super(Analysis, self).__init__(**kwargs)
        self.main = main

        self.cols = 2

        self.add_widget(Label(text="User: "))
        self.user_text_input = TextInput(multiline=False)
        self.add_widget(self.user_text_input)

        self.add_widget(Label(text='Is private'))
        self.is_private_checkbox = CheckBox()
        self.add_widget(self.is_private_checkbox)

        self.add_widget(Label(text='Comments'))
        self.comments_checkbox = CheckBox()
        self.add_widget(self.comments_checkbox)

        self.add_widget(Label(text='Most liked Posts'))
        self.most_liked_posts_checkbox = CheckBox()
        self.add_widget(self.most_liked_posts_checkbox)

        self.add_widget(Label(text='Most likers'))
        self.most_likers_checkbox = CheckBox()
        self.add_widget(self.most_likers_checkbox)

        self.add_widget(Label(text='Save file'))
        self.save_file_checkbox = CheckBox()
        self.add_widget(self.save_file_checkbox)

        self.add_widget(Label(text='Console'))
        self.console_checkbox = CheckBox()
        self.add_widget(self.console_checkbox)

        #comments
        self.analyse_button = Button(text="Analyse", font_size=20)
        self.analyse_button.bind(on_press=self.analyse_thread)
        self.add_widget(self.analyse_button)


    def analyse_thread(self, instance):
        if self.main.bot.ready:
            self.main.bot.stop_bool = False
            self.main.bot.ready = False
            thread = threading.Thread(target=self.analyse_func)
            thread.start()
        else:
            print("another task is running")

    def analyse_func(self):
        try:
            authenticated = False
            if not self.main.bot.authenticated:
                authenticated = self.main.check()
            else:
                authenticated = True
            if not authenticated:
                self.main.bot.ready = True
                print("not anaylising")
                return
            console = self.console_checkbox.active
            save = self.save_file_checkbox.active
            comments = self.comments_checkbox.active
            likes = self.most_liked_posts_checkbox.active
            most_likers = self.most_likers_checkbox.active
            user = str(self.user_text_input.text).strip()
            if (console or save) and (str(self.user_text_input.text).strip() != "") and (comments or likes or most_likers):
                print("analysing..")
                user_id = self.main.bot.get_user_id(user)
                if comments:
                    self.main.bot.analyse_posts_for_comments(user_id=user_id,target_username=user,console=console,save_html=save,
                                                         path=os.path.join(os.path.dirname(__file__), user+"_comments_analysis.html")
                                                         ,is_private=self.is_private_checkbox.active,debug=self.main.settings.debug)
                if likes:
                    self.main.bot.analyse_most_liked_posts(path=os.path.join(os.path.dirname(__file__), user+"_most_liked_posts_analysis.html"), username=user,
                                                debug=self.main.settings.debug, save_html=save, console=console)

                if most_likers:
                    self.main.bot.analyse_most_likers(path=os.path.join(os.path.dirname(__file__), user+"_most_likers_analysis.html"),username=user,
                                                      debug=self.main.settings.debug,is_private=self.is_private_checkbox.active,console=console,save_html=save)

                print("finished analysing")
            self.main.bot.ready = True
        except:
            if self.main.settings.debug:
                traceback.print_exc()
        finally:
            self.main.bot.ready = True

class Messages(GridLayout):
    def __init__(self,main:MyGrid, **kwargs):
        super(Messages, self).__init__(**kwargs)
        self.main = main

        self.cols = 2

        self.add_widget(Label(text="User: "))
        self.user_text_input = TextInput(multiline=False)
        self.add_widget(self.user_text_input)

        self.add_widget(Label(text="Date: "))
        self.date_text_input = TextInput(multiline=False)
        self.add_widget(self.date_text_input)
        self.date_text_input.text ="Year,Month,Day"

        self.export_button = Button(text="export", font_size=20)
        self.export_button.bind(on_press=self.export_thread)
        self.add_widget(self.export_button)

    def export_thread(self, instance):
        if self.main.bot.ready:
            self.main.bot.stop_bool = False
            self.main.bot.ready = False
            thread = threading.Thread(target=self.export_func)
            thread.start()
        else:
            print("another task is running")

    def export_func(self):
        target_user = str(self.user_text_input.text).strip()
        if target_user == "":
            print("user can not br empty")
            self.main.bot.ready = True
            return
        try:
            year,month,day = str(self.date_text_input.text).strip().split(",")
            if self.main.settings.debug:
                print(year, month, day)
            target_date = datetime.date(int(year), int(month), int(day))
        except:
            if self.main.settings.debug:
                traceback.print_exc()
            print("please check the fields and try again..")
            self.date_text_input.text = "Year,Month,Day"
        finally:
            self.main.bot.ready = True
        self.main.check()
        print("exporting..")
        self.main.bot.export_messages(os.path.join(os.path.dirname(__file__), "chat_with_" + target_user + ".html"),
                                      target_user, target_date, self.main.settings.debug)
        print("export finished")
        self.main.bot.ready = True

class MyApp(App):
    def build(self):
        self.title = 'Smart Follower (alpha)'
        self.icon = os.path.join(os.path.dirname(__file__), 'icon.png')
        return MyGrid()

if __name__ == "__main__":
    MyApp().run()
