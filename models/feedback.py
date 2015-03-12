import utils.event_globals as EG

class Feedback:
    def __init__(self, _id=None, submitter_id=None, date_created=None,
                 comment_type=None, owner_id=None, date_closed=None,
		 comment=None):
        self._id = _id
        self.submitter_id = submitter_id
        self.date_created = date_created
        self.comment_type = comment_type
        self.comment = comment
        self.owner_id = owner_id
        self.date_closed = date_closed


if __name__ == "__main__":
    print("Called from command line\n")
