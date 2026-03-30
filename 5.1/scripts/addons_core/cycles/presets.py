# SPDX-FileCopyrightText: 2011-2022 Blender Foundation
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from bl_operators.presets import AddPresetBase
from bpy.types import Operator


class AddPresetIntegrator(AddPresetBase, Operator):
    '''添加积分器预设'''
    bl_idname = "render.cycles_integrator_preset_add"
    bl_label = "添加积分器预设"
    preset_menu = "CYCLES_PT_integrator_presets"

    preset_defines = [
        "cycles = bpy.context.scene.cycles"
    ]

    preset_values = [
        "cycles.max_bounces",
        "cycles.diffuse_bounces",
        "cycles.glossy_bounces",
        "cycles.transmission_bounces",
        "cycles.volume_bounces",
        "cycles.transparent_max_bounces",
        "cycles.caustics_reflective",
        "cycles.caustics_refractive",
        "cycles.blur_glossy",
        "cycles.use_fast_gi",
        "cycles.ao_bounces",
        "cycles.ao_bounces_render",
    ]

    preset_subdir = "cycles/integrator"


class AddPresetSampling(AddPresetBase, Operator):
    '''添加采样预设'''
    bl_idname = "render.cycles_sampling_preset_add"
    bl_label = "添加采样预设"
    preset_menu = "CYCLES_PT_sampling_presets"

    preset_defines = [
        "cycles = bpy.context.scene.cycles"
    ]

    preset_values = [
        "cycles.use_adaptive_sampling",
        "cycles.samples",
        "cycles.adaptive_threshold",
        "cycles.adaptive_min_samples",
        "cycles.time_limit",
        "cycles.use_denoising",
        "cycles.denoiser",
        "cycles.denoising_input_passes",
        "cycles.denoising_prefilter",
        "cycles.denoising_quality",
    ]

    preset_subdir = "cycles/sampling"


class AddPresetViewportSampling(AddPresetBase, Operator):
    '''添加视口采样预设'''
    bl_idname = "render.cycles_viewport_sampling_preset_add"
    bl_label = "添加视口采样预设"
    preset_menu = "CYCLES_PT_viewport_sampling_presets"

    preset_defines = [
        "cycles = bpy.context.scene.cycles"
    ]

    preset_values = [
        "cycles.use_preview_adaptive_sampling",
        "cycles.preview_samples",
        "cycles.preview_adaptive_threshold",
        "cycles.preview_adaptive_min_samples",
        "cycles.use_preview_denoising",
        "cycles.preview_denoiser",
        "cycles.preview_denoising_input_passes",
        "cycles.preview_denoising_prefilter",
        "cycles.preview_denoising_quality",
        "cycles.preview_denoising_start_sample",
    ]

    preset_subdir = "cycles/viewport_sampling"


class AddPresetPerformance(AddPresetBase, Operator):
    '''添加性能预设'''
    bl_idname = "render.cycles_performance_preset_add"
    bl_label = "添加性能预设"
    preset_menu = "CYCLES_PT_performance_presets"

    preset_defines = [
        "render = bpy.context.scene.render",
        "cycles = bpy.context.scene.cycles",
    ]

    preset_values = [
        "render.threads_mode",
        "render.use_persistent_data",
        "cycles.debug_use_spatial_splits",
        "cycles.debug_use_compact_bvh",
        "cycles.debug_use_hair_bvh",
        "cycles.debug_bvh_time_steps",
        "cycles.tile_size",
    ]

    preset_subdir = "cycles/performance"

class AddPresetKCyclesPostFX(AddPresetBase, Operator):
    '''添加 K-Cycles 后期特效预设'''
    bl_idname = "render.cycles_kcycles_postfx_preset_add"
    bl_label = "添加 K-Cycles 后期特效预设"
    preset_menu = "CYCLES_PT_kcycles_postfx_presets"

    preset_defines = [
        "kscene = bpy.context.scene.kcycles_postfx",
        "camera_name = bpy.context.scene.camera.data.name",
        "camera_mode = kscene.camera_mode",
        "camera_kcycles = bpy.data.cameras[camera_name].kcycles_postfx",
        "kscene = camera_kcycles if camera_mode == True else kscene"
    ]

    preset_values = [
        "kscene.use_bloom",
        "kscene.bloom_threshold",
        "kscene.bloom_blend",
        "kscene.bloom_size",
        "kscene.bloom_intensity",
        "kscene.bloom_color_tint",
        "kscene.flares_threshold",
        "kscene.flares_glare_power",
        "kscene.flares_glare_rays",
        "kscene.flares_glare_rotation",
        "kscene.flares_glare_thin",
        "kscene.flares_glare_intensity",
        "kscene.flares_glare_color_shift",
        "kscene.flares_glare_color_tint",
        "kscene.flares_glare_softness",
        "kscene.flares_anamorphic_power",
        "kscene.flares_anamorphic_rotation",
        "kscene.flares_anamorphic_thin",
        "kscene.flares_anamorphic_intensity",
        "kscene.flares_anamorphic_color_shift",
        "kscene.flares_anamorphic_color_tint",
        "kscene.flares_anamorphic_softness",
        "kscene.flares_ghosts_intensity",
        "kscene.flares_ghosts_color_shift",
        "kscene.flares_ghosts_color_tint",
        "kscene.use_tonemapping",
        "kscene.tonemapping_exposure",
        "kscene.tonemapping_contrast",
        "kscene.tonemapping_highlights",
        "kscene.tonemapping_shadows",
        "kscene.tonemapping_color_boost",
        "kscene.tonemapping_saturation",
        "kscene.tonemapping_white_balance",
        "kscene.tonemapping_color_tint",
        "kscene.tonemapping_detail",
        "kscene.tonemapping_sharpen",
        "kscene.use_lens",
        "kscene.lens_distortion",
        "kscene.lens_axial_ca",
        "kscene.lens_lateral_ca",
        "kscene.lens_vignette_intensity",
        "kscene.lens_vignette_size",
        "kscene.lens_film_grain",
        "bpy.data.cameras[camera_name].show_sensor"
    ]

    preset_subdir = "cycles/kcycles_postfx"

class AddPresetKCyclesBloom(AddPresetBase, Operator):
    '''Add a K-Cycles Bloom Preset'''
    bl_idname = "render.cycles_kcycles_bloom_preset_add"
    bl_label = "Add K-Cycles Bloom Preset"
    preset_menu = "CYCLES_PT_kcycles_bloom_presets"

    preset_defines = [
        "kscene = bpy.context.scene.kcycles_postfx",
        "camera_name = bpy.context.scene.camera.data.name",
        "camera_mode = kscene.camera_mode",
        "camera_kcycles = bpy.data.cameras[camera_name].kcycles_postfx",
        "kscene = camera_kcycles if camera_mode == True else kscene"
    ]

    preset_values = [
        "kscene.bloom_threshold",
        "kscene.bloom_blend",
        "kscene.bloom_size",
        "kscene.bloom_intensity",
        "kscene.bloom_color_tint",
        "kscene.flares_threshold",
        "kscene.flares_glare_power",
        "kscene.flares_glare_rays",
        "kscene.flares_glare_rotation",
        "kscene.flares_glare_thin",
        "kscene.flares_glare_intensity",
        "kscene.flares_glare_color_shift",
        "kscene.flares_glare_color_tint",
        "kscene.flares_glare_softness",
        "kscene.flares_anamorphic_power",
        "kscene.flares_anamorphic_rotation",
        "kscene.flares_anamorphic_thin",
        "kscene.flares_anamorphic_intensity",
        "kscene.flares_anamorphic_color_shift",
        "kscene.flares_anamorphic_color_tint",
        "kscene.flares_anamorphic_softness",
        "kscene.flares_ghosts_intensity",
        "kscene.flares_ghosts_color_shift",
        "kscene.flares_ghosts_color_tint",
        "bpy.data.cameras[camera_name].show_sensor"
    ]

    preset_subdir = "cycles/kcycles_bloom"

class AddPresetKCyclesTonemapping(AddPresetBase, Operator):
    '''Add a K-Cycles Tone Mapping Preset'''
    bl_idname = "render.cycles_kcycles_tonemapping_preset_add"
    bl_label = "Add K-Cycles Tone Mapping Preset"
    preset_menu = "CYCLES_PT_kcycles_tonemapping_presets"

    preset_defines = [
        "kscene = bpy.context.scene.kcycles_postfx",
        "camera_name = bpy.context.scene.camera.data.name",
        "camera_mode = kscene.camera_mode",
        "camera_kcycles = bpy.data.cameras[camera_name].kcycles_postfx",
        "kscene = camera_kcycles if camera_mode == True else kscene"
    ]

    preset_values = [
        "kscene.tonemapping_exposure",
        "kscene.tonemapping_contrast",
        "kscene.tonemapping_highlights",
        "kscene.tonemapping_shadows",
        "kscene.tonemapping_color_boost",
        "kscene.tonemapping_saturation",
        "kscene.tonemapping_white_balance",
        "kscene.tonemapping_color_tint",
        "kscene.tonemapping_detail",
        "kscene.tonemapping_sharpen",
        "bpy.data.cameras[camera_name].show_sensor"
    ]

    preset_subdir = "cycles/kcycles_tonemapping"

class AddPresetKCyclesLens(AddPresetBase, Operator):
    '''添加 K-Cycles 镜头预设'''
    bl_idname = "render.cycles_kcycles_lens_preset_add"
    bl_label = "添加 K-Cycles 镜头预设"
    preset_menu = "CYCLES_PT_kcycles_lens_presets"

    preset_defines = [
        "kscene = bpy.context.scene.kcycles_postfx",
        "camera_name = bpy.context.scene.camera.data.name",
        "camera_mode = kscene.camera_mode",
        "camera_kcycles = bpy.data.cameras[camera_name].kcycles_postfx",
        "kscene = camera_kcycles if camera_mode == True else kscene"
    ]

    preset_values = [
        "kscene.lens_distortion",
        "kscene.lens_axial_ca",
        "kscene.lens_lateral_ca",
        "kscene.lens_vignette_intensity",
        "kscene.lens_vignette_size",
        "kscene.lens_film_grain",
        "bpy.data.cameras[camera_name].show_sensor"
    ]

    preset_subdir = "cycles/kcycles_lens"

class AddPresetKCyclesLightgroups(AddPresetBase, Operator):
    '''添加 K-Cycles 灯光组预设'''
    bl_idname = "render.cycles_kcycles_lightgroups_preset_add"
    bl_label = "添加 K-Cycles 灯光组预设"
    preset_menu = "CYCLES_PT_kcycles_lightgroups_presets"

    preset_defines = [
        "cycles = bpy.context.scene.cycles",
        "camera_name = bpy.context.scene.camera.data.name",
    ]

    preset_values = [
        "cycles.kcycles_lightgroups_list_values",
        "bpy.data.cameras[camera_name].show_sensor"
    ]

    preset_subdir = "cycles/kcycles_lightgroups"

classes = (
    AddPresetIntegrator,
    AddPresetSampling,
    AddPresetViewportSampling,
    AddPresetPerformance,
    AddPresetKCyclesPostFX,
    AddPresetKCyclesBloom,
    AddPresetKCyclesTonemapping,
    AddPresetKCyclesLens,
    AddPresetKCyclesLightgroups,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)


if __name__ == "__main__":
    register()
