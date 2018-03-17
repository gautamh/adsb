from abc import ABCMeta, abstractmethod

class FlightListLoader:
    __metaclass__ = ABCMeta

    ''' Loads a list of flight paths.

    Each flight path is a list of tuples (lat, long, time).
    '''
    @abstractmethod
    def load_flight_path_list(self): raise NotImplementedError

class DatastoreListLoader(FlightListLoader):
    def load_flight_path_list(self):
        raise NotImplementedError




