import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    FloatVectorProperty,
    PointerProperty,
)
from bpy.types import Panel, UIList
from bpy.utils import register_class, unregister_class
from pathlib import Path
from sys import platform
import os
import subprocess
import tempfile
import stat

file_path_error = ""
temporal_error = ""
update_subdirectory_item = True

def get_node_id(nodes, id_name):
    node_id = []
    for node in nodes:
        if node.bl_idname == id_name:
            node_id = node
    return node_id

def update_playback_mode(self, context):
    camera = bpy.context.scene.camera
    scene = bpy.context.scene
    kcycles_playback = scene.kcycles_playback

    bpy.ops.kcycles.playback_load(load_subdirectory=True)
    update_use_kc_temporal(self, context)
    update_use_vector_blur(self, context)

def update_subdirectory(self, context):
    if update_subdirectory_item:
        bpy.ops.kcycles.playback_load(load_subdirectory=True)
        update_use_kc_temporal(self, context)
        update_use_vector_blur(self, context)

def update_animation_path(self, context):
    camera = bpy.context.scene.camera
    scene = bpy.context.scene
    kcycles_playback = scene.kcycles_playback

    bpy.ops.kcycles.playback_load()
    update_use_kc_temporal(self, context)
    update_use_vector_blur(self, context)

def update_image_file(self, context):
    camera = bpy.context.scene.camera
    scene = bpy.context.scene
    kcycles_playback = scene.kcycles_playback

    bpy.ops.kcycles.playback_load()
    update_use_kc_temporal(self, context)

def update_apply_timeline(self, context):
    camera = bpy.context.scene.camera
    scene = bpy.context.scene
    kcycles_playback = scene.kcycles_playback

    if (kcycles_playback.playback_mode == "ANIMATION"):
        node_group = context.scene.compositing_node_group
        nodes_kc_playback = node_group.nodes["KC_Playback"].node_tree.nodes

        scene.frame_current = nodes_kc_playback["KC_Play"].frame_start
        scene.frame_start = nodes_kc_playback["KC_Play"].frame_start
        scene.frame_end = nodes_kc_playback["KC_Play"].frame_start + nodes_kc_playback["KC_Play"].frame_duration - 1

def update_change_camera_from_path(self, context):
    camera = bpy.context.scene.camera
    scene = bpy.context.scene
    kcycles_playback = scene.kcycles_playback

    if (kcycles_playback.change_camera_from_path and kcycles_playback.animation_path != "" and "(None)" not in kcycles_playback.subdirectory_list):
        camera_list = [ obj.name for obj in context.visible_objects if obj.type=='CAMERA' and obj.visible_get() == True]
        subdirectory_path = kcycles_playback.subdirectory_list
        path_name = kcycles_playback.animation_path if "(None)" in subdirectory_path else subdirectory_path
        for camera_name in camera_list:
            if camera_name in path_name:
                scene.camera = bpy.data.objects[camera_name]
                break

def get_image_files(image_folder_path):
    image_files = list()
    valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tga", ".exr", ".tif", ".tiff", ".gif", ".webp"}
    for file_name in os.listdir(image_folder_path):
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()
        if ext in valid_extensions:
            image_files.append(file_name)
    image_files.sort()

    return image_files

def get_number_from_filename_end(filepath):
    # Extracts a number from the end of a filename (before the extension).
    filename_without_ext, _ = os.path.splitext(filepath)
    
    # Find the last sequence of digits
    number_str = ""
    for char in reversed(filename_without_ext):
        if char.isdigit():
            number_str = char + number_str
        else:
            # Stop when a non-digit character is encountered
            break

    if number_str:
        return int(number_str)
    else:
        return None

def get_subdirs_with_files(root_dir):
    valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tga", ".exr", ".tif", ".tiff", ".gif", ".webp"}
    found_subdirs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Check if any of the target files exist in the current directory's files
        for file_name in filenames:
            _, ext = os.path.splitext(file_name)
            ext = ext.lower()
            if ext in valid_extensions:
                relative_path = os.path.relpath(dirpath, root_dir)
                #if relative_path != '.':
                found_subdirs.append(relative_path)
                break
    return found_subdirs

def append_kcycles_node(node_name):
    path = os.path.join(bpy.utils.resource_path('LOCAL'), "datafiles", "kcycles")
    blendfile = "kcycles_assets.blend"
    filepath = path + os.path.sep + blendfile

    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.node_groups = [node_name]

