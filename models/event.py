

class Event:
    def __init__(self, _id=None, creator_id=None, title=None, start_time=None,
                 end_time=None, city_id=None, description=None, address1=None,
                 address2=None, zip=None, website=None, categories=None,
                 date_created=None, date_last_updated=None, hit_counter=0,
                 credits_paid=0):
        self._id = _id
        self.creator_id = creator_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.city_id = city_id
        self.description = description
        self.address1 = address1
        self.address2 = address2
        self.zip = zip
        self.website = website

        self.categories = []
        # 'NoneType' object is not iterable
        if categories:
            for category in categories:
                self.categories.append(category)

        self.date_created = date_created
        self.date_last_updated = date_last_updated
        self.hit_counter = hit_counter
        self.credits_paid = credits_paid

    @property
    def id(self):
        """The 'id' property."""
        return self._id
    
    @id.setter
    def id(self, event_id):
        self._id = event_id
