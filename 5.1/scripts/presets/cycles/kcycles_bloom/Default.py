import bpy

kscene = bpy.context.scene.kcycles_postfx
camera = bpy.context.scene.camera
if camera is not None and kscene.camera_mode:
    kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

kscene.bloom_threshold = 1.00
kscene.bloom_blend = 0.50
kscene.bloom_size = 0.15
kscene.bloom_intensity = 0.0
kscene.bloom_color_tint = (1.0,1.0,1.0)
kscene.flares_threshold = 1.0
kscene.flares_glare_power = 0.50
kscene.flares_glare_rays = 6
kscene.flares_glare_rotation = 30.0
kscene.flares_glare_thin = 0
kscene.flares_glare_intensity = 0.0
kscene.flares_glare_color_shift = 0.0
kscene.flares_glare_color_tint = (1.0, 1.0, 1.0)
kscene.flares_glare_softness = 0
kscene.flares_anamorphic_power = 0.50
kscene.flares_anamorphic_rotation = 0.0
kscene.flares_anamorphic_thin = 0
kscene.flares_anamorphic_intensity = 0.0
kscene.flares_anamorphic_color_shift = 0.0
kscene.flares_anamorphic_color_tint = (1.0, 1.0, 1.0)
kscene.flares_anamorphic_softness = 0
kscene.flares_ghosts_intensity = 0.0
kscene.flares_ghosts_color_shift = 0.0
kscene.flares_ghosts_color_tint = (1.0, 1.0, 1.0)

if camera is not None and bpy.context.scene.kcycles_postfx.camera_mode:
    bpy.data.cameras[camera.data.name].show_sensor = bpy.data.cameras[camera.data.name].show_sensor