class RENDER_OT_kcycles_playback_load(bpy.types.Operator):
    bl_idname = "kcycles.playback_load"
    bl_label = "播放加载"
    bl_description = "加载图像或图像序列"

    load_subdirectory : BoolProperty(default=False)

    def execute(self, context):
        scene = context.scene
        kcycles_playback = scene.kcycles_playback
        node_group = context.scene.compositing_node_group
        nodes_kc_playback = node_group.nodes["KC_Playback"].node_tree.nodes
        global file_path_error
        global temporal_error
        global update_subdirectory_item

        # Check for animation
        load_image = True if kcycles_playback.playback_mode == "IMAGE" else False

        if kcycles_playback.use_playback and node_group is not None and "KC_Play" in nodes_kc_playback:
            kc_play_node =  nodes_kc_playback["KC_Play"]
            file_path_error = ""
            temporal_error = ""
            if (kc_play_node.image is not None ):
                bpy.data.images.remove(kc_play_node.image)
                #bpy.ops.kc_playback_node.image.delete()
            if load_image:
                if os.path.exists(kcycles_playback.image_file):
                    kc_play_node.image = bpy.data.images.load(kcycles_playback.image_file)
                    kc_play_node.image.source = "FILE"
                else:
                    file_path_error = "         ** 错误: 路径或文件不存在。 "
            else:
                complete_animation_path = bpy.path.abspath(kcycles_playback.animation_path)
                if (self.load_subdirectory and kcycles_playback.subdirectory_list.strip() != "(None)"):
                    complete_animation_path =  bpy.path.abspath(complete_animation_path + os.sep + kcycles_playback.subdirectory_list + os.sep)
                else:
                    scene.kcycles_playback_subdirectory_list.clear()
                    new_item = scene.kcycles_playback_subdirectory_list.add()
                    new_item.name = "(None)                                  "
                    update_subdirectory_item = False
                    kcycles_playback.subdirectory_list = new_item.name
                    update_subdirectory_item = True

                # check that the folder exists and not drive root
                drive, tail = os.path.splitdrive(complete_animation_path)
                valid_tail = any(char.isalpha() for char in tail) or any(char.isdigit() for char in tail)
 
                if os.path.isdir(complete_animation_path) and valid_tail and len(complete_animation_path) > 3:
                    if (not self.load_subdirectory):
                        sub_directories = get_subdirs_with_files(complete_animation_path)
                        for sub_directory in sub_directories:
                            new_item = scene.kcycles_playback_subdirectory_list.add()
                            new_item.name = sub_directory

                    image_files = get_image_files(complete_animation_path)
                    total_files = len(image_files)
                    if (total_files > 2):
                        start_frame = get_number_from_filename_end(image_files[0])
                        end_frame = get_number_from_filename_end(image_files[(total_files-1)])
                        if ((end_frame - start_frame + 1) == total_files):
                            kc_play_node.image = bpy.data.images.load(complete_animation_path+image_files[0])
                            kc_play_node.image.source = "SEQUENCE"
                            kc_play_node.frame_start = start_frame
                            kc_play_node.frame_duration = total_files
                            kc_play_node.frame_offset = start_frame - 1
                            kc_play_node.use_cyclic = False
                            kc_play_node.use_auto_refresh = False
                            if ("Vector" not in kc_play_node.outputs):
                                temporal_error = "         ** 信息: 图像文件需要数据矢量通道"
                        else:
                            file_path_error = "         ** 错误: 图像文件编号必须是连续的。"
                    else:
                        file_path_error = "         ** 信息: 请输入包含超过 2 个文件的路径/子文件夹。"
                else:
                    if not valid_tail:
                        file_path_error = "         ** 错误: 路径必须是子目录。 "
                    else:
                        file_path_error = "         ** 错误: 路径不存在。 "

                if (len(file_path_error) == 0):
                    update_apply_timeline(self, context)
                    update_change_camera_from_path(self, context)

            if ("Combined" in nodes_kc_playback["KC_Play"].outputs or "Image" in nodes_kc_playback["KC_Play"].outputs) and ".KC_Temporal_Core" in nodes_kc_playback:
                node_group.nodes["KC_Playback"].node_tree.links.new(nodes_kc_playback["KC_Play"].outputs[0], nodes_kc_playback[".KC_Temporal_Core"].inputs["Frame"])
            if "Vector" in nodes_kc_playback["KC_Play"].outputs and ".KC_Temporal_Core" in nodes_kc_playback:
                node_group.nodes["KC_Playback"].node_tree.links.new(nodes_kc_playback["KC_Play"].outputs["Vector"], nodes_kc_playback[".KC_Temporal_Core"].inputs["Vector"])
        return {"FINISHED"}

def set_viewport_compositor(self, context):
    kcycles_playback = context.scene.kcycles_playback
    if (kcycles_playback.use_playback):
        viewport_compositor = 'ALWAYS' if kcycles_playback.viewport_compositor else 'DISABLED'
        for workspace in bpy.data.workspaces:
            for screen in workspace.screens:
                for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        if (area.spaces[0].shading.use_compositor != viewport_compositor):
                            area.spaces[0].shading.use_compositor = viewport_compositor
    return

def playback_viewport_settings(self, context, enable):
    scene = context.scene
    kcycles_playback = scene.kcycles_playback
    node_group = context.scene.compositing_node_group
    nodes_kc_playback = node_group.nodes["KC_Playback"].node_tree.nodes

    if "KC_ScaleView" in node_group.nodes:
        node_group.nodes["KC_ScaleView"].mute = False if kcycles_playback.scale_fit_viewport and enable else True

    for obj in scene.objects:
        if (obj.type != 'CAMERA'):
            obj.hide_viewport = True if kcycles_playback.disable_viewport_object and enable else False

    if (scene.cycles.preview_samples != 1 and enable):
        kcycles_playback.preview_render_samples_previous = scene.cycles.preview_samples

    scene.cycles.preview_samples = 1 if kcycles_playback.preview_render_samples_one and enable else kcycles_playback.preview_render_samples_previous
    scene.render.compositor_device = "GPU" if kcycles_playback.compositor_device_GPU else "CPU"


def update_playback_viewport_settings(self, context):
    playback_viewport_settings(self, context, True)
    return

def node_output_socket_link(node_group, node_name, output_socket_name):
    node = node_group.nodes.get(node_name)
    if not node:
        return None

    output_socket = node.outputs.get(output_socket_name)
    if not output_socket:
        return None

    for link in node_group.links:
        if link.from_socket == output_socket:
            return link
    return None

