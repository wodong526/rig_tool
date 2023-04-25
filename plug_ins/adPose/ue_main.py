# coding:utf-8

import unreal


def main():
    menus = unreal.ToolMenus.get()
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    if not main_menu:
        print("can not find LevelEditor.MainMenu")
    script_menu = main_menu.add_sub_menu(main_menu.get_name(), "adPose", "adPose", "adPose")

    rbf_bp_entry = unreal.ToolMenuEntry(
        name="adPoseBP",
        type=unreal.MultiBlockType.MENU_ENTRY,
        insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST)
    )
    rbf_bp_entry.set_label("adPoseBP")
    cmd = "import adPoseBP;adPoseBP.create_ad_pose_bp_by_selected()"
    rbf_bp_entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "adPoseBP", cmd)
    script_menu.add_menu_entry("adPoseBP", rbf_bp_entry)
    menus.refresh_all_widgets()


if __name__ == '__main__':
    main()