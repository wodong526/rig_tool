import os
import sys
from ctypes import *
from DHI.modules.maya.util import MayaUtil


def _initialize_libs(platform):
    '''
    Initialize required libraries based on Maya version
    Returns
    '''

    #print("Importing DHI external libraries")
    from DHI.modules.file.handler import FileHandler

    current = os.path.dirname(os.path.abspath(__file__))

    if current not in sys.path:
        sys.path.append(current)

    python_to_load = resolve_used_python_version()

    lib_folder = FileHandler.joinPath((current, "lib", platform, python_to_load))
    #MayaUtil.logger.info("Fetching libraries from folder %s" % lib_folder)

    if platform == "Linux":
        MayaUtil.logger.info("Setting LD_LIBRARY_PATH to  %s" % lib_folder)
        os.environ["LD_LIBRARY_PATH"] = lib_folder
        try:
            cdll.LoadLibrary(lib_folder + "/libdna.so.7.1.0")
        except Exception as exc:
            MayaUtil.logger.error("Failed to load library:", exc)
            sys.exit(1)

    if lib_folder not in sys.path:
        #MayaUtil.logger.info("Lib folder not on path... Adding")
        sys.path.append(lib_folder)


def resolve_used_python_version():
    from DHI.modules.maya.about import AboutEnv
    about = AboutEnv.getInstance()
    #MayaUtil.logger.info("Running Maya version %s" % about.version)
    python_to_load = 'python2'
    if int(about.version) == 2022:
        python_to_load = 'python3'
    if int(about.version) == 2023:
        python_to_load = 'python397'

    return python_to_load


def _resolve_platform():
    import platform
    platform = platform.system()

    if platform not in ["Windows", "Linux"]:
        platform = "Windows"

    #MayaUtil.logger.info("Running on %s " % platform)
    return platform


def _load_required_plugins():
    try:
        from modules.maya.util import MayaUtil
        from modules.file.handler import FileHandler
        from modules.maya.about import AboutEnv
        import platform
        platform = _resolve_platform()

        current = os.path.dirname(os.path.abspath(__file__))

        about = AboutEnv.getInstance()
        #MayaUtil.logger.info("Running Maya version %s" % about.version)

        rl_plugin_name = "embeddedRL4"
        if platform == "Linux":
            rl_plugin_name = "libembeddedRL4"

        MayaUtil.loadPlugin(rl_plugin_name, FileHandler.joinPath((current, "plugins", platform, about.version)),
                            platform)
        MayaUtil.loadPlugin("MayaUE4RBFPlugin" + about.version,
                            FileHandler.joinPath((current, "plugins", platform, about.version)), platform, ".mll")
        MayaUtil.loadPlugin("MayaUERBFPlugin",
                            FileHandler.joinPath((current, "plugins", platform, about.version)), platform, ".mll")
    except:
        print("Could not load required plugins!")


def load():
    #MayaUtil.logger.info("Preparing paths and loading DHI Plugins")
    platform = _resolve_platform()
    _initialize_libs(platform)
    _load_required_plugins()
