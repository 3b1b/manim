class EventListner(object):
    def __init__(self, mobject, event_type, event_callback):
        self.mobject = mobject
        self.event_type = event_type
        self.callback = event_callback

    def __eq__(self, o: object) -> bool:
        return_val = False
        try:
            return_val = self.callback == o.callback \
                and self.mobject == o.mobject \
                and self.event_type == o.event_type
        except:
            pass
        return return_val
