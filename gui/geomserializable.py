# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from graphcore.settings import GraphCoreSettings, GraphCoreSettingsUser


# GeometrySerializer
class GeometrySerializer(QWidget):
    def __init__(self, parent=None, serialize_position=None, serialize_size=None):
        super().__init__(parent)
        self._serialize_position = serialize_position
        self._serialize_size = serialize_size

    @property
    def serialize_position(self):
        return self._serialize_position

    @serialize_position.setter
    def serialize_position(self, setter):
        self._serialize_position = setter

    @property
    def serialize_size(self):
        return self._serialize_size

    @serialize_size.setter
    def serialize_size(self, setter):
        self._serialize_size = setter

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if self.serialize_size is not None:
            size = event.size()
            self.serialize_size(size.width(), size.height())

    def moveEvent(self, event: QMoveEvent):
        super().moveEvent(event)
        if self.serialize_position is not None:
            pos = event.pos()
            self.serialize_position(pos.x(), pos.y())


# Geometry Serializable Widget class
class GeometrySerializable(QWidget):
    def __init__(self, parent=None, setting_name=None, settings=None):
        super(QWidget, self).__init__(parent)
        self._setting_name = setting_name
        self._settings = settings
        if setting_name is not None and settings is not None:
            self.set_settings(setting_name, settings)

    @property
    def setting_name(self) -> str:
        return self._setting_name

    @property
    def settings(self) -> GraphCoreSettings:
        return self._settings

    def set_settings(self, setting_name: str, settings: GraphCoreSettings):
        self._setting_name = setting_name
        self._settings = settings
        self.move(self.settings.setting(self.setting_name)['x'], self.settings.setting(self.setting_name)['y'])
        self.resize(self.settings.setting(self.setting_name)['width'], self.settings.setting(self.setting_name)['height'])

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        size = event.size()
        self.settings.setting(self.setting_name)['width'] = size.width()
        self.settings.setting(self.setting_name)['height'] = size.height()

    def moveEvent(self, event: QMoveEvent):
        super().moveEvent(event)
        pos = event.pos()
        self.settings.setting(self.setting_name)['x'] = pos.x()
        self.settings.setting(self.setting_name)['y'] = pos.y()


class GeometrySerializableFrame(QFrame, GeometrySerializer):
    def __init__(self, parent=None, serialize_position=None, serialize_size=None):
        super().__init__(parent, serialize_position=serialize_position, serialize_size=serialize_size)

# class GeometrySerializableFrame(QFrame, GeometrySerializer):
#     def __init__(self, parent, serialize_position, serialize_size):
#         super().__init__(parent, serialize_position=serialize_position, serialize_size=serialize_size)


class GeometrySerializableDialog(QDialog, GeometrySerializer):
    def __init__(self, parent=None, serialize_position=None, serialize_size=None):
        super().__init__(parent, serialize_position=serialize_position, serialize_size=serialize_size)

# class GeometrySerializableFrame(QFrame, GeometrySerializable):
#     def __init__(self, parent=None, setting_name=None, settings=None):
#         super().__init__(parent, setting_name, settings)


# class GeometrySerializableDialog(QDialog, GeometrySerializable):
#     def __init__(self, parent=None, setting_name=None, settings=None):
#         super().__init__(parent, setting_name, settings)