def node_input_socket_link(node_group, node_name, input_socket_name):
    node = node_group.nodes.get(node_name)
    if not node:
        return None

    input_socket = node.inputs.get(input_socket_name)
    if not input_socket:
        return None

    for link in node_group.links:
        if link.to_socket == input_socket:
            return link
    return None

def update_use_playback(self, context):
    #print("update_use_playback")
    scene = context.scene
    kcycles_playback = scene.kcycles_playback

    node_group = []
    if not scene.compositing_node_group:
        node_group = scene.compositing_node_group = bpy.data.node_groups.new('Compositing Nodes', 'CompositorNodeTree')
    else:
        node_group = scene.compositing_node_group

    render_layers = get_node_id(node_group.nodes, "CompositorNodeRLayers")
    if not render_layers:
        render_layers = node_group.nodes.new(type="CompositorNodeRLayers")
        render_layers.select = False
    group_output = get_node_id(node_group.nodes, "NodeGroupOutput")
    if not group_output:
        group_output = node_group.nodes.new(type="NodeGroupOutput")
        if not ("Image" in node_group.nodes['Group Output'].inputs):
            node_group.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        group_output.select = False
    viewer_output = get_node_id(node_group.nodes, "CompositorNodeViewer")
    if not viewer_output:
        viewer_output = node_group.nodes.new(type="CompositorNodeViewer")
        viewer_output.select = False

    if not "KC_ScaleView" in node_group.nodes:
        kc_scale_view_node = node_group.nodes.new(type="CompositorNodeScale")
        kc_scale_view_node.name = "KC_ScaleView"
        kc_scale_view_node.label = "KC ScaleView"
        kc_scale_view_node.location = (render_layers.location[0] + 375, render_layers.location[1] - 50)
        kc_scale_view_node.inputs["Type"].default_value = "Render Size"
        kc_scale_view_node.inputs["Frame Type"].default_value = "Fit"
        kc_scale_view_node.inputs["Interpolation"].default_value = "Anisotropic"
        kc_scale_view_node.select = False
        kc_scale_view_node.mute = False

    # Hide KC_Playback
    if not kcycles_playback.use_playback:
        render_layers.mute = False
        if "KC_Playback" in node_group.nodes:
             node_group.nodes["KC_Playback"].mute = True
             playback_viewport_settings(self, context, False)
             update_use_kc_temporal(self, context)

             # Update the links
             link = node_output_socket_link(node_group, "KC_Playback", "Image")
             #print("**** link from: " + link.from_node.name)
             #print("**** link to: " + link.to_node.name)
             if (link != None):
                node_group.links.new(render_layers.outputs[0], link.to_node.inputs[link.to_socket.name])
             link_input = node_input_socket_link(node_group, "KC_ScaleView", "Image")
             link_output = node_output_socket_link(node_group, "KC_ScaleView", "Image")
             if (link_output != None and link_input.from_node.name == "KC_Playback"):
                node_group.links.new(render_layers.outputs[0], link_output.to_node.inputs[link_output.to_socket.name])
             elif (link_input != None and link_output != None):
                node_group.links.new(link_input.from_node.outputs[link_input.from_socket.name], link_output.to_node.inputs[link_output.to_socket.name])
             node_group.nodes.remove(node_group.nodes["KC_ScaleView"])
             node_group.nodes.remove(node_group.nodes["KC_Playback"])
             return
    else:
        if not "KC_Playback" in node_group.nodes:
            if not scene.render.use_compositing:
                scene.render.use_compositing = True

            # Append and create a KC_Playback node group
            if not "KC_Playback" in bpy.data.node_groups:
                append_kcycles_node(node_name="KC_Playback")

            kc_playback_node = node_group.nodes.new("CompositorNodeGroup")
            kc_playback_node.name = "KC_Playback"
            kc_playback_node.label = "KC Playback"
            kc_playback_node.node_tree = bpy.data.node_groups["KC_Playback"]
            kc_playback_node.node_tree.name = "KC_Playback"
            kc_playback_node.select = False

        # Link Render Layer, Composite and Viewer nodes
        kc_playback_node = node_group.nodes["KC_Playback"]
        link_output = node_output_socket_link(node_group, "Render Layers", "Image")
        if (link_output != None):
            node_group.links.new(kc_playback_node.outputs[0], link_output.to_node.inputs[link_output.to_socket.name])
            kc_playback_node.location = (link_output.to_node.location.x - link_output.to_node.width -50, link_output.to_node.location.y)
        else:
            node_group.links.new(kc_playback_node.outputs[0], node_group.nodes['Group Output'].inputs[0])
            node_group.nodes['Group Output'].location = (kc_playback_node.location.x + kc_playback_node.width + 50, kc_playback_node.location.y)
            kc_playback_node.location = (render_layers.location.x + render_layers.width + 50, render_layers.location.y - 50)

        link_input = node_input_socket_link(node_group, "Viewer", "Image")
        #if link_input != None:
        #    print("**** from: " + link_input.from_node.name)
        #    print("**** to: " + link_input.to_node.name)
        if (link_input != None and link_input.from_node.name != "Render Layers"):
            node_group.links.new(link_input.from_node.outputs[link_input.from_socket.name], node_group.nodes['KC_ScaleView'].inputs["Image"])
        else:
            node_group.links.new(kc_playback_node.outputs[0], node_group.nodes['KC_ScaleView'].inputs["Image"])
        node_group.links.new(node_group.nodes['KC_ScaleView'].outputs["Image"], node_group.nodes['Viewer'].inputs["Image"])
        node_group.nodes['Viewer'].location = (node_group.nodes['Group Output'].location.x, node_group.nodes['Group Output'].location.y - node_group.nodes['Viewer'].height)
        node_group.nodes['KC_ScaleView'].location = (node_group.nodes['Viewer'].location.x - node_group.nodes['Viewer'].width -50, node_group.nodes['Viewer'].location.y)
        node_group.nodes["KC_Playback"].mute = False
        render_layers.mute = True

    # Update the compositor values
    scene.sync_mode = 'NONE'
    playback_viewport_settings(self, context, True)
    bpy.ops.kcycles.playback_load()
    update_use_kc_temporal(self, context)
    update_use_vector_blur(self, context)

