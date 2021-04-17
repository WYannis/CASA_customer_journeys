import time


class Chrono:
    def __init__(self, class_name=""):
        self.class_name = class_name
        self.start_time = None
        self.delay_s = None

    def start(self):
        #self.start_time = time.clock()
        self.start_time = time.perf_counter()
        return self

    def stop(self, function_name='', display=True):
        #delay_s = time.clock() - self.start_time
        self.delay_s = time.perf_counter() - self.start_time
        delay_str = self.beautify_sec(self.delay_s)
        if display:
            print("[{}] Time of function {}: {}.".format(self.class_name, function_name, delay_str))
        return self
        
    def get_delay(self):
        return self.delay_s

    @staticmethod
    def beautify_sec(s):
        """
        Beautify the number of seconds
        :return:
        """
        if s < 60:
            return '{:.2f} s'.format(s)
        elif s < 3600:
            return '{:.2f} min'.format(s / 60)
        elif s < 3600 * 24:
            return '{:.2f} h'.format(s / 3600)
        elif s < 3600 * 24 * 30.5:
            return '{:.2f} d'.format(s / 3600 / 24)
        elif s < 3600 * 24 * 365.25:
            return '{:.2f} mon'.format(s / 3600 / 24 / 30.5)
        else:
            return '{:.2f} Y'.format(s / 3600 / 24 / 365.25)
