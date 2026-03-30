import bpy

kscene = bpy.context.scene.kcycles_postfx
camera = bpy.context.scene.camera
if camera is not None and kscene.camera_mode:
    kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

kscene.lens_distortion = 0.0
kscene.lens_axial_ca = 0.0
kscene.lens_lateral_ca = 0.0
kscene.lens_vignette_intensity = 0.0
kscene.lens_vignette_size = 0.5
kscene.lens_film_grain = 0.0

if camera is not None and bpy.context.scene.kcycles_postfx.camera_mode:
    bpy.data.cameras[camera.data.name].show_sensor = bpy.data.cameras[camera.data.name].show_sensor


