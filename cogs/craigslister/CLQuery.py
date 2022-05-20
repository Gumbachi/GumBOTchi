class CLQuery:
    def __init__(   
                self, uid, zip_code, state, channel, site, 
                keywords, spam_tolerance = 1, budget = 1000, distance = 30, 
                category="sss", has_image=False, ping=True
        ):
        self.owner_id = uid
        self.zip_code = zip_code
        self.state = state
        self.channel = channel
        self.site = site
        self.budget = budget
        self.distance = distance
        self.keywords = keywords
        self.has_image = has_image
        self.spam_tolerance = spam_tolerance
        self.ping = ping
        self.category = category
        self.sent_listings = set()

    def to_db(self):
        final_dic = {}
        for k, v in self.__dict__.items():
            if k not in ["sent_listings"]:
                final_dic[k] = v
        return final_dic 