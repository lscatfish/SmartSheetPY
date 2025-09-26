import copy

from point import Point


class MyCell:
    def __init__(
        self,
        text: str = None,
        top_left: Point = None,
        top_right: Point = None,
        bottom_left: Point = None,
        bottom_right: Point = None):
        self.__top_left = copy.deepcopy(top_left)
        self.__top_right = copy.deepcopy(top_right)
        self.__bottom_left = copy.deepcopy(bottom_left)
        self.__bottom_right = copy.deepcopy(bottom_right)
        self.__text = text

    def init_by_rect(self, rect = None):
        from rectcell import MyRectCell
        if isinstance(rect, MyRectCell) and rect is not None:
            self.__top_left = rect.top_left
            self.__top_right = rect.top_right
            self.__bottom_left = rect.bottom_left
            self.__bottom_right = rect.bottom_right
            self.__text = rect.text
            return True
        return False

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value: str):
        self.__text = value

    @property
    def top_left(self):
        return copy.deepcopy(self.__top_left)

    @top_left.setter
    def top_left(self, value: Point):
        self.__top_left = copy.deepcopy(value)

    @property
    def top_right(self):
        return copy.deepcopy(self.__top_right)

    @top_right.setter
    def top_right(self, value: Point):
        self.__top_right = copy.deepcopy(value)

    @property
    def bottom_left(self):
        return copy.deepcopy(self.__bottom_left)

    @bottom_left.setter
    def bottom_left(self, value: Point):
        self.__bottom_left = copy.deepcopy(value)

    @property
    def bottom_right(self):
        return copy.deepcopy(self.__bottom_right)

    @bottom_right.setter
    def bottom_right(self, value: Point):
        self.__bottom_right = copy.deepcopy(value)
