import maya.cmds as cmds


class Progress(object):
    """
    Simple wrapper class that will build a basic progress window. The initialation can take up to three arguments, title, display and a maximum value.

    Methods:
        -> update( amount ):
            Increases the progress bar display by the given amount
        -> kill( ):
            Closes the window
        -> reset( displayStr ):
            Sets the progress bar back to zero, and allows you to pass in a new display string
    """
    WIN_NAME = ""
    PROGRESS_BAR_UI = ""
    TEXT_UI = ""
    WIN_TITLE = "Progress Window"
    WIN_DISPLAY = "Progress:"
    MAX_VALUE = 100
    VALUE = 0
    WIN_WIDTH = 500
    WIN_HEIGHT = 80

    def __init__(self, winTitle="Progress Window", displayText="Progress:", maxValue=100):
        self.WIN_TITLE = winTitle
        self.WIN_DISPLAY = displayText
        self.MAX_VALUE = maxValue

        self.WIN_NAME = cmds.window(title=self.WIN_TITLE, sizeable=False)
        cmds.columnLayout(width=(self.WIN_WIDTH))

        self.TEXT_UI = cmds.text(l=self.WIN_DISPLAY, align="left")
        self.PROGRESS_BAR_UI = cmds.progressBar(maxValue=self.MAX_VALUE, width=(self.WIN_WIDTH))

    def show(self):
        if cmds.window(self.WIN_NAME, q=True, ex=True):
            cmds.showWindow(self.WIN_NAME)
            cmds.window(self.WIN_NAME, e=True, width=self.WIN_WIDTH, height=self.WIN_HEIGHT)

    def hide(self):
        if cmds.window(self.WIN_NAME, q=True, ex=True):
            cmds.window(self.WIN_NAME, edit=True, visible=False)

    def update(self, amount=1, updateText=''):
        """Increases the progress bar display by the given amount"""
        if cmds.window(self.WIN_NAME, q=True, ex=True):
            if cmds.progressBar(self.PROGRESS_BAR_UI, q=True, ex=True):
                self.VALUE += amount
                cmds.progressBar(self.PROGRESS_BAR_UI, edit=True, progress=self.VALUE)
                cmds.text(self.TEXT_UI, e=True, l=('Progress: ' + updateText))
                if self.VALUE >= self.MAX_VALUE:
                    self.hide()

    def reset(self, displayText="Progress:"):
        if cmds.window(self.WIN_NAME, q=True, ex=True):
            if cmds.progressBar(self.PROGRESS_BAR_UI, q=True, ex=True):
                self.WIN_DISPLAY = displayText
                self.VALUE = 0
                cmds.progressBar(self.PROGRESS_BAR_UI, edit=True, progress=self.VALUE)
                cmds.text(self.TEXT_UI, e=True, l=(self.WIN_DISPLAY + " %" + "self.VALUE"))

    def kill(self):
        """Closes the window"""
        if cmds.window(self.WIN_NAME, q=True, ex=True):
            cmds.deleteUI(self.WIN_NAME)
