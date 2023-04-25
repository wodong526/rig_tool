import os
import sys
from DHI.modules.maya.util import MayaUtil


def _initializeLibs(platform):
    '''
    Initialize required libraries based on Maya version
    Returns
    '''

    #print ("Importing DHI external libraries")
    from DHI.modules.file.handler import FileHandler
    from DHI.modules.maya.about import AboutEnv
    about = AboutEnv.getInstance()
    #MayaUtil.logger.info("Running Maya version %s" % about.version)

    current = os.path.dirname(os.path.abspath(__file__))

    if current not in sys.path:
        sys.path.append(current)

    python_to_load = 'python2'
    if int(about.version) >= 2022:
        python_to_load = 'python3'

    lib_folder = FileHandler.joinPath((current, "lib", platform, python_to_load))
    #MayaUtil.logger.info("Fetching libraries from folder %s" % lib_folder)

    if platform == "Linux":
        os.environ["LD_LIBRARY_PATH"] = lib_folder

    if lib_folder not in sys.path:
        sys.path.append(lib_folder)

    #print(sys.path)


def _resolvePlatform():
    import platform
    platform = platform.system()

    if platform not in ["Windows", "Linux"]:
        platform = "Windows"

    #MayaUtil.logger.info("Running on %s " % platform)
    return platform


def _loadRequiredPlugins():
    try:
        from modules.maya.util import MayaUtil
        from modules.file.handler import FileHandler
        from modules.maya.about import AboutEnv
        import platform
        platform = _resolvePlatform()

        current = os.path.dirname(os.path.abspath(__file__))

        about = AboutEnv.getInstance()
        #MayaUtil.logger.info("Running Maya version %s" % about.version)

        rlPluginName = "embeddedRL4"
        if platform == "Linux":
            rlPluginName = "libembeddedRL4"

        MayaUtil.loadPlugin(rlPluginName, FileHandler.joinPath((current, "plugins", platform, about.version)), platform)
        MayaUtil.loadPlugin("MayaUE4RBFPlugin" + about.version,
                            FileHandler.joinPath((current, "plugins", platform, about.version)), platform, ".mll")
        MayaUtil.loadPlugin("MayaUERBFPlugin",
                            FileHandler.joinPath((current, "plugins", platform, about.version)), platform, ".mll")
    except:
        print("Could not load required plugins!")


def load():
    #MayaUtil.logger.info("Preparing paths and loading DHI Plugins")
    platform = _resolvePlatform()
    _initializeLibs(platform)
    _loadRequiredPlugins()
