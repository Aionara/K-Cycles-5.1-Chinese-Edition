import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    FloatVectorProperty,
)
from bpy.types import Panel, UIList
from bpy.utils import register_class, unregister_class
from pathlib import Path
from sys import platform
import os
import subprocess
import tempfile
import stat

def update_kcycles_render_output_camera_mode(self, context):
    camera = context.scene.camera
    scene = context.scene
    scene_render = context.scene.render

    if camera is not None and not bpy.data.cameras[camera.data.name].kcycles_render_output.camera_mode:
        kcycles_render_output = bpy.data.cameras[camera.data.name].kcycles_render_output
        
        kcycles_render_output.resolution_x = scene_render.resolution_x
        kcycles_render_output.resolution_y = scene_render.resolution_y
        kcycles_render_output.resolution_percentage = scene_render.resolution_percentage

        kcycles_render_output.frame_start = scene.frame_start
        kcycles_render_output.frame_end = scene.frame_end

    elif camera is not None and bpy.data.cameras[camera.data.name].kcycles_render_output.camera_mode:
        kcycles_render_output = bpy.data.cameras[camera.data.name].kcycles_render_output

        kcycles_render_output.enable_camera_resolution_updates = False
        kcycles_render_output.resolution_x = scene_render.resolution_x
        kcycles_render_output.resolution_y = scene_render.resolution_y
        kcycles_render_output.resolution_percentage = scene_render.resolution_percentage

        kcycles_render_output.frame_start = scene.frame_start
        kcycles_render_output.frame_end = scene.frame_end

        kcycles_render_output.enable_camera_resolution_updates = True

def update_kcycles_render_output(self, context):
    camera = context.scene.camera
    if camera is not None and bpy.data.cameras[camera.data.name].kcycles_render_output.enable_camera_resolution_updates and bpy.data.cameras[camera.data.name].kcycles_render_output.camera_mode:
        scene = context.scene
        scene_render = context.scene.render
        kcycles_render_output = bpy.data.cameras[camera.data.name].kcycles_render_output

        scene_render.resolution_x = kcycles_render_output.resolution_x
        scene_render.resolution_y = kcycles_render_output.resolution_y
        scene_render.resolution_percentage = kcycles_render_output.resolution_percentage

        scene.frame_start = kcycles_render_output.frame_start
        scene.frame_end = kcycles_render_output.frame_end

class RenderButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

class KCyclesRenderOutputSettings(bpy.types.PropertyGroup):
    camera_mode: BoolProperty(
        name="相机模式渲染输出",
        description="每个相机拥有独立的渲染输出设置",
        default=False,
        update=update_kcycles_render_output_camera_mode,
    )

    resolution_x: IntProperty(
        name="分辨率 X",
        description="渲染图像的水平像素数",
        min=4, max=65536, subtype = 'PIXEL',
        default=1920,
        update=update_kcycles_render_output,
    )

    resolution_y: IntProperty(
        name="分辨率 Y",
        description="渲染图像的垂直像素数",
        min=4, max=65536, subtype = 'PIXEL',
        default=1080,
        update=update_kcycles_render_output,
    )

    resolution_percentage: IntProperty(
        name="分辨率 %",
        description="渲染分辨率的百分比缩放",
        min=1, max=32767, subtype = 'PERCENTAGE',
        default=100,
        update=update_kcycles_render_output,
    )

    frame_start: IntProperty(
        name="起始帧",
        description="播放/渲染范围的第一帧",
        min=0, max=1048574,
        default=1,
        update=update_kcycles_render_output,
    )

    frame_end: IntProperty(
        name="结束帧",
        description="播放/渲染范围的最后一帧",
        min=0, max=1048574,
        default=250,
        update=update_kcycles_render_output,
    )

    enable_camera_resolution_updates: BoolProperty(
        name="启用相机分辨率更新",
        default=True,
    )

