from .point import Point
class MyRectCell:
    """定义一个单元格地址和内容"""

    def __init__(
        self,
        text: str = None,
        left: float = None,
        top: float = None,
        right: float = None,
        bottom: float = None):
        self.__text = text
        self.__left = left
        self.__top = top
        self.__right = right
        self.__bottom = bottom

    def init_by_cell(self, cell = None):
        from cell import MyCell
        if isinstance(cell, MyCell) and cell is not None:
            self.__text = cell.text
            self.__left = (cell.top_left.x + cell.bottom_left.x) / 2
            self.__right = (cell.top_right.x + cell.bottom_right.x) / 2
            self.__bottom = (cell.bottom_left.y + cell.bottom_right.y) / 2
            self.__top = (cell.top_left.y + cell.top_right.y) / 2
            return True
        return False

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value: str):
        self.__text = value

    @property
    def left(self):
        return self.__left

    @left.setter
    def left(self, value: float):
        self.__left = value

    @property
    def top(self):
        return self.__top

    @top.setter
    def top(self, value: float):
        self.__top = value

    @property
    def right(self):
        return self.__right

    @right.setter
    def right(self, value: float):
        self.__right = value

    @property
    def bottom(self):
        return self.__bottom

    @bottom.setter
    def bottom(self, value: float):
        self.__bottom = value

    @property
    def top_left(self):
        return Point(self.__left, self.__top)

    @top_left.setter
    def top_left(self, value: Point):
        self.__left = value.x
        self.__top = value.y

    @property
    def top_right(self):
        return Point(self.__right, self.__top)

    @top_right.setter
    def top_right(self, value: Point):
        self.__right = value.x
        self.__top = value.y

    @property
    def bottom_left(self):
        return Point(self.__left, self.__bottom)

    @bottom_left.setter
    def bottom_left(self, value: Point):
        self.__left = value.x
        self.__bottom = value.y

    @property
    def bottom_right(self):
        return Point(self.__right, self.__bottom)

    @bottom_right.setter
    def bottom_right(self, value: Point):
        self.__right = value.x
        self.__bottom = value.y