def update_kc_prev_next_node(self, context, postfix, offset):
    node_group = context.scene.compositing_node_group
    nodes_kc_playback = node_group.nodes["KC_Playback"].node_tree.nodes

    node_prev_name = "KC_Play" + "Prev" + postfix
    node_next_name = "KC_Play" + "Next" + postfix
    prev_input_frame = "Frame" + "Prev" + postfix
    next_input_frame = "Frame" + "Next" + postfix
    prev_input_vector = "Vector" + "Prev" + postfix
    next_input_vector = "Vector" + "Next" + postfix

    if not node_prev_name in nodes_kc_playback:
        KC_PlayPrev_node = nodes_kc_playback.new("CompositorNodeImage")
        KC_PlayPrev_node.name = node_prev_name
        KC_PlayPrev_node.label = node_prev_name
        KC_PlayPrev_node.location = (nodes_kc_playback[".KC_Temporal_Core"].location[0] - 350,  nodes_kc_playback[".KC_Temporal_Core"].location[1] - 50)
        KC_PlayPrev_node.select = False

    nodes_kc_playback[node_prev_name].image = nodes_kc_playback["KC_Play"].image
    nodes_kc_playback[node_prev_name].image.source = "SEQUENCE"
    nodes_kc_playback[node_prev_name].frame_start = nodes_kc_playback["KC_Play"].frame_start
    nodes_kc_playback[node_prev_name].frame_offset = nodes_kc_playback["KC_Play"].frame_offset - offset
    nodes_kc_playback[node_prev_name].frame_duration = nodes_kc_playback["KC_Play"].frame_duration
    nodes_kc_playback[node_prev_name].use_cyclic = False
    nodes_kc_playback[node_prev_name].use_auto_refresh = False

    node_group.nodes["KC_Playback"].node_tree.links.new(nodes_kc_playback[node_prev_name].outputs[0], nodes_kc_playback[".KC_Temporal_Core"].inputs[prev_input_frame])
    node_group.nodes["KC_Playback"].node_tree.links.new(nodes_kc_playback[node_prev_name].outputs["Vector"], nodes_kc_playback[".KC_Temporal_Core"].inputs[prev_input_vector])

    if not node_next_name in nodes_kc_playback:
        KC_PlayNext_node = nodes_kc_playback.new("CompositorNodeImage")
        KC_PlayNext_node.name = node_next_name
        KC_PlayNext_node.label = node_next_name
        KC_PlayNext_node.location = (nodes_kc_playback[".KC_Temporal_Core"].location[0] - 300,  nodes_kc_playback[".KC_Temporal_Core"].location[1] - 50)
        KC_PlayNext_node.select = False

    nodes_kc_playback[node_next_name].image = nodes_kc_playback["KC_Play"].image
    nodes_kc_playback[node_next_name].image.source = "SEQUENCE"
    nodes_kc_playback[node_next_name].frame_start = nodes_kc_playback["KC_Play"].frame_start
    nodes_kc_playback[node_next_name].frame_offset = nodes_kc_playback["KC_Play"].frame_offset + offset
    nodes_kc_playback[node_next_name].frame_duration = nodes_kc_playback["KC_Play"].frame_duration
    nodes_kc_playback[node_next_name].use_cyclic = False
    nodes_kc_playback[node_next_name].use_auto_refresh = False

    node_group.nodes["KC_Playback"].node_tree.links.new(nodes_kc_playback[node_next_name].outputs[0], nodes_kc_playback[".KC_Temporal_Core"].inputs[next_input_frame])
    node_group.nodes["KC_Playback"].node_tree.links.new(nodes_kc_playback[node_next_name].outputs["Vector"], nodes_kc_playback[".KC_Temporal_Core"].inputs[next_input_vector])