class KCyclesRenderCamerasSettings(bpy.types.PropertyGroup):
    file_save: BoolProperty(
        name="渲染文件保存",
        description="保存渲染输出文件",
        default=False,
    )

    file_folder_camera: BoolProperty(
        name="按相机创建渲染文件夹",
        description="为每个相机创建渲染文件夹",
        default=True,
    ) 

    raw_file_folder: BoolProperty(
        name="RAW（无合成器）文件及文件夹",
        description="保存带文件夹的RAW（无合成器）文件",
        default=False,
    )

    raw_compact: BoolProperty(
        name="RAW 紧凑文件大小",
        description="使用有损压缩将RAW文件体积最小化，图像质量影响不明显",
        default=True,
    )
 
    temporal_data: BoolProperty(
        name="添加时序数据",
        description="通过矢量通道添加时序数据",
        default=True,
    )

    file_use_blend_name: BoolProperty(
        name="使用Blend文件名",
        description="使用Blend文件名作为渲染文件名",
        default=False,
    )

    file_increment: BoolProperty(
        name="静帧渲染文件递增",
        description="静帧渲染文件递增编号",
        default=False,
    )

    animation: BoolProperty(
        name="渲染动画",
        description="渲染动画",
        default=False,
    )

    scene_camera_option: bpy.props.EnumProperty(
        name="场景相机",
        description="要渲染的场景相机",
        items=[
            ('ACTIVE', "活动", "渲染活动场景相机"),
            ('SELECTED', "选中", "渲染选中的场景相机"),
            ('ALL', "全部", "渲染所有场景相机"),
        ],
        default='ACTIVE'
    )

    auto_slot: BoolProperty(
        name="自动渲染槽",
        description="新渲染使用下一个图像槽",
        default=False,
    )

    max_slots: IntProperty(
        name="最大渲染槽",
        description="灯光组切换",
        min=8, max=24,
        default=8,
    )

    name_slot: BoolProperty(
        name="命名渲染槽",
        description="用相机名称命名渲染槽",
        default=False,
    )

    background_rendering: BoolProperty(
        name="后台渲染",
        description="启用后台渲染",
        default=False,
    )

