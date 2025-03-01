from SPMUtil import JsonEditor

class BaseModule(object):

    @property
    def enabled(self):
        pass
    @enabled.getter
    def enabled(self):
        return self._enabled
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        if value:
            print(type(self).__name__, "has been enabled")
        else:
            print(type(self).__name__, "has been disabled")



    def __init__(self):
        self._enabled = True
        self.is_essential_module = False

    def update_class_dict_param(self, m_dict: dict):
        # do not add new key
        self.__dict__.update((k, m_dict[k]) for k in (self.__dict__.keys() & m_dict.keys()))

    def edit_class_dict_param_gui(self):
        JsonEditor(show_private_member=False).EditDict(self.__dict__, callback=self.update_class_dict_param)

    def print_notice(self, msg: str):
        print("     " + type(self).__name__ + "@@@\033[33m" + msg + "\033[0m")

    def print_info(self, msg: str):
        print("     " + type(self).__name__ + "@@@\033[32m" + msg + "\033[0m")

    def print_warning(self, msg: str):
        print("     " + type(self).__name__ + "@@@\033[31m" + msg + "\033[0m")



if __name__ == '__main__':
    class TestBaseClass(BaseModule):
        def __init__(self):
            super().__init__()
            self.a = 2
            self.b = "str"
            self.c = [0,1,2]

    t = TestBaseClass()
    # t.edit_class_dict_param_gui()
    # print(t.__dict__)




