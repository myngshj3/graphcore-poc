
import os
from graphcore.settings import gcore_settings
from gui.mainwindow import GraphCoreEditorMainWindow
from gui.Ui_MainWindow import Ui_MainWindow
from gui.coordfinderwidget import CoordFinderWidget
from gui.CoordinationFinderWidget import Ui_CoordFinderForm
from gui.console import ConsoleDialog
from gui.Ui_ScriptEditor import Ui_ScriptEdior
from gui.Ui_ConsoleWidget import Ui_ConsoleForm
from gui.scripteditor import ScriptEditorDialog
from gui.Ui_SolverController import Ui_SolverControllerForm
from gui.solvercontroller import SolverControllerDialog
from graphcore.shell import GraphCoreShell
from gui.geomserializable import GeometrySerializableFrame
from graphcore.graphicsscene import GraphCoreScene
# from graphcore.constraint import set_constraint_main_window
import sys
from PyQt5.QtWidgets import *


def main():
    # load settings
    settings = gcore_settings()

    # load shell
    shell = GraphCoreShell(settings=settings)
    handler = shell.handler
    async_handler = shell.async_handler

    app = QApplication(sys.argv)

    # setup main window
    main_ui = Ui_MainWindow()
    main_window = GraphCoreEditorMainWindow(main_ui, settings, shell, handler, async_handler)
    main_window.move(settings.setting_value(['main-window', 'x']), settings.setting_value(['main-window', 'y']))
    main_window.resize(settings.setting_value(['main-window', 'width']), settings.setting_value(['main-window', 'height']))
    main_ui.left_pane.move(settings.setting_value(['main-window-left-pane', 'x']),
                           settings.setting_value(['main-window-left-pane', 'y']))
    main_ui.left_pane.resize(settings.setting_value(['main-window-left-pane', 'width']),
                             settings.setting_value(['main-window-left-pane', 'height']))
    main_ui.left_top_pane.move(settings.setting_value(['main-window-left-top-pane', 'x']),
                               settings.setting_value(['main-window-left-top-pane', 'y']))
    main_ui.left_top_pane.resize(settings.setting_value(['main-window-left-top-pane', 'height']),
                                 settings.setting_value(['main-window-left-top-pane', 'width']))
    main_ui.editorTabWidget.setCurrentIndex(settings.setting_value(['editor-tab-widget', 'tab-index']))
    main_ui.messageTab.setCurrentIndex(settings.setting_value(['message-tab-widget', 'tab-index']))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window', 'x'], main_window.frameGeometry().x()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window', 'y'], main_window.frameGeometry().y()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window', 'width'], main_window.frameGeometry().width()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window', 'height'], main_window.frameGeometry().height()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window-left-pane', 'x'],
                                                                      main_ui.left_pane.frameGeometry().x()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window-left-pane', 'y'],
                                                                      main_ui.left_pane.frameGeometry().y()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window-left-pane', 'width'],
                                                                      main_ui.left_pane.frameGeometry().width()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window-left-pane', 'height'],
                                                                      main_ui.left_pane.frameGeometry().height()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window-left-top-pane', 'x'],
                                                                      main_ui.left_top_pane.frameGeometry().x()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window-left-top-pane', 'y'],
                                                                      main_ui.left_top_pane.frameGeometry().y()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window-left-top-pane', 'width'],
                                                                      main_ui.left_top_pane.frameGeometry().width()))
    main_window.serializers.append(lambda: settings.set_setting_value(['main-window-left-top-pane', 'height'],
                                                                      main_ui.left_top_pane.frameGeometry().height()))
    main_window.serializers.append(lambda: settings.set_setting_value(['editor-tab-widget', 'tab-index'],
                                                                      main_ui.editorTabWidget.currentIndex()))
    main_window.serializers.append(lambda: settings.set_setting_value(['message-tab-widget', 'tab-index'],
                                                                      main_ui.messageTab.currentIndex()))

    main_window.property_init()
    main_window.error_message_init()
    main_window.constraints_init()

    # setup layout manager
    layout_manager = CoordFinderWidget(async_handler)
    layout_manager_ui = Ui_CoordFinderForm()
    layout_manager.ui = layout_manager_ui
    main_window.coord_finder = layout_manager

    # setup console
    console_ui = Ui_ConsoleForm()
    console = ConsoleDialog(ui=console_ui, handler=handler, async_handler=async_handler)
    console.move(settings.setting_value(['console', 'x']), settings.setting_value(['console', 'y']))
    console.resize(settings.setting_value(['console', 'width']), settings.setting_value(['console', 'height']))
    main_window.console = console
    main_window.serializers.append(lambda: settings.set_setting_value(['console', 'x'], console.frameGeometry().x()))
    main_window.serializers.append(lambda: settings.set_setting_value(['console', 'y'], console.frameGeometry().y()))
    main_window.serializers.append(lambda: settings.set_setting_value(['console', 'width'], console.frameGeometry().width()))
    main_window.serializers.append(lambda: settings.set_setting_value(['console', 'height'], console.frameGeometry().height()))

    # setup script editor
    script_editor_ui = Ui_ScriptEdior()
    script_editor = ScriptEditorDialog(main_window, script_editor_ui, handler=handler, async_handler=async_handler)
    script_editor.move(settings.setting_value(['script-editor', 'x']),
                       settings.setting_value(['script-editor', 'y']))
    script_editor.resize(settings.setting_value(['script-editor', 'width']),
                         settings.setting_value(['script-editor', 'height']))
    main_window.script_editor = script_editor
    main_window.serializers.append(lambda: settings.set_setting_value(['script-editor', 'x'],
                                                                      script_editor.frameGeometry().x()))
    main_window.serializers.append(lambda: settings.set_setting_value(['script-editor', 'y'],
                                                                      script_editor.frameGeometry().y()))
    main_window.serializers.append(lambda: settings.set_setting_value(['script-editor', 'width'],
                                                                      script_editor.frameGeometry().width()))
    main_window.serializers.append(lambda: settings.set_setting_value(['script-editor', 'height'],
                                                                      script_editor.frameGeometry().height()))

    # setup solve controller
    solver_controller_ui = Ui_SolverControllerForm()
    solver_controller = SolverControllerDialog(main_window, solver_controller_ui, async_handler)
    solver_controller.move(settings.setting_value(['solver-controller', 'x']),
                           settings.setting_value(['solver-controller', 'y']))
    solver_controller.resize(settings.setting_value(['solver-controller', 'width']),
                             settings.setting_value(['solver-controller', 'height']))
    main_window.solver_controller = solver_controller
    main_window.serializers.append(
        lambda: settings.set_setting_value(['solver-controller', 'x'], solver_controller.frameGeometry().x()))
    main_window.serializers.append(
        lambda: settings.set_setting_value(['solver-controller', 'y'], solver_controller.frameGeometry().y()))
    main_window.serializers.append(
        lambda: settings.set_setting_value(['solver-controller', 'width'], solver_controller.frameGeometry().width()))
    main_window.serializers.append(
        lambda: settings.set_setting_value(['solver-controller', 'height'], solver_controller.frameGeometry().height()))

    # etc.
    # set_constraint_main_window(main_window)
    
    # show main window
    main_window.command_new_model()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