class RENDER_PT_kcycles_camera_mode(RenderButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "RENDER_PT_kcycles"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        cscene = context.scene.cycles

        layout.use_property_decorate = True
        layout.use_property_split = False

        row = layout.row(align=False)
        split = row.split(factor = 0.38, align=False)
        split.label(text = "相机模式")
        split.scale_x = 1.15
        split.prop(context.scene, "camera", text="")

    def draw(self, context):
        layout = self.layout

class RENDER_PT_kcycles_camera_resolution(RenderButtonsPanel, Panel):
    bl_label = "分辨率与帧范围"
    bl_parent_id = "RENDER_PT_kcycles_render_cameras"

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        camera = context.scene.camera
        if camera is not None:
            scene = bpy.data.cameras[camera.data.name].kcycles_render_output
            layout.prop(scene, "camera_mode", icon="OUTLINER_DATA_CAMERA", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene_render = context.scene.render
        scene = context.scene       
        camera = context.scene.camera

        if camera is not None and bpy.data.cameras[camera.data.name].kcycles_render_output.camera_mode:
            scene_render = bpy.data.cameras[camera.data.name].kcycles_render_output
            scene = scene_render

        col = layout.column(align=True)
        col.prop(scene_render, "resolution_x", text="分辨率 X")
        col.prop(scene_render, "resolution_y", text="Y")
        col.prop(scene_render, "resolution_percentage", text="%")
        
        col = layout.column(align=True)
        col.prop(scene, "frame_start", text="起始帧")
        col.prop(scene, "frame_end", text="结束")


def next_file_path(path_pattern):
    i = 1

    # First do an exponential search
    while os.path.exists(path_pattern % i):
        i = i * 2

    # Result lies somewhere in the interval (i/2..i]
    # We call this interval (a..b] and narrow it down until a + 1 = b
    a, b = (i // 2, i)
    while a + 1 < b:
        c = (a + b) // 2 # interval midpoint
        a, b = (c, b) if os.path.exists(path_pattern % c) else (a, c)

    return path_pattern % b

def scene_render_filepath(full_path, camera_name):
    scene = bpy.context.scene
    kcycles_render_cameras = scene.kcycles_render_cameras
    blend_name = ""

    if (full_path[:2] ==  "//"):
        directory = os.path.dirname(bpy.data.filepath)
        full_path = str(directory + os.path.sep + full_path[2:])
    elif (full_path[:1] == "/"):
        full_path = str(os.path.sep + full_path[1:])

    if (len(Path(bpy.data.filepath).stem) > 0):
        blend_name = str(Path(bpy.data.filepath).stem + "_") if kcycles_render_cameras.file_use_blend_name else ""

    raw_file = ("Raw" + os.path.sep) if kcycles_render_cameras.raw_file_folder else ""
    if (kcycles_render_cameras.file_folder_camera):
        full_path = str(full_path + camera_name + os.path.sep + raw_file + blend_name + camera_name)
    else:
        full_path = str(full_path + raw_file + blend_name + camera_name)
    
    full_path = bpy.path.abspath(full_path)
    if (kcycles_render_cameras.file_increment and not kcycles_render_cameras.animation):
        full_path = next_file_path(str(full_path + "_0%s" + scene.render.file_extension))
    return (full_path +  str("_" if kcycles_render_cameras.animation else ""))

class RENDER_OT_kcycles_render_slots_reset_name(bpy.types.Operator):
    bl_idname = "kcycles.render_slots_reset_name"
    bl_label = "重置渲染槽名称"
    bl_description = "重置所有渲染槽的名称"

    def execute(self, context):
        image = bpy.data.images['Render Result']

        for i in range(len(image.render_slots)):
            image.render_slots[i].name = str("Slot " + str(i+1))

        return {"FINISHED"}

def scene_render_settings(self, context, set_settings):
    scene = bpy.context.scene
    view_layer = context.view_layer
    kcycles_render_cameras = scene.kcycles_render_cameras

    if (scene.kcycles_render_cameras.file_save and scene.kcycles_render_cameras.raw_file_folder):
        if (set_settings):
            self.scene_use_compositing = scene.render.use_compositing
            self.scene_media_type = scene.render.image_settings.media_type
            self.scene_exr_codec = scene.render.image_settings.exr_codec
            self.scene_color_depth = scene.render.image_settings.color_depth
            scene.render.use_compositing = False
            scene.render.image_settings.media_type = 'MULTI_LAYER_IMAGE'
            scene.render.image_settings.exr_codec = 'DWAA' if scene.kcycles_render_cameras.raw_compact else 'ZIP'
            scene.render.image_settings.color_depth = '16' if scene.kcycles_render_cameras.raw_compact else '32'
            scene.render.image_settings.use_exr_interleave = False
            if (scene.kcycles_render_cameras.temporal_data):
                self.view_layer_use_pass_vector = view_layer.use_pass_vector
                view_layer.use_pass_vector = True
        else:
            scene.render.use_compositing = self.scene_use_compositing
            scene.render.image_settings.media_type = self.scene_media_type
            scene.render.image_settings.exr_codec = self.scene_exr_codec
            scene.render.image_settings.color_depth = self.scene_color_depth
            if (scene.kcycles_render_cameras.temporal_data):
                view_layer.use_pass_vector = self.view_layer_use_pass_vector

class RENDER_OT_kcycles_render_cameras(bpy.types.Operator):
    bl_idname = "kcycles.render_cameras"
    bl_label = "渲染相机"
    bl_description = "渲染场景中的相机"

    camera_list = []
    camera_render_index = 0
    finish_render = False
    rendering = True
    timer_event = None
    active_slot = 0
    scene_path = []
    gallery = True
    render_option : IntProperty(default=0)
    command_line : BoolProperty(default=False)
    scene_use_compositing = False
    scene_media_type = ""
    scene_exr_codec = ""
    scene_color_depth = ""
    view_layer_use_pass_z = False
    view_layer_use_pass_vector = False

    # Rendering callback functions
    def pre_render(self, dummy, thrd = None):
        self.rendering = True

    def post_render(self, dummy, thrd = None):
        scene = bpy.context.scene
        kcycles_render_cameras = scene.kcycles_render_cameras

        if (not kcycles_render_cameras.animation or (kcycles_render_cameras.animation and scene.frame_current == scene.frame_end)):
            self.camera_render_index += 1

        if (self.camera_render_index < len(self.camera_list) or
           (kcycles_render_cameras.animation and scene.frame_current < scene.frame_end)):
            self.rendering = False
        else:
            self.rendering = True
            self.finish_render = True

        if kcycles_render_cameras.auto_slot and self.camera_render_index < len(self.camera_list) and not kcycles_render_cameras.animation:
            image = bpy.data.images['Render Result']
            self.active_slot = image.render_slots.active_index

            if self.camera_render_index > 0 and self.active_slot < (kcycles_render_cameras.max_slots - 1):
                self.active_slot += 1
            else:
                self.active_slot = 0

            if self.active_slot == len(image.render_slots):
                image.render_slots.new()

            image.render_slots.active_index = self.active_slot

    def cancel_render(self, dummy, thrd = None):
        self.finish_render = True

    def execute(self, context):
        scene = context.scene
        self.finish_render = False
        self.rendering = False

        # Check for animation
        scene.kcycles_render_cameras.animation = False if self.render_option ==  0 else True

        # Get the camera list
        if (scene.kcycles_render_cameras.scene_camera_option == "ALL"):
            self.camera_list = [ obj.name for obj in context.visible_objects if obj.type=='CAMERA' and obj.visible_get() == True]
        elif (scene.kcycles_render_cameras.scene_camera_option == "SELECTED"):
            self.camera_list = [ obj.name for obj in context.selected_objects if obj.type=='CAMERA' and obj.visible_get() == True]
        elif (scene.kcycles_render_cameras.scene_camera_option == "ACTIVE" and scene.camera != None):
            self.camera_list = []
            self.camera_list.append(scene.camera.name)
        self.camera_list.sort()

        if (len(self.camera_list) == 0):
            self.finish_render = True
            self.rendering = True

        self.scene_path = scene.render.filepath

        # Command line rendering
        if (self.command_line == True):
            scene_render_settings(self, context, True)
            for camera_name in self.camera_list:
                if camera_name in scene.objects:
                    scene.camera = bpy.data.objects[camera_name]
                    scene.render.filepath = scene_render_filepath(self.scene_path, camera_name)
                    bpy.ops.render.render("INVOKE_DEFAULT", write_still=True, animation=scene.kcycles_render_cameras.animation)
            scene_render_settings(self, context, False)
            return {"FINISHED"}
        elif (scene.kcycles_render_cameras.background_rendering == True):
            # Background rendering
            path = bpy.data.filepath
            python_expr = "import bpy; bpy.ops.kcycles.render_cameras(render_option=" + str(self.render_option) + ", command_line=True)"
            if (not path):
                self.report({'ERROR'}, '请先保存场景再进行后台渲染。')
                return {'CANCELLED'}
            if (not scene.kcycles_render_cameras.file_save):
                self.report({'ERROR'}, "请先在后台渲染前启用'文件保存'属性。")
                return {'CANCELLED'}
            elif bpy.data.is_dirty:
                bpy.ops.wm.save_as_mainfile()
            if os.name == 'nt':
                subprocess.Popen(["start", "cmd", "/k", bpy.app.binary_path, "-b", path, "--python-expr", python_expr], shell=True)
            elif platform == 'darwin':
                shell_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.sh', delete=False)
                python_expr_combined = ' --python-expr ' + '\"' + python_expr + '\"'
                shell_file.write(bpy.app.binary_path + " -b " + path + python_expr_combined)
                shell_file.close()
                os.chmod(shell_file.name, os.stat(shell_file.name).st_mode | stat.S_IEXEC)
                subprocess.call(['open', '-a', 'Terminal.app', shell_file.name])
            elif platform == 'linux':
                found_terminal = False
                possible_terminals = [
                    ('mate-terminal', lambda cmd: ['mate-terminal', '--command=', cmd]),
                    ('konsole', lambda cmd: ['konsole', '-e', cmd]),
                    ('xfce4-terminal', lambda cmd: ['xfce4-terminal', '-e', cmd]),
                    ('xterm', lambda cmd: ['xterm', '-e', cmd]),
                    ('gnome-terminal', lambda cmd: ['gnome-terminal', '--', cmd]),]
                for name, cmdline in possible_terminals:
                    if len(subprocess.run(["command -v " + name], shell=True, capture_output=True).stdout) > 0:
                        found_terminal = True
                        shell_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.sh', delete=False)
                        shell_file.write('#!/bin/bash' + '\n')
                        python_expr_combined = ' --python-expr ' + '\"' + python_expr + '\"'
                        shell_file.write(bpy.app.binary_path + " -b " + path + python_expr_combined)
                        shell_file.write('\n' + 'read -r -p "Press Enter to exit:" key')
                        shell_file.close()
                        os.chmod(shell_file.name, os.stat(shell_file.name).st_mode | stat.S_IEXEC)
                        subprocess.call(cmdline(shell_file.name))
                        break
                if not found_terminal:
                    subprocess.Popen([bpy.app.binary_path, "-b", path , "--python-expr", python_expr])
            
            return {"FINISHED"}

        # Register the render handlers
        bpy.app.handlers.render_pre.append(self.pre_render)
        bpy.app.handlers.render_post.append(self.post_render)
        bpy.app.handlers.render_cancel.append(self.cancel_render)

        # Timer event that runs every half second to check if render camera list needs to be updated
        self.timerEvent = context.window_manager.event_timer_add(0.5, window=context.window)

        # Add the modal handler for running in background
        context.window_manager.modal_handler_add(self)

        image = bpy.data.images['Render Result']
        self.active_slot = image.render_slots.active_index

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        scene = bpy.context.scene
        view_layer = context.view_layer
        kcycles_render_cameras = scene.kcycles_render_cameras

        if event.type == 'TIMER':
            # Finish camera list rendering
            if self.finish_render is True:
                bpy.app.handlers.render_pre.remove(self.pre_render)
                bpy.app.handlers.render_post.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.cancel_render)

                context.window_manager.event_timer_remove(self.timerEvent)
                scene.render.filepath = self.scene_path
                scene_render_settings(self, context, False)

                # bpy.data.images['Render Result'].render_slots.active_index = 0
                # print(bpy.data.images['Render Result'].render_slots[0])
                # bpy.data.images['Render Result'].save_render("c:\\tmp\\Camera.png")
                # print(bpy.data.images['Render Result'].size[0])
                # full_path = bpy.path.abspath(bpy.context.scene.render.filepath)
                # print("full_path: " + full_path)
                # image = bpy.data.images.load(str(full_path + ".png"))
                # print(str(image.size[0]) + " X " + str(image.size[1]))
                # size = image.size
                # pixels = [None] * size[0] * size[1]
                # for x in range(size[0]):
                    # for y in range(size[1]):
                        # # assign RGBA to something useful
                        # r = x / size[0]
                        # g = y / size[1]
                        # b = (1 - r) * g
                        # a = 1.0

                        # pixels[(y * size[0]) + x] = [r, g, b, a]

                # # flatten list
                # pixels = [chan for px in pixels for chan in px]

                # # assign pixels
                # image.pixels = pixels

                # # write image
                # #image.filepath_raw = full_path + ".png"
                # #image.file_format = 'PNG'
                # image.save()
                # bpy.data.images['Render Result'].reload()

                self.report({"INFO"},"K-CYCLES 渲染完成")

                return {"FINISHED"}

            # Render camera
            elif self.rendering == False:
                camera_name = self.camera_list[self.camera_render_index]
                if camera_name in scene.objects:
                    scene.camera = bpy.data.objects[camera_name]
                    scene.render.filepath = scene_render_filepath(self.scene_path, camera_name)
                    scene_render_settings(self, context, True)
                    slot_name = camera_name if kcycles_render_cameras.name_slot else str("Slot " + str(self.active_slot+1))

                    bpy.data.images['Render Result'].render_slots[self.active_slot].name = slot_name
                    bpy.ops.render.render("INVOKE_DEFAULT", write_still=kcycles_render_cameras.file_save, animation=kcycles_render_cameras.animation)

        return {"PASS_THROUGH"}

class RENDER_PT_kcycles_render_cameras(RenderButtonsPanel, Panel):
    bl_label = "渲染相机"
    bl_parent_id = "RENDER_PT_kcycles"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        kcycles_render_cameras = scene.kcycles_render_cameras

        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_x = 0.95
        row.label(text="  ")
        row.operator("kcycles.render_cameras", icon='RENDER_STILL', text="渲染图像").render_option=0
        row.label(text=" ")
        row.operator("kcycles.render_cameras", icon='RENDER_ANIMATION', text="渲染动画").render_option=1
        row.label(text=" ")
        row.prop(kcycles_render_cameras, "background_rendering", text="", icon="EVENT_B")
        row = layout.row(align=True)
        row.scale_x = 0.95
        row.prop(kcycles_render_cameras, "scene_camera_option", expand=True)
    

class RENDER_PT_kcycles_render_cameras_slots(RenderButtonsPanel, Panel):
    bl_label = "渲染槽"
    bl_parent_id = "RENDER_PT_kcycles_render_cameras"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        kcycles_render_cameras = scene.kcycles_render_cameras

        slot = "1"
        if ("Render Result" in bpy.data.images.keys()):
            slot = str(bpy.data.images['Render Result'].render_slots.active_index + 1)

        col = layout.column(align=True, heading="自动槽位 (" + slot + ")")
        col.scale_y = .9
        row = col.row()
        row.prop(kcycles_render_cameras, "auto_slot", text="")
        row.scale_x = 1.5
        sub = row.row()
        sub.prop(kcycles_render_cameras, "max_slots", text="最大槽位", slider=True)

        col = layout.column(align=True, heading="槽位命名")
        col.scale_y = .9
        row = col.row()
        row.prop(kcycles_render_cameras, "name_slot", text="")
        row.scale_x = 1.5
        sub = row.row()
        sub.operator("kcycles.render_slots_reset_name", icon="COLLAPSEMENU", text="重置槽位名称")

class RENDER_PT_kcycles_render_cameras_output(RenderButtonsPanel, Panel):
    bl_label = "输出"
    bl_parent_id = "RENDER_PT_kcycles_render_cameras"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        kcycles_render_cameras = scene.kcycles_render_cameras
        layout.use_property_split = False
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.label(text="")
        row.label(text="保存")
        row.prop(kcycles_render_cameras, "file_save", text="")
        sub = row.row()
        sub.scale_x = 1.2
        sub.prop(scene.render, "filepath", text="")

        layout.use_property_split = False
        row = layout.row(align=False)
        row.label(text="  ")
        row.enabled = kcycles_render_cameras.file_save
        row.scale_x = 5.0
        row.prop(kcycles_render_cameras, "raw_file_folder", text="RAW", toggle=True)
        row.prop(kcycles_render_cameras, "file_folder_camera", text="相机", toggle=True)
        row.prop(kcycles_render_cameras, "file_use_blend_name", text="Blend", toggle=True)
        row.prop(kcycles_render_cameras, "file_increment", text="递增", toggle=True)

        #layout.use_property_split = False
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.enabled = kcycles_render_cameras.file_save and kcycles_render_cameras.raw_file_folder
        row.label(text="    ")
        row.label(text="    ")
        row.label(text="    ")
        row.prop(kcycles_render_cameras, "raw_compact", text="紧凑 RAW")

        row = layout.row(align=True)
        row.alignment = 'LEFT'
        row.enabled = kcycles_render_cameras.file_save and kcycles_render_cameras.raw_file_folder
        row.label(text="    ")
        row.label(text="    ")
        row.label(text="    ")
        row.prop(kcycles_render_cameras, "temporal_data", text="时序数据")

classes = (
    RENDER_OT_kcycles_render_slots_reset_name,
    RENDER_OT_kcycles_render_cameras,
    RENDER_PT_kcycles_render_cameras,
    RENDER_PT_kcycles_render_cameras_slots,
    RENDER_PT_kcycles_render_cameras_output,
    RENDER_PT_kcycles_camera_resolution,
)

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)