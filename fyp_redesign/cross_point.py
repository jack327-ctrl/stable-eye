from PySide2.QtWidgets import QGraphicsColorizeEffect


class point_base(object):
    def __init__(self,x,y,color,operator):
        self.x=x
        self.y=y
        self.color=color
        self.operator=operator
    