

class Events:
    def register(self, event_name, action):
        event_filter = myContract.events. < event_name >.createFilter({'filter': {'arg1': 10}})


event_filter = myContract.events.<event_name>.createFilter({'filter': {'arg1':10}})
event_filter.get_new_entries()