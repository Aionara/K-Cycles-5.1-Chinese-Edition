# SPDX-FileCopyrightText: 2011-2022 Blender Foundation
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from bpy.app.translations import pgettext_tip as tip_


class CYCLES_OT_use_shading_nodes(Operator):
    """在灯光上启用节点"""
    bl_idname = "cycles.use_shading_nodes"
    bl_label = "使用节点"

    @classmethod
    def poll(cls, context):
        return getattr(context, "light", False)

    def execute(self, context):
        if context.light:
            context.light.use_nodes = True

        return {'FINISHED'}


class CYCLES_OT_denoise_animation(Operator):
    "使用当前场景和视图层设置对渲染的动画序列进行降噪。" \
        "需要降噪数据通道并输出到 OpenEXR 多层文件"
    bl_idname = "cycles.denoise_animation"
    bl_label = "动画降噪"

    input_filepath: StringProperty(
        name='输入文件路径',
        description='要降噪的图像文件路径。如果未指定，则使用场景中的渲染文件路径和帧范围',
        default='',
        subtype='FILE_PATH')

    output_filepath: StringProperty(
        name='输出文件路径',
        description='如果未指定，渲染将在原地进行降噪',
        default='',
        subtype='FILE_PATH')

    def execute(self, context):
        import os

        preferences = context.preferences
        scene = context.scene
        view_layer = context.view_layer

        in_filepath = self.input_filepath
        out_filepath = self.output_filepath

        in_filepaths = []
        out_filepaths = []

        if in_filepath != '':
            # Denoise a single file
            if out_filepath == '':
                out_filepath = in_filepath

            in_filepaths.append(in_filepath)
            out_filepaths.append(out_filepath)
        else:
            # Denoise animation sequence with expanded frames matching
            # Blender render output file naming.
            in_filepath = scene.render.filepath
            if out_filepath == '':
                out_filepath = in_filepath

            # Backup since we will overwrite the scene path temporarily
            original_filepath = scene.render.filepath

            for frame in range(scene.frame_start, scene.frame_end + 1):
                scene.render.filepath = in_filepath
                filepath = scene.render.frame_path(frame=frame)
                in_filepaths.append(filepath)

                if not os.path.isfile(filepath):
                    scene.render.filepath = original_filepath
                    err_msg = tip_("未找到帧 '%s'，动画必须完整") % filepath
                    self.report({'ERROR'}, err_msg)
                    return {'CANCELLED'}

                scene.render.filepath = out_filepath
                filepath = scene.render.frame_path(frame=frame)
                out_filepaths.append(filepath)

            scene.render.filepath = original_filepath

        # Run denoiser
        # TODO: support cancel and progress reports.
        import _cycles
        try:
            _cycles.denoise(preferences.as_pointer(),
                            scene.as_pointer(),
                            view_layer.as_pointer(),
                            input=in_filepaths,
                            output=out_filepaths)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'FINISHED'}

        self.report({'INFO'}, "降噪完成")
        return {'FINISHED'}


class CYCLES_OT_merge_images(Operator):
    "将使用不同采样范围渲染的 OpenEXR 多层图像合并为一张噪点更少的图像"
    bl_idname = "cycles.merge_images"
    bl_label = "合并图像"

    input_filepath1: StringProperty(
        name='输入文件路径 1',
        description='要合并的图像文件路径',
        default='',
        subtype='FILE_PATH')

    input_filepath2: StringProperty(
        name='输入文件路径 2',
        description='要合并的图像文件路径',
        default='',
        subtype='FILE_PATH')

    output_filepath: StringProperty(
        name='输出文件路径',
        description='合并后图像的文件路径',
        default='',
        subtype='FILE_PATH')

    def execute(self, context):
        in_filepaths = [self.input_filepath1, self.input_filepath2]
        out_filepath = self.output_filepath

        import _cycles
        try:
            _cycles.merge(input=in_filepaths, output=out_filepath)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'FINISHED'}

        return {'FINISHED'}


classes = (
    CYCLES_OT_use_shading_nodes,
    CYCLES_OT_denoise_animation,
    CYCLES_OT_merge_images
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