def update_use_kc_temporal(self, context):
    scene = context.scene
    kcycles_playback = scene.kcycles_playback

    node_group = context.scene.compositing_node_group
    nodes_kc_playback = node_group.nodes["KC_Playback"].node_tree.nodes
    nodes = nodes_kc_playback[".KC_Temporal_Core"].node_tree.nodes

    if (not kcycles_playback.use_playback or not kcycles_playback.use_temporal or kcycles_playback.playback_mode == "IMAGE" or nodes_kc_playback["KC_Play"].image is None or len(file_path_error) > 0 or len(temporal_error) > 0):
        nodes_kc_playback[".KC_Temporal_Core"].mute = True
        if "KC_PlayPrev" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayPrev"])
        if "KC_PlayNext" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayNext"])
        if "KC_PlayPrev2" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayPrev2"])
        if "KC_PlayNext2" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayNext2"])
        if "KC_PlayPrev3" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayPrev3"])
        if "KC_PlayNext3" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayNext3"])
        return

    update_kc_temporal_settings(self, context)
    update_kc_prev_next_node(self, context, "", 1)
    if (kcycles_playback.temporal_stabilize_level == "STANDARD"):
        nodes[".KC_Displace_Motion3"].mute = True
        nodes[".KC_Displace_Motion4"].mute = True
        nodes[".KC_Displace_Motion5"].mute = True
        nodes[".KC_Displace_Motion6"].mute = True
        nodes["Add_3-4"].mute = True
        nodes["Add_1-2-3-4"].mute = True
        nodes["Add_5-6"].mute = True
        nodes["Add_1-2-3-4-5-6"].mute = True
        nodes["Divide_All"].inputs["B"].default_value = (3, 3, 3, 1)
        nodes["Mask_Vector_1-2-3-4"].inputs["Factor"].default_value = 0
        nodes["Mask_Color_1-2-3-4"].inputs["Factor"].default_value = 0
        nodes["Mask_Vector_1-2-3-4-5-6"].inputs["Factor"].default_value = 0
        nodes["Mask_Color_1-2-3-4-5-6"].inputs["Factor"].default_value = 0
        if "KC_PlayPrev2" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayPrev2"])
        if "KC_PlayNext2" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayNext2"])
        if "KC_PlayPrev3" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayPrev3"])
        if "KC_PlayNext3" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayNext3"])
    elif (kcycles_playback.temporal_stabilize_level == "HIGH"):
        update_kc_prev_next_node(self, context, "2", 2)
        nodes[".KC_Displace_Motion3"].mute = False
        nodes[".KC_Displace_Motion4"].mute = False
        nodes[".KC_Displace_Motion5"].mute = True
        nodes[".KC_Displace_Motion6"].mute = True
        nodes["Add_3-4"].mute = False
        nodes["Add_1-2-3-4"].mute = False
        nodes["Add_5-6"].mute = True
        nodes["Add_1-2-3-4-5-6"].mute = True
        nodes["Divide_All"].inputs["B"].default_value = (5, 5, 5, 1)
        nodes["Mask_Vector_1-2-3-4"].inputs["Factor"].default_value = 1
        nodes["Mask_Color_1-2-3-4"].inputs["Factor"].default_value = 1
        nodes["Mask_Vector_1-2-3-4-5-6"].inputs["Factor"].default_value = 0
        nodes["Mask_Color_1-2-3-4-5-6"].inputs["Factor"].default_value = 0
        if "KC_PlayPrev3" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayPrev3"])
        if "KC_PlayNext3" in nodes_kc_playback:
            nodes_kc_playback.remove(nodes_kc_playback["KC_PlayNext3"])
    elif (kcycles_playback.temporal_stabilize_level == "ULTRA"):
        update_kc_prev_next_node(self, context, "2", 2)
        update_kc_prev_next_node(self, context, "3", 3)
        nodes[".KC_Displace_Motion3"].mute = False
        nodes[".KC_Displace_Motion4"].mute = False
        nodes[".KC_Displace_Motion5"].mute = False
        nodes[".KC_Displace_Motion6"].mute = False
        nodes["Add_3-4"].mute = False
        nodes["Add_1-2-3-4"].mute = False
        nodes["Add_5-6"].mute = False
        nodes["Add_1-2-3-4-5-6"].mute = False
        nodes["Divide_All"].inputs["B"].default_value = (7, 7, 7, 1)
        nodes["Mask_Vector_1-2-3-4"].inputs["Factor"].default_value = 1
        nodes["Mask_Color_1-2-3-4"].inputs["Factor"].default_value = 1
        nodes["Mask_Vector_1-2-3-4-5-6"].inputs["Factor"].default_value = 1
        nodes["Mask_Color_1-2-3-4-5-6"].inputs["Factor"].default_value = 1
   
    return


def update_kc_temporal_settings(self, context):
    scene = context.scene
    kcycles_playback = scene.kcycles_playback

    node_group = context.scene.compositing_node_group
    nodes_kc_playback = node_group.nodes["KC_Playback"].node_tree.nodes
    nodes = nodes_kc_playback[".KC_Temporal_Core"].node_tree.nodes

    if (kcycles_playback.use_temporal):
        nodes_kc_playback[".KC_Temporal_Core"].mute = False
        nodes_kc_playback[".KC_Temporal_Core"].inputs["Frame Start"].default_value = nodes_kc_playback["KC_Play"].frame_start
        nodes_kc_playback[".KC_Temporal_Core"].inputs["Frame End"].default_value = nodes_kc_playback["KC_Play"].frame_start + nodes_kc_playback["KC_Play"].frame_duration - 1
        nodes["Motion_Mask_Mix"].mute = False if kcycles_playback.use_motion_stabilization else True
    return

def update_use_vector_blur(self, context):
    scene = context.scene
    kcycles_playback = scene.kcycles_playback
    node_group = context.scene.compositing_node_group
    nodes_kc_playback = node_group.nodes["KC_Playback"].node_tree.nodes

    nodes_kc_playback["KC_Vector_Blur"].mute = False if kcycles_playback.use_vector_blur else True

    kc_vector_blur = node_group.nodes["KC_Playback"].node_tree.nodes["KC_Vector_Blur"]

    if ("Vector" in nodes_kc_playback["KC_Play"].outputs):
        node_group.nodes["KC_Playback"].node_tree.links.new(nodes_kc_playback["KC_Play"].outputs["Vector"], kc_vector_blur.inputs["Speed"])
    if ("Depth" in nodes_kc_playback["KC_Play"].outputs):
        node_group.nodes["KC_Playback"].node_tree.links.new(nodes_kc_playback["KC_Play"].outputs["Depth"], kc_vector_blur.inputs["Z"])
    return

