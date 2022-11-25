import DHI.core.progresswindow as pw

progressWindow = pw.Progress(maxValue=100)

'''
    Progress bar percentage distribution per loading segment.
'''
percentage = {
    'HEAD_CREATE_DERIVED_MESHES': 60,
    'HEAD_BODY_SKIN_WEIGHTS': 10,
    'HEAD_SHADERS': 20,
    'HEAD_JOINTS': 10
}


def update(amount, message):
    progressWindow.update(amount, message)


def hide():
    progressWindow.hide()


def show():
    progressWindow.show()


def reset():
    progressWindow.reset()


def calculateProgressStepValue(numberOfElements, percentageToDistribut):
    return float(percentageToDistribut) / float(numberOfElements)
