import bpy

kscene = bpy.context.scene.kcycles_postfx
camera = bpy.context.scene.camera
if camera is not None and kscene.camera_mode:
    kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

kscene.tonemapping_exposure = 0.0
kscene.tonemapping_gamma = 1.0
kscene.tonemapping_contrast = 0.0
kscene.tonemapping_highlights = 0.0
kscene.tonemapping_shadows = 0.0
kscene.tonemapping_color_boost = 0.0
kscene.tonemapping_saturation = 1.0
kscene.tonemapping_white_balance = 0.0
kscene.tonemapping_color_tint = (1.0, 1.0, 1.0)
kscene.tonemapping_detail = 0
kscene.tonemapping_sharpen = 0.0

if camera is not None and bpy.context.scene.kcycles_postfx.camera_mode:
    bpy.data.cameras[camera.data.name].show_sensor = bpy.data.cameras[camera.data.name].show_sensor