def get_subdirectory_enum_items(self, context):
    items = []
    for i, item in enumerate(context.scene.kcycles_playback_subdirectory_list):
        # Each item tuple: (identifier, display_name, description, icon, index)
        items.append((item.name, item.name, f"Description for {item.name}", '', i))
    return items

class KCyclesSubDirectoryItem(bpy.types.PropertyGroup):
    """保存单个目录名称。"""
    name: bpy.props.StringProperty(
        name="目录名称",
        description="选定父目录中的子目录",
        maxlen=256
    )

class KCyclesPlaybackSettings(bpy.types.PropertyGroup):
    use_playback: BoolProperty(
        name="启用播放模式",
        description="启用播放模式",
        default=False,
        update=update_use_playback,
        options={'SKIP_PRESET'},
    )

    playback_mode: bpy.props.EnumProperty(
        name="播放模式",
        description="播放模式",
        items=[
            ('IMAGE', "图像", "播放图像"),
            ('ANIMATION', "动画", "播放动画"),
        ],
        default='ANIMATION',
        update=update_playback_mode,
        options={'LIBRARY_EDITABLE'},
    )

    image_file: StringProperty(
        name="",
        description="加载图像的文件路径",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
        update=update_image_file,
    )

    animation_path: StringProperty(
        name="",
        description="加载动画的目录路径",
        default="",
        maxlen=1024,
        subtype='DIR_PATH',
        update=update_animation_path,
    )

    subdirectory_list: EnumProperty(
        name="子目录",
        description="子目录列表",
        items=get_subdirectory_enum_items,
        update=update_subdirectory,
    )

    apply_timeline: BoolProperty(
        name="将图像序列应用到播放时间线",
        description="将图像序列应用到播放时间线",
        default=True,
        update=update_apply_timeline,
    )

    change_camera_from_path: BoolProperty(
        name="从动画/子目录路径更改场景相机",
        description="从动画/子目录路径更改场景相机",
        default=False,
        update=update_change_camera_from_path,
    )

    use_temporal: BoolProperty(
        name="启用时序稳定",
        description="启用时序稳定",
        default=False,
        update=update_use_kc_temporal,
        options={'SKIP_PRESET'}
    )

    temporal_stabilize_level: bpy.props.EnumProperty(
        name="时序稳定级别",
        description="时序稳定级别",
        items=[
            ('STANDARD', "标准", "标准时序稳定级别"),
            ('HIGH', "高", "高时序稳定级别"),
            ('ULTRA', "超高", "超高时序稳定级别"),
        ],
        default='STANDARD',
        update=update_use_kc_temporal,
        options={'LIBRARY_EDITABLE'}
    )

    use_motion_stabilization: BoolProperty(
        name="启用运动稳定",
        description="启用运动稳定",
        default=True,
        update=update_kc_temporal_settings,
        options={'SKIP_PRESET'}
    )

    viewport_compositor: BoolProperty(
        name="启用视口合成器",
        description="启用视口合成器以在视口中显示播放图像",
        default=True,
        update=update_playback_viewport_settings,
    )

    disable_viewport_object: BoolProperty(
        name="隐藏视口中的所有物体",
        description="隐藏视口中的所有物体以获得更快的视口性能",
        default=True,
        update=update_playback_viewport_settings,
    )

    scale_fit_viewport: BoolProperty(
        name="缩放播放以适应 3D 视口",
        description="缩放播放以适应 3D 视口",
        default=True,
        update=update_playback_viewport_settings,
    )

    compositor_device_GPU: BoolProperty(
        name="设置合成器设备为 GPU",
        description="设置合成器设备为 GPU 以获得更快的合成速度",
        default=True,
        update=update_playback_viewport_settings,
    )

    preview_render_samples_one: BoolProperty(
        name="将预览渲染采样设置为 1",
        description="将预览渲染采样设置为 1 以获得更快的视口更新",
        default=True,
        update=update_playback_viewport_settings,
    )

    preview_render_samples_previous: IntProperty(
        name="原始预览渲染采样",
        description="原始预览渲染采样",
        default=1024,
    )

    use_vector_blur: BoolProperty(
        name="启用矢量模糊",
        description="启用矢量模糊",
        default=False,
        update=update_use_vector_blur,
        options={'SKIP_PRESET'},
    )

class RenderButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

