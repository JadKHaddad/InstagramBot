class Settings:
    def __init__(self, maximum=500, difference=100, how_many_pages=3, how_many_posts_per_explore=20
                , likers_per_post=5, how_many_likes_per_user=3,follow_if_private=False, debug=False,
                 how_many_tags=3,tags_check_likers=False,how_much_per_tag=20,first_log_in=True,activation_key=None):
        self.maximum = maximum
        self.difference = difference
        self.how_many_pages = how_many_pages
        self.how_many_posts_per_explore = how_many_posts_per_explore
        self.likers_per_post = likers_per_post
        self.how_many_likes_per_user = how_many_likes_per_user
        self.follow_if_private = follow_if_private
        self.debug = debug

        self.how_many_tags = how_many_tags
        self.tags_check_likers = tags_check_likers
        self.how_much_per_tag = how_much_per_tag

        self.first_log_in = first_log_in
        self.activation_key = activation_key


