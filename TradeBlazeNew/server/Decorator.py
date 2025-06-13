import threading

# Any class decorated with annotation @singleton will become Singleton
# As an example, see the class SimulatedBroker.
def singleton(cls):
    instances = {}
    lock = threading.Lock()

    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
            return instances[cls]

    return get_instance