class RENDER_PT_kcycles_playback(RenderButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "RENDER_PT_kcycles"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        kcycles_playback = scene.kcycles_playback
        layout.prop(kcycles_playback, "use_playback", text="播放与超级时序降噪器")
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        scene = context.scene
        kcycles_playback = scene.kcycles_playback

        layout.use_property_split = False
        row = layout.row(align=True)
        row.enabled = kcycles_playback.use_playback
        row.alignment = 'LEFT'
        row.label(text="     ")
        row.label(text="     ")
        row.label(text="模式 ")
        sub = row.row()
        sub.enabled = kcycles_playback.use_playback
        sub.scale_x = 0.4
        sub.prop(kcycles_playback, "playback_mode", expand=True)

        layout.use_property_split = False
        row = layout.row(align=True)
        row.enabled = kcycles_playback.use_playback
        row.alignment = 'LEFT'
        row.label(text="   ")
        row.label(text="   ")
        if (kcycles_playback.playback_mode == "ANIMATION"):
            row.label(text="路径")
            sub = row.row()
            sub.scale_x = 1.1
            sub.prop(kcycles_playback, "animation_path", text="")
            layout.use_property_split = False
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            row.enabled = kcycles_playback.use_playback
            row.scale_x = 1.1
            row.label(text="       ")
            row.label(text="子目录")
            row.prop(kcycles_playback, "subdirectory_list", text="")
            row.operator("kcycles.playback_load", icon="FILE_REFRESH", text = "")
        else:
            row.label(text="文件")
            sub = row.row()
            sub.scale_x = 1.0
            sub.prop(kcycles_playback, "image_file", text="")

        layout.use_property_split = False
        row = layout.row(align=True)
        row.enabled = kcycles_playback.use_playback
        row.alignment = 'LEFT'
        if (kcycles_playback.use_playback and kcycles_playback.playback_mode == "ANIMATION"):
            if (len(file_path_error) > 0):
                row.alert = True
                row.label(text=file_path_error)
            else:
                node_group = context.scene.compositing_node_group
                nodes_kc_playback = node_group.nodes["KC_Playback"].node_tree.nodes
                if (node_group != None and "KC_Play" in nodes_kc_playback and nodes_kc_playback["KC_Play"].image != None):
                    if (nodes_kc_playback["KC_Play"].image.source == "SEQUENCE"):
                        image_sequence_label = "             图像序列: " + "开始: " + str(nodes_kc_playback["KC_Play"].frame_start) \
                            + " - 结束: " + str(nodes_kc_playback["KC_Play"].frame_start + nodes_kc_playback["KC_Play"].frame_duration - 1)
                        row.label(text=image_sequence_label)
                        row.scale_y = 0.95

                        layout.use_property_split = False
                        row = layout.row(align=True)
                        row.enabled = kcycles_playback.use_playback
                        row.alignment = 'LEFT'
                        row.scale_x = 1.0
                        row.scale_y = 0.95
                        if (kcycles_playback.playback_mode == "ANIMATION"):
                            row.label(text="           ")
                            row.prop(kcycles_playback, "apply_timeline", text="将图像序列应用到时间线")

                        layout.use_property_split = False
                        row = layout.row(align=True)
                        row.enabled = kcycles_playback.use_playback
                        row.alignment = 'LEFT'
                        row.scale_x = 1.0
                        if (kcycles_playback.playback_mode == "ANIMATION"):
                            row.label(text="           ")
                            row.prop(kcycles_playback, "change_camera_from_path", text="从路径更换场景相机")


        elif (kcycles_playback.use_playback and kcycles_playback.playback_mode == "IMAGE"):
            if (len(file_path_error) > 0):
                row.alert = True
                row.label(text=file_path_error)

class RENDER_PT_kcycles_temporal(RenderButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "RENDER_PT_kcycles_playback"

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        kcycles_playback = scene.kcycles_playback

        layout.active = kcycles_playback.use_playback and kcycles_playback.playback_mode == "ANIMATION" and len(file_path_error) == 0 and len(temporal_error) == 0
        layout.prop(kcycles_playback, "use_temporal", text="超级时序降噪器")
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        scene = context.scene
        kcycles_playback = scene.kcycles_playback
        allow_temporal = kcycles_playback.use_playback and kcycles_playback.use_temporal and kcycles_playback.playback_mode == "ANIMATION" and len(file_path_error) == 0 and len(temporal_error) == 0

        if (kcycles_playback.playback_mode != "ANIMATION" or not kcycles_playback.use_temporal):
            layout.use_property_split = False
            row = layout.row(align=True)
            if (len(file_path_error) > 0 or len(temporal_error) > 0):
                if (len(temporal_error) > 0):
                    row.alignment = 'LEFT'
                    row.alert = True
                    row.label(text=temporal_error)
            return

        if (allow_temporal):
            node_group = context.scene.compositing_node_group
            kc_temporal = node_group.nodes["KC_Playback"].node_tree.nodes[".KC_Temporal_Core"]
            nodes_kc_temporal = kc_temporal.node_tree.nodes
 
            layout.use_property_split = False
            row = layout.row(align=True)
            row.enabled = allow_temporal
            row.alignment = 'RIGHT'
            row.label(text=" ")
            row.label(text="稳定级别 ")
            sub = row.row()
            sub.scale_x = 0.27
            sub.prop(kcycles_playback, "temporal_stabilize_level", expand=True)

            layout.use_property_split = False
            row = layout.row(align=True)
            row.enabled = allow_temporal
            row.alignment = 'LEFT'
            row.label(text="       ")
            row.prop(kcycles_playback, "use_motion_stabilization", text="")
            row.label(text="运动稳定")

            layout.use_property_split = False
            row = layout.row(align=True)
            row.enabled = allow_temporal and kcycles_playback.use_motion_stabilization
            row.alignment = 'RIGHT'
            row.scale_x = 0.90
            row.label(text="矢量")
            row.prop(nodes_kc_temporal["Switch_Vector_Mask"].inputs["Switch"], "default_value", text="")
            row.label(text="")
            sub = row.row(align=True)
            sub.enabled = allow_temporal and kcycles_playback.use_motion_stabilization and nodes_kc_temporal["Switch_Vector_Mask"].inputs["Switch"].default_value
            sub.alignment = 'RIGHT'
            sub.scale_x = 0.90
            sub.prop(kc_temporal.inputs["Vector Threshold"], "default_value", text="阈值")
            sub.prop(kc_temporal.inputs["Vector Size"], "default_value", text="大小")

            layout.use_property_split = False
            row = layout.row(align=True)
            row.enabled = allow_temporal and kcycles_playback.use_temporal and kcycles_playback.use_motion_stabilization
            row.alignment = 'RIGHT'
            row.scale_x = 0.90
            row.label(text="颜色")
            row.prop(nodes_kc_temporal["Switch_Color_Mask"].inputs["Switch"], "default_value", text="")
            row.label(text="")
            sub = row.row(align=True)
            sub.enabled = allow_temporal and kcycles_playback.use_temporal and kcycles_playback.use_motion_stabilization and nodes_kc_temporal["Switch_Color_Mask"].inputs["Switch"].default_value
            sub.alignment = 'RIGHT'
            sub.scale_x = 0.90
            sub.prop(kc_temporal.inputs["Color Threshold"], "default_value", text="阈值")
            sub.prop(kc_temporal.inputs["Color Size"], "default_value", text="大小")

            layout.use_property_split = False
            row = layout.row(align=True)
            row.enabled = allow_temporal and kcycles_playback.use_temporal and kcycles_playback.use_motion_stabilization
            row.alignment = 'RIGHT'
            row.scale_x = 0.97
            row.label(text="  覆盖运动遮罩 ")
            row.prop(nodes_kc_temporal["Switch_Mask"].inputs["Switch"], "default_value", text="")
            row.label(text="")
            sub = row.row()
            sub.enabled = allow_temporal and kcycles_playback.use_temporal and kcycles_playback.use_motion_stabilization and nodes_kc_temporal["Switch_Mask"].inputs["Switch"].default_value
            sub.scale_x = 0.71
            sub.prop(nodes_kc_temporal["Blend_Mask"].inputs["Factor"], "default_value", text="强度")

class RENDER_PT_kcycles_viewport(RenderButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "RENDER_PT_kcycles_playback"

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        kcycles_playback = scene.kcycles_playback

        layout.use_property_split = False
        row = layout.row(align=True)
        row.enabled = kcycles_playback.use_playback 
        row.alignment = 'LEFT'
        row.label(text="视口设置 ")
        if (kcycles_playback.use_playback):
            set_viewport_compositor(self, context)
        row.prop(kcycles_playback, "viewport_compositor", icon="NODE_COMPOSITING", text="")

        row.prop(kcycles_playback, "scale_fit_viewport", icon="VIEWZOOM", text="")
        if (kcycles_playback.disable_viewport_object):
            row.prop(kcycles_playback, "disable_viewport_object", icon="RESTRICT_VIEW_ON", text="")
        else:
            row.prop(kcycles_playback, "disable_viewport_object", icon="RESTRICT_VIEW_OFF", text="")
        row.prop(kcycles_playback, "compositor_device_GPU", icon="EVENT_G", text="")
        row.prop(kcycles_playback, "preview_render_samples_one", icon="EVENT_ONEKEY", text="")

    def draw(self, context):
        return


class RENDER_PT_kcycles_vector_blur(RenderButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "RENDER_PT_kcycles_playback"

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        kcycles_playback = scene.kcycles_playback

        layout.active = kcycles_playback.use_playback and kcycles_playback.playback_mode == "ANIMATION" and len(file_path_error) == 0 and len(temporal_error) == 0
        layout.prop(kcycles_playback, "use_vector_blur", text="矢量模糊")
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        scene = context.scene
        kcycles_playback = scene.kcycles_playback
        node_group = context.scene.compositing_node_group
        allow_vector_blur = kcycles_playback.use_playback and kcycles_playback.use_vector_blur and kcycles_playback.playback_mode == "ANIMATION" and len(file_path_error) == 0 and len(temporal_error) == 0
        if allow_vector_blur:
            kc_vector_blur = node_group.nodes["KC_Playback"].node_tree.nodes["KC_Vector_Blur"]
            layout.use_property_split = False
            row = layout.row(align=True)
            row.enabled = allow_vector_blur
            row.alignment = 'LEFT'
            row.label(text="       ")
            row.prop(kc_vector_blur.inputs["Samples"], "default_value", text="采样")

            layout.use_property_split = False
            row = layout.row(align=True)
            row.enabled = allow_vector_blur
            row.alignment = 'LEFT'
            row.label(text="       ")
            row.prop(kc_vector_blur.inputs["Shutter"], "default_value", text="快门  ")
        return

classes = (
    RENDER_PT_kcycles_playback,
    RENDER_OT_kcycles_playback_load,
    RENDER_PT_kcycles_temporal,
    RENDER_PT_kcycles_viewport,
    RENDER_PT_kcycles_vector_blur,
    KCyclesSubDirectoryItem,
)

def register():
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.kcycles_playback_subdirectory_list = bpy.props.CollectionProperty(type=KCyclesSubDirectoryItem)
    bpy.utils.register_class(KCyclesPlaybackSettings)
    bpy.types.Scene.kcycles_playback = PointerProperty(type=KCyclesPlaybackSettings)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    del bpy.types.Scene.kcycles_playback_subdirectory_list
    del bpy.types.Scene.kcycles_playback
    bpy.utils.unregister_class(KCyclesPlaybackSettings)
