from PySide2 import QtWidgets, QtCore, QtGui, QtMultimedia, QtMultimediaWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.OpenMaya as OpenMaya
import json
import os
from shiboken2 import wrapInstance
import subprocess
from maya import mel


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class AnimationStatistics:
    def __init__(self, anim_data):
        self.anim_data = anim_data
        self.keyframe_count = 0
        self.duration = 0
        self.fps = 0
        self.calculate_statistics()

    def calculate_statistics(self):
        all_times = []
        for keyframes in self.anim_data.values():
            if keyframes:
                self.keyframe_count += len(keyframes) // 2
                all_times.extend(keyframes[::2])

        if all_times:
            self.duration = max(all_times) - min(all_times)
            self.fps = self.keyframe_count / self.duration if self.duration > 0 else 0


class AnimationPreviewWidget(QtMultimediaWidgets.QVideoWidget):
    left_clicked = QtCore.Signal(str, str, str)
    right_clicked = QtCore.Signal(QtCore.QPoint, str, str)

    def __init__(self, parent=None):
        super(AnimationPreviewWidget, self).__init__(parent)
        self.mediaPlayer = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self)
        self.mediaPlayer.error.connect(self.handle_error)
        self.mediaPlayer.mediaStatusChanged.connect(self.handle_media_status_changed)
        self.setMouseTracking(True)
        self.info_label = QtWidgets.QLabel(self)
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.7); color: white; padding: 5px;")
        self.info_label.hide()

    def set_video(self, video_path):
        self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(video_path)))
        self.mediaPlayer.pause()

    def play(self):
        self.mediaPlayer.play()

    def pause(self):
        self.mediaPlayer.pause()

    def stop(self):
        self.mediaPlayer.stop()

    def handle_error(self):
        print(f"Media player error: {self.mediaPlayer.errorString()}")

    def handle_media_status_changed(self, status):
        if status == QtMultimedia.QMediaPlayer.LoadedMedia:
            self.update()
        elif status == QtMultimedia.QMediaPlayer.InvalidMedia:
            print("Invalid media")
        elif status == QtMultimedia.QMediaPlayer.NoMedia:
            print("No media set")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.left_clicked.emit(self.anim_name, self.group_name, self.preview_path)
        elif event.button() == QtCore.Qt.RightButton:
            self.right_clicked.emit(event.globalPos(), self.anim_name, self.group_name)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.play()
        self.show_info()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.pause()
        self.info_label.hide()

    def show_info(self):
        duration = self.mediaPlayer.duration()
        fps = self.mediaPlayer.metaData("VideoFrameRate")

        info_parts = []

        if duration is not None and duration > 0:
            info_parts.append(f"Duration: {duration / 1000:.2f} s")

            if fps is not None:
                frame_count = int(duration / 1000 * fps)
                info_parts.append(f"Frames: {frame_count}")
                info_parts.append(f"FPS: {fps:.2f}")
            else:
                info_parts.append("FPS: Unknown")
        else:
            info_parts.append("Video information unavailable")

        info_text = "\n".join(info_parts)
        self.info_label.setText(info_text)
        self.info_label.adjustSize()
        self.info_label.move(5, 5)
        self.info_label.show()


