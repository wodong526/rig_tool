# coding=utf-8
from general_ui import *
from config import ConfigTool
from targets import TargetEditTool
from grid import UVPoseTool
from facs_ui import FaceTargetEditTool
import ocd
import bs
import sdr
import ADPose
import joints


class ADPoseTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_host_app())
        self.setObjectName("UVPoseTool")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 2, 0, 0)
        try:
            layout.setMargin(5)
        except AttributeError:
            pass
        self.setLayout(layout)
        self.config = ConfigTool(self)
        menu_bar = QMenuBar()
        layout.setMenuBar(menu_bar)

        self.list = TargetEditTool(self)
        self.face = FaceTargetEditTool(self)
        self.grid = UVPoseTool()
        self.tab = QTabWidget(self)
        layout.addWidget(self.tab)
        self.tab.addTab(self.list, u"列表")
        self.tab.addTab(self.grid, u"网格")
        self.tab.addTab(self.face, u"表情")
        self.setBaseSize(10, 10)
        self.tab.currentChanged.connect(self.grid.reload)
        self.tab.currentChanged.connect(self.list.list.reload)
        self.tab.currentChanged.connect(self.face.list.reload)

        self.bake_ocd = ocd.BakeOcd(self)
        self.bake_deform = ocd.BakeDeform(self)
        self.sdr_driver = sdr.SdrJointDriver(self)
        self.sdr_ani = sdr.SdrJointAnim(self)
        tool_menu = menu_bar.addMenu(u"工具")
        tool_menu.addAction(u"配置", self.config.showNormal)
        tool_menu.addAction(u"检查镜像", bs.check_mirror)
        tool_menu.addAction(u"清理orig", ocd.clear_orig)
        tool_menu.addAction(u"冻结骨骼旋转值", ADPose.free_joints)

        ocd_menu = menu_bar.addMenu(u"ocd")
        ocd_menu.addAction(u"创建ocd", ocd.create_ocd)
        ocd_menu.addAction(u"根据蒙皮创建ocd", ocd.create_ocd_by_skin)
        ocd_menu.addAction(u"烘焙修型", self.bake_deform.show)
        ocd_menu.addAction(u"烘焙ocd", self.bake_ocd.show)

        sdr_menu = menu_bar.addMenu(u"sdr")
        sdr_menu.addAction(u"修型转骨骼", self.sdr_driver.showNormal)
        sdr_menu.addAction(u"镜像骨骼驱动", sdr.mirror_sdr_joints)
        sdr_menu.addAction(u"自动key帧", sdr.auto_key)
        sdr_menu.addAction(u"转成骨骼动画", self.sdr_ani.showNormal)
        sdr_menu.addAction(u"转为骨骼驱动", sdr.plane_sdk)
        # sdr_menu.addAction(u"修复骨骼驱动", sdr.re_plane_sdk)

        sdr_menu.addAction(u"导出到unity", sdr.export_to_unity_ui)
        sdr_menu.addAction(u"导出Pose", sdr.export_pose_data_ui)
        sdr_menu.addAction(u"导出修型模型", sdr.import_pose_data_ui)

        self.create_joint_tool = joints.CreateJointTool(self)
        joints_menu = menu_bar.addMenu(u"骨骼")
        joints_menu.addAction(u"创建骨骼", self.create_joint_tool.showNormal)
        joints_menu.addAction(u"镜像骨骼", joints.mirror_joints)
        joints_menu.addAction(u"创建驱动", joints.create_plane_by_selected)


window = None


def show():
    global window
    if window is None:
        window = ADPoseTool()
    window.show()


def show_in_maya():
    global window
    if int(str(pm.about(api=True))[:4]) > 2017:
        while pm.control("uvPoseTool_dock", query=True, exists=True):
            pm.deleteUI("uvPoseTool_dock")
        while pm.control("UVPoseTool", query=True, exists=True):
            pm.deleteUI("UVPoseTool")
        dock = pm.mel.getUIComponentDockControl("Channel Box / Layer Editor", False)
        pm.workspaceControl("uvPoseTool_dock", ttc=(dock, -1), r=1, l=u"UVPoseTool", retain=True)
        window = ADPoseTool()
        pm.control(window.objectName(), e=1, p="uvPoseTool_dock")
    else:
        if window is None:
            if pm.dockControl("uvPoseTool_dock", ex=1):
                pm.deleteUI("uvPoseTool_dock")
            window = ADPoseTool()
            pm.dockControl("uvPoseTool_dock", area='right', content="UVPoseTool",
                           allowedArea=['right', 'left'], l=u"UVPose")
        pm.dockControl("uvPoseTool_dock", e=1, vis=0)
        pm.dockControl("uvPoseTool_dock", e=1, vis=1)


