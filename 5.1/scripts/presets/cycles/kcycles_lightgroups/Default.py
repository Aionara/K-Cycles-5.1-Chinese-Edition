import bpy

cycles = bpy.context.scene.cycles
camera = bpy.context.scene.camera

cycles.kcycles_lightgroups_list_values = ""

if camera is not None and cycles.kcycles_lightgroup_camera_mode:
    bpy.data.cameras[camera.data.name].show_sensor = bpy.data.cameras[camera.data.name].show_sensor