class AnimationDataUI(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(AnimationDataUI, self).__init__(parent)
        self.setWindowTitle("Animation Data Tool By Pitaya37")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        self.file_path = self.load_file_path()
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        self.thumbnail_size = 240
        self.group_boxes = {}
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setup_ui_styles()

    def create_widgets(self):
        self.title_label = QtWidgets.QLabel("Animation Data Tool by Pitaya37")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4A90E2;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3A3A3A, stop:1 #2E2E2E);
            border-bottom: 2px solid #4A90E2;
        """)

        self.start_frame_label = QtWidgets.QLabel('Start Frame:')
        self.start_frame_field = QtWidgets.QSpinBox()
        self.start_frame_field.setRange(0, 10000)

        self.end_frame_label = QtWidgets.QLabel('End Frame:')
        self.end_frame_field = QtWidgets.QSpinBox()
        self.end_frame_field.setRange(0, 10000)

        self.translate_x_slider, self.translate_x_layout, self.translate_x_text = self.create_slider(
            'Translate X Scale')
        self.translate_y_slider, self.translate_y_layout, self.translate_y_text = self.create_slider(
            'Translate Y Scale')
        self.translate_z_slider, self.translate_z_layout, self.translate_z_text = self.create_slider(
            'Translate Z Scale')
        self.rotate_x_slider, self.rotate_x_layout, self.rotate_x_text = self.create_slider('Rotate X Scale')
        self.rotate_y_slider, self.rotate_y_layout, self.rotate_y_text = self.create_slider('Rotate Y Scale')
        self.rotate_z_slider, self.rotate_z_layout, self.rotate_z_text = self.create_slider('Rotate Z Scale')

        self.group_name_field = QtWidgets.QLineEdit()
        self.animation_name_field = QtWidgets.QLineEdit()
        self.save_button = QtWidgets.QPushButton("Save Animation Data")
        self.load_button = QtWidgets.QPushButton("Load Animation Data")
        self.tab_widget = QtWidgets.QTabWidget()
        self.change_path_button = QtWidgets.QPushButton("Change Save Path")

        self.stats_label = QtWidgets.QLabel()
        self.stats_label.setAlignment(QtCore.Qt.AlignCenter)
        self.stats_label.setStyleSheet("font-weight: bold; color: #4A90E2;")

    def create_slider(self, label):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(10000)
        slider.setValue(1000)
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        slider.setTickInterval(1000)

        value_display = QtWidgets.QLineEdit("1.00")
        value_display.setFixedWidth(50)
        value_display.setAlignment(QtCore.Qt.AlignCenter)

        def update_value(value):
            if value <= 1000:
                display_value = value / 1000.0
            else:
                display_value = (value - 1000) / 100.0 + 1
            value_display.setText(f"{display_value:.2f}")

        def set_slider_from_input():
            try:
                input_value = float(value_display.text())
                if 0 <= input_value <= 100:
                    if input_value <= 1:
                        slider_value = int(input_value * 1000)
                    else:
                        slider_value = int((input_value - 1) * 100 + 1000)
                    slider.setValue(slider_value)
            except ValueError:
                pass

        slider.valueChanged.connect(update_value)
        value_display.editingFinished.connect(set_slider_from_input)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(label))
        layout.addWidget(slider)
        layout.addWidget(value_display)

        return slider, layout, value_display

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.title_label)

        top_layout = QtWidgets.QHBoxLayout()

        left_layout = QtWidgets.QVBoxLayout()
        frame_group = QtWidgets.QGroupBox("Frame Range")
        frame_layout = QtWidgets.QGridLayout(frame_group)
        frame_layout.addWidget(self.start_frame_label, 0, 0)
        frame_layout.addWidget(self.start_frame_field, 0, 1)
        frame_layout.addWidget(self.end_frame_label, 1, 0)
        frame_layout.addWidget(self.end_frame_field, 1, 1)
        left_layout.addWidget(frame_group)

        scale_group = QtWidgets.QGroupBox("Scale Animation Data")
        scale_layout = QtWidgets.QVBoxLayout(scale_group)
        scale_layout.addLayout(self.translate_x_layout)
        scale_layout.addLayout(self.translate_y_layout)
        scale_layout.addLayout(self.translate_z_layout)
        scale_layout.addLayout(self.rotate_x_layout)
        scale_layout.addLayout(self.rotate_y_layout)
        scale_layout.addLayout(self.rotate_z_layout)
        left_layout.addWidget(scale_group)

        top_layout.addLayout(left_layout)

        right_layout = QtWidgets.QVBoxLayout()
        save_group = QtWidgets.QGroupBox("Save Animation")
        save_layout = QtWidgets.QFormLayout(save_group)
        save_layout.addRow('Group Name:', self.group_name_field)
        save_layout.addRow('Animation Name:', self.animation_name_field)
        save_layout.addRow(self.save_button)
        save_layout.addRow(self.change_path_button)
        right_layout.addWidget(save_group)
        right_layout.addStretch()

        top_layout.addLayout(right_layout)

        main_layout.addLayout(top_layout)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line)

        main_layout.addWidget(self.stats_label)

        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.load_button)

        top_layout.setStretchFactor(left_layout, 2)
        top_layout.setStretchFactor(right_layout, 1)

    def create_connections(self):
        self.save_button.clicked.connect(self.save_animation)
        self.load_button.clicked.connect(self.load_animation_panel)
        self.translate_x_slider.valueChanged.connect(lambda value: self.update_text(self.translate_x_text, value))
        self.translate_y_slider.valueChanged.connect(lambda value: self.update_text(self.translate_y_text, value))
        self.translate_z_slider.valueChanged.connect(lambda value: self.update_text(self.translate_z_text, value))
        self.rotate_x_slider.valueChanged.connect(lambda value: self.update_text(self.rotate_x_text, value))
        self.rotate_y_slider.valueChanged.connect(lambda value: self.update_text(self.rotate_y_text, value))
        self.rotate_z_slider.valueChanged.connect(lambda value: self.update_text(self.rotate_z_text, value))
        self.change_path_button.clicked.connect(self.change_save_path)
        self.tab_widget.tabBar().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tab_widget.tabBar().customContextMenuRequested.connect(self.show_tab_context_menu)

    def update_text(self, text_widget, value):
        if value <= 1000:
            display_value = value / 1000.0
        else:
            display_value = (value - 1000) / 100.0 + 1
        text_widget.setText(f"{display_value:.2f}")

    def change_save_path(self):
        new_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", self.file_path)
        if new_path:
            self.file_path = new_path
            self.save_file_path()
            self.load_animation_panel()
            QtWidgets.QMessageBox.information(self, "Path Changed", f"New save path:\n{new_path}")

    def load_file_path(self):
        settings = QtCore.QSettings("YourCompany", "AnimationDataTool")
        return settings.value("file_path", os.path.expanduser("~/Documents/maya/animations"))

    def create_or_update_anim_info(self, anim_folder):
        anim_file = os.path.join(anim_folder, "animation.json")
        anim_info_path = os.path.join(anim_folder, "anim_info.json")

        if os.path.exists(anim_file):
            try:
                with open(anim_file, "r") as f:
                    anim_data = json.load(f)

                all_times = []
                for keyframes in anim_data.values():
                    if keyframes:
                        all_times.extend(keyframes[::2])

                if all_times:
                    start_frame = min(all_times)
                    end_frame = max(all_times)
                    frame_count = max(1, int(end_frame - start_frame) + 1)  # 确保至少有1帧
                    # get current time unit
                    time_unit = cmds.currentUnit(q=1, t=1)

                    # get the index in the list defined for the settings windows
                    index = mel.eval(f'getIndexFromCurrentUnitCmdValue("{time_unit}")') - 1

                    # get the ui name for the tiem unit (something fps)
                    fps_name = mel.eval(f'getTimeUnitDisplayString({index});')

                    # if you want the number now you can process the name since it will be consistent
                    fps = float(fps_name.split(' ')[0])

                    print(fps)
                    if fps <= 0:
                        print(f"Warning: Invalid FPS ({fps}) for {anim_folder}. Using default 30 fps.")
                        fps = 30

                    duration = max((end_frame - start_frame) / fps, 1 / fps)  # 最小持续时间为1帧

                    anim_info = {
                        "frame_count": frame_count,
                        "fps": fps,
                        "duration": duration
                    }

                    with open(anim_info_path, "w") as f:
                        json.dump(anim_info, f)

                    return anim_info
                else:
                    print(f"Warning: No keyframe data found in {anim_file}")
            except Exception as e:
                print(f"Error processing animation in {anim_folder}: {str(e)}")
        else:
            print(f"Animation file not found: {anim_file}")

        return None

    def save_file_path(self):
        settings = QtCore.QSettings("YourCompany", "AnimationDataTool")
        settings.setValue("file_path", self.file_path)

    def save_animation(self):
        start_frame = self.start_frame_field.value()
        end_frame = self.end_frame_field.value()
        group_name = self.group_name_field.text()
        anim_name = self.animation_name_field.text()
        group_folder = os.path.join(self.file_path, group_name)
        anim_folder = os.path.join(group_folder, anim_name)
        if not os.path.exists(anim_folder):
            os.makedirs(anim_folder)

        ctrl_list = cmds.ls(selection=True, long=True)
        anim_data = {}
        for ctrl in ctrl_list:
            all_attrs = cmds.listAttr(ctrl)
            cb_attrs = cmds.listAnimatable(ctrl)
            ordered_attrs = [attr for attr in all_attrs for cb in cb_attrs if cb.endswith(attr)]
            for attr in ordered_attrs:
                keyframe_info = cmds.keyframe(ctrl, attribute=attr, query=True, time=(start_frame, end_frame),
                                              timeChange=True, valueChange=True)
                anim_data[ctrl + "." + attr] = keyframe_info
        with open(os.path.join(anim_folder, "animation.json"), "w") as f:
            json.dump(anim_data, f)

        stats = AnimationStatistics(anim_data)
        self.update_stats_display(stats)

        preview_path = os.path.join(anim_folder, f"{anim_name}_preview.mp4")
        actual_preview_path = self.create_animation_preview(preview_path, start_frame, end_frame)

        self.create_thumbnail_button(group_name, anim_name, actual_preview_path)
        cmds.confirmDialog(title="Save Successful", message="Animation data and preview have been saved.",
                           button=["OK"])
        frame_count = max(1, end_frame - start_frame + 1)  # Ensure at least 1 frame
        # get current time unit
        time_unit = cmds.currentUnit(q=1, t=1)

        # get the index in the list defined for the settings windows
        index = mel.eval(f'getIndexFromCurrentUnitCmdValue("{time_unit}")') - 1

        # get the ui name for the tiem unit (something fps)
        fps_name = mel.eval(f'getTimeUnitDisplayString({index});')

        # if you want the number now you can process the name since it will be consistent
        fps = float(fps_name.split(' ')[0])
        print(fps)
        duration = frame_count / fps if fps > 0 else 0  # Avoid division by zero

        # Save animation info
        anim_info = {
            "frame_count": frame_count,
            "fps": fps,
            "duration": duration
        }
        anim_info_path = os.path.join(anim_folder, "anim_info.json")
        with open(anim_info_path, "w") as f:
            json.dump(anim_info, f)

    def update_stats_display(self, stats):
        stats_text = f"Keyframes: {stats.keyframe_count} | Duration: {stats.duration:.2f}s | FPS: {stats.fps:.2f}"
        self.stats_label.setText(stats_text)

    def create_animation_preview(self, preview_path, start_frame, end_frame):
        current_frame = cmds.currentTime(query=True)

        try:
            max_frames = 150
            if end_frame - start_frame > max_frames:
                end_frame = start_frame + max_frames

            temp_avi = preview_path.rsplit('.', 1)[0] + '.avi'

            view = omui.M3dView.active3dView()
            width = view.portWidth()
            height = view.portHeight()

            cmds.playblast(
                filename=temp_avi,
                forceOverwrite=True,
                format="avi",
                sequenceTime=0,
                clearCache=1,
                viewer=0,
                showOrnaments=0,
                framePadding=4,
                percent=50,
                compression="none",
                quality=70,
                widthHeight=[width // 2, height // 2],
                startTime=start_frame,
                endTime=end_frame,
                offScreen=True
            )

            ffmpeg_command = [
                'ffmpeg', '-i', temp_avi,
                '-c:v', 'libx264',
                '-preset', 'slow',
                '-crf', '18',
                '-vf', 'fps=30',
                '-y',
                preview_path
            ]

            subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
            print(f"Successfully created MP4: {preview_path}")
            os.remove(temp_avi)
            return preview_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
        except FileNotFoundError:
            print("FFmpeg not found. Please ensure it's installed and in your system PATH.")
        except Exception as e:
            print(f"Error during video conversion: {str(e)}")

        print("Using AVI file as fallback.")
        return temp_avi

    def create_thumbnail_button(self, group_name, anim_name, preview_path):
        if not os.path.exists(preview_path):
            print(f"Preview file not found: {preview_path}")
            return

        video_widget = AnimationPreviewWidget(self)
        video_widget.setFixedSize(self.thumbnail_size, self.thumbnail_size * 3 // 4)
        video_widget.set_video(preview_path)

        video_widget.anim_name = anim_name
        video_widget.group_name = group_name
        video_widget.preview_path = preview_path

        video_widget.left_clicked.connect(self.show_preview)
        video_widget.right_clicked.connect(self.show_context_menu)

        name_label = QtWidgets.QLabel(anim_name)
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold;")

        container = QtWidgets.QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #3A3A3A;
                border-radius: 5px;
            }
            QWidget:hover {
                background-color: #4A4A4A;
            }
        """)

        vbox = QtWidgets.QVBoxLayout(container)
        vbox.setContentsMargins(5, 5, 5, 5)
        vbox.setSpacing(5)
        vbox.addWidget(video_widget)
        vbox.addWidget(name_label)

        if group_name not in self.group_boxes:
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            container_widget = QtWidgets.QWidget()
            scroll_area.setWidget(container_widget)
            layout = QtWidgets.QGridLayout(container_widget)
            layout.setSpacing(10)
            self.tab_widget.addTab(scroll_area, group_name)
            self.group_boxes[group_name] = layout

        # 加载动画信息
        anim_folder = os.path.dirname(preview_path)
        anim_info_path = os.path.join(anim_folder, "anim_info.json")

        if not os.path.exists(anim_info_path):
            print(f"Warning: anim_info.json not found for {group_name}/{anim_name}")
            anim_info = self.create_or_update_anim_info(anim_folder)
        else:
            with open(anim_info_path, "r") as f:
                anim_info = json.load(f)

        if anim_info:
            info_label = QtWidgets.QLabel(f"Frames: {anim_info['frame_count']} | FPS: {anim_info['fps']:.2f}")
        else:
            info_label = QtWidgets.QLabel("Frame and FPS information not available")

        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 10px; color: #AAAAAA;")

        vbox.addWidget(info_label)

        if group_name not in self.group_boxes:
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            container_widget = QtWidgets.QWidget()
            scroll_area.setWidget(container_widget)
            layout = QtWidgets.QGridLayout(container_widget)
            layout.setSpacing(10)
            self.tab_widget.addTab(scroll_area, group_name)
            self.group_boxes[group_name] = layout

        layout = self.group_boxes[group_name]
        count = layout.count()
        row = count // 4
        column = count % 4
        layout.addWidget(container, row, column, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)  # 添加对齐方式

    def show_preview(self, anim_name, group_name, preview_path):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Animation Preview")
        dialog.setModal(True)

        layout = QtWidgets.QVBoxLayout(dialog)

        video_widget = AnimationPreviewWidget(dialog)
        video_widget.setFixedSize(720, 540)  # 增加预览窗口大小
        video_widget.set_video(preview_path)
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Animation Preview")
        dialog.setModal(True)

        layout = QtWidgets.QVBoxLayout(dialog)

        video_widget = AnimationPreviewWidget(dialog)
        video_widget.setFixedSize(480, 360)
        video_widget.set_video(preview_path)

        layout.addWidget(video_widget)

        button_layout = QtWidgets.QHBoxLayout()
        load_button = QtWidgets.QPushButton("Load Animation")
        cancel_button = QtWidgets.QPushButton("Cancel")
        button_layout.addWidget(load_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        load_button.clicked.connect(lambda: self.load_and_close(dialog, group_name, anim_name))
        cancel_button.clicked.connect(dialog.reject)

        video_widget.play()
        dialog.exec_()
        video_widget.stop()

    def load_and_close(self, dialog, group_name, anim_name):
        self.load_animation(group_name, anim_name)
        dialog.accept()

    def load_animation(self, group_name, anim_name):
        anim_folder = os.path.join(self.file_path, group_name, anim_name)
        anim_file = os.path.join(anim_folder, "animation.json")

        if not os.path.exists(anim_file):
            cmds.warning("Animation file does not exist: {}".format(anim_file))
            return

        with open(anim_file, "r") as f:
            anim_data = json.load(f)

        scale_translate_x = self.get_slider_value(self.translate_x_slider)
        scale_translate_y = self.get_slider_value(self.translate_y_slider)
        scale_translate_z = self.get_slider_value(self.translate_z_slider)
        scale_rotate_x = self.get_slider_value(self.rotate_x_slider)
        scale_rotate_y = self.get_slider_value(self.rotate_y_slider)
        scale_rotate_z = self.get_slider_value(self.rotate_z_slider)

        current_frame = cmds.currentTime(query=True)

        start_frame = min(keyframes[0] for keyframes in anim_data.values() if keyframes)

        for ctrl_attr, keyframes in anim_data.items():
            if not keyframes:
                cmds.warning(f"No keyframes found for {ctrl_attr}, skipping.")
                continue

            ctrl, attr = ctrl_attr.rsplit('.', 1)
            ctrl_name = ctrl.split('|')[-1]
            matching_ctrls = cmds.ls(ctrl_name)

            if not matching_ctrls:
                cmds.warning(f"No matching controllers found for {ctrl_name}, skipping.")
                continue

            for ctrl_match in matching_ctrls:
                for i in range(0, len(keyframes), 2):
                    time = keyframes[i] - start_frame + current_frame
                    value = keyframes[i + 1]

                    if 'translateX' in attr:
                        value *= scale_translate_x
                    elif 'translateY' in attr:
                        value *= scale_translate_y
                    elif 'translateZ' in attr:
                        value *= scale_translate_z
                    elif 'rotateX' in attr:
                        value *= scale_rotate_x
                    elif 'rotateY' in attr:
                        value *= scale_rotate_y
                    elif 'rotateZ' in attr:
                        value *= scale_rotate_z

                    try:
                        cmds.setKeyframe(ctrl_match, attribute=attr, time=(time, time), value=value)
                    except RuntimeError as e:
                        cmds.warning(f"Failed to set keyframe for {ctrl_match}.{attr} at time {time}, skipping.")
                        continue

        cmds.currentTime(current_frame)
        cmds.refresh()

        stats = AnimationStatistics(anim_data)
        self.update_stats_display(stats)

    def get_slider_value(self, slider):
        value = slider.value()
        if value <= 1000:
            return value / 1000.0
        else:
            return (value - 1000) / 100.0 + 1

    def show_context_menu(self, pos, anim_name, group_name):
        context_menu = QtWidgets.QMenu(self)
        delete_action = context_menu.addAction("删除动画和缩略图")
        action = context_menu.exec_(pos)
        if action == delete_action:
            self.delete_animation(group_name, anim_name)

    def delete_animation(self, group_name, anim_name):
        reply = QtWidgets.QMessageBox.question(self, '确认删除',
                                               f"确定要删除 {group_name}/{anim_name} 吗？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            anim_folder = os.path.join(self.file_path, group_name, anim_name)
            try:
                for root, dirs, files in os.walk(anim_folder, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(anim_folder)
                self.load_animation_panel()
                QtWidgets.QMessageBox.information(self, "删除成功", f"{group_name}/{anim_name} 已成功删除。")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "删除失败", f"删除 {group_name}/{anim_name} 时发生错误：{str(e)}")

    def show_tab_context_menu(self, pos):
        index = self.tab_widget.tabBar().tabAt(pos)
        if index != -1:
            group_name = self.tab_widget.tabText(index)
            context_menu = QtWidgets.QMenu(self)
            delete_all_action = context_menu.addAction("删除所有动画和缩略图")
            action = context_menu.exec_(self.tab_widget.tabBar().mapToGlobal(pos))
            if action == delete_all_action:
                self.delete_all_animations(group_name)

    def delete_all_animations(self, group_name):
        reply = QtWidgets.QMessageBox.question(self, '确认删除',
                                               f"确定要删除 {group_name} 中的所有动画和缩略图吗？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            group_folder = os.path.join(self.file_path, group_name)
            try:
                for root, dirs, files in os.walk(group_folder, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(group_folder)
                self.load_animation_panel()
                QtWidgets.QMessageBox.information(self, "删除成功", f"{group_name} 中的所有动画和缩略图已成功删除。")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "删除失败", f"删除 {group_name} 中的内容时发生错误：{str(e)}")

    def setup_ui_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #F0F0F0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #5CACEE, stop: 1 #4A90E2);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #6CBAFF, stop: 1 #5AA0F2);
            }
            QLineEdit {
                background-color: #3A3A3A;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4A90E2, stop:1 #5AA0F2);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)

    def load_animation_panel(self):
        self.tab_widget.clear()
        self.group_boxes.clear()

        if not os.path.exists(self.file_path):
            print(f"Directory not found: {self.file_path}")
            return

        anim_groups = [f for f in os.listdir(self.file_path) if os.path.isdir(os.path.join(self.file_path, f))]

        for anim_group in anim_groups:
            group_path = os.path.join(self.file_path, anim_group)
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            container_widget = QtWidgets.QWidget()
            scroll_area.setWidget(container_widget)
            layout = QtWidgets.QGridLayout(container_widget)
            self.tab_widget.addTab(scroll_area, anim_group)
            self.group_boxes[anim_group] = layout

            animation_folders = [f for f in os.listdir(group_path) if os.path.isdir(os.path.join(group_path, f))]
            for anim_folder in animation_folders:
                anim_path = os.path.join(group_path, anim_folder)

                try:
                    anim_info = self.create_or_update_anim_info(anim_path)
                    if anim_info is None:
                        print(f"Failed to create or update anim_info for {anim_group}/{anim_folder}")
                        continue

                    mp4_path = os.path.join(anim_path, f"{anim_folder}_preview.mp4")
                    avi_path = os.path.join(anim_path, f"{anim_folder}_preview.avi")

                    if os.path.exists(mp4_path):
                        preview_path = mp4_path
                    elif os.path.exists(avi_path):
                        preview_path = avi_path
                    else:
                        print(f"No preview found for {anim_group}/{anim_folder}")
                        continue

                    print(f"Loading preview: {preview_path}")
                    self.create_thumbnail_button(anim_group, anim_folder, preview_path)
                except Exception as e:
                    print(f"Error loading animation {anim_group}/{anim_folder}: {str(e)}")
                    continue  # 跳过这个动画，继续处理下一个

        QtCore.QTimer.singleShot(100, self.update_ui)

    def update_ui(self):
        for i in range(self.tab_widget.count()):
            scroll_area = self.tab_widget.widget(i)
            scroll_area.widget().update()


def run():
    global animation_data_ui
    try:
        animation_data_ui.close()
        animation_data_ui.deleteLater()
    except:
        pass

    animation_data_ui = AnimationDataUI()
    animation_data_ui.show()


if __name__ == "__main__":
    run()