import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
    FloatVectorProperty,
)
from bpy.props import PointerProperty
from bpy.types import Panel, UIList
from bl_ui.utils import PresetPanel
from bpy.utils import register_class, unregister_class
from .properties import update_render_passes

import pathlib
import os

from . import kcycles_playback


def get_true(self):
    # Get true, use when the set is use as a function
    return True

def get_false(self):
    # Get false, use when the set is use as a function
    return False

class RenderPresetPanel(PresetPanel, Panel):
    COMPAT_ENGINES = {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
    preset_operator = "script.execute_preset"

    @staticmethod
    def post_cb(context, _filepath):
        # Modify an arbitrary built-in scene property to force a depsgraph
        # update, because add-on properties don't. (see T62325)
        render = context.scene.render
        render.filter_size = render.filter_size

class RenderButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {'CYCLES', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

def create_mask_string(mask_items):
    if (len(mask_items) > 0):
        mask_string = ""
        for item in mask_items:
            if (item.typ == "C"):
                collection = bpy.data.collections[item.name]
                for obj in [o for o in collection.all_objects if o.type == 'MESH']:
                    if (mask_string.find(obj.name) == -1):
                        mask_string += str(obj.name + ",")
            elif (item.typ == "M"):
                if (mask_string.find(item.name) == -1):
                    mask_string += str(item.name + ",")
        mask_string = mask_string[:-1]
        mask_count = len(mask_items)
    else:
        mask_string = ""
        mask_count = 0
    return mask_string, mask_count

enum_kcycles_bloom_mask_list = []
def enum_kcycles_bloom_mask_items(self, context):
    global enum_kcycles_bloom_mask_list
    enum_kcycles_bloom_mask_list = []
    scene = context.scene
    kscene = context.scene.kcycles_postfx
    camera = context.scene.camera
    if camera is not None and kscene.camera_mode:
        scene = bpy.data.cameras[camera.data.name]

    i = 0
    for item_data in scene.kcycles_bloom_mask_items:
        data = item_data.name
        icon_name = "PYTHON"
        if (item_data.typ == "M"):
            icon_name = "OUTLINER_OB_MESH"
        elif (item_data.typ == "C"):
            icon_name = "OUTLINER_COLLECTION"
        item = (str(i), data, "", icon_name, i)

        enum_kcycles_bloom_mask_list.append(item)
        i += 1

    return enum_kcycles_bloom_mask_list

enum_kcycles_tonemapping_mask_list = []
def enum_kcycles_tonemapping_mask_items(self, context):
    global enum_kcycles_tonemapping_mask_list
    enum_kcycles_tonemapping_mask_list = []
    scene = context.scene
    kscene = bpy.context.scene.kcycles_postfx
    camera = context.scene.camera
    if camera is not None and kscene.camera_mode:
        scene = bpy.data.cameras[camera.data.name]

    i = 0
    for item_data in scene.kcycles_tonemapping_mask_items:
        data = item_data.name
        icon_name = "PYTHON"
        if (item_data.typ == "M"):
            icon_name = "OUTLINER_OB_MESH"
        elif (item_data.typ == "C"):
            icon_name = "OUTLINER_COLLECTION"
        item = (str(i), data, "", icon_name, i)

        enum_kcycles_tonemapping_mask_list.append(item)
        i += 1

    return enum_kcycles_tonemapping_mask_list

def set_bloom_mask_add(self, value):
    scene = bpy.context.scene
    kscene = bpy.context.scene.kcycles_postfx
    camera = scene.camera
    if camera is not None and kscene.camera_mode:
        scene = bpy.data.cameras[camera.data.name]
        kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

    if (len(bpy.context.selected_objects) == 0 and len(bpy.context.collection.name) > 0):
        if bpy.context.collection.name not in scene.kcycles_bloom_mask_items:
            KCyclesItemList = scene.kcycles_bloom_mask_items.add()
            KCyclesItemList.typ = 'C'
            KCyclesItemList.name = bpy.context.collection.name
            if (len(scene.kcycles_bloom_mask_items) > 1):
                i = kscene.bloom_mask
                scene.kcycles_bloom_mask_items.move(len(scene.kcycles_bloom_mask_items) - 1, int(i))

    for item in bpy.context.selected_objects:
        if item.bl_rna.identifier == "Object":
            if item.type == 'MESH':
                if item.name not in scene.kcycles_bloom_mask_items:
                    KCyclesItemList = scene.kcycles_bloom_mask_items.add()
                    KCyclesItemList.typ = 'M'
                    KCyclesItemList.name = item.name
                    if (len(scene.kcycles_bloom_mask_items) > 1):
                        i = kscene.bloom_mask
                        scene.kcycles_bloom_mask_items.move(len(scene.kcycles_bloom_mask_items) - 1, int(i))

    kscene.bloom_mask_string, kscene.bloom_mask_count = create_mask_string(scene.kcycles_bloom_mask_items)

def set_bloom_mask_remove(self, value):
    scene = bpy.context.scene
    kscene = bpy.context.scene.kcycles_postfx
    camera = scene.camera
    if camera is not None and kscene.camera_mode:
        scene = bpy.data.cameras[camera.data.name]
        kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

    if len(scene.kcycles_bloom_mask_items) > 0:
        i = kscene.bloom_mask
        scene.kcycles_bloom_mask_items.remove(int(i))
        if (int(i) != 0 and int(i) == len(scene.kcycles_bloom_mask_items)):
            kscene.bloom_mask = str(len(scene.kcycles_bloom_mask_items) - 1)

    kscene.bloom_mask_string, kscene.bloom_mask_count = create_mask_string(scene.kcycles_bloom_mask_items)

def set_tonemapping_mask_add(self, value):
    scene = bpy.context.scene
    kscene = bpy.context.scene.kcycles_postfx
    camera = scene.camera
    if camera is not None and kscene.camera_mode:
        scene = bpy.data.cameras[camera.data.name]
        kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

    if (len(bpy.context.selected_objects) == 0 and len(bpy.context.collection.name) > 0):
        if bpy.context.collection.name not in scene.kcycles_tonemapping_mask_items:
            KCyclesItemList = scene.kcycles_tonemapping_mask_items.add()
            KCyclesItemList.typ = 'C'
            KCyclesItemList.name = bpy.context.collection.name
            if (len(scene.kcycles_tonemapping_mask_items) > 1):
                i = kscene.tonemapping_mask
                scene.kcycles_tonemapping_mask_items.move(len(scene.kcycles_tonemapping_mask_items) - 1, int(i))

    for item in bpy.context.selected_objects:
        if item.bl_rna.identifier == "Object":
            if item.type == 'MESH':
                if item.name not in scene.kcycles_tonemapping_mask_items:
                    KCyclesItemList = scene.kcycles_tonemapping_mask_items.add()
                    KCyclesItemList.typ = 'M'
                    KCyclesItemList.name = item.name
                    if (len(scene.kcycles_tonemapping_mask_items) > 1):
                        i = kscene.tonemapping_mask
                        scene.kcycles_tonemapping_mask_items.move(len(scene.kcycles_tonemapping_mask_items) - 1, int(i))

    kscene.tonemapping_mask_string, kscene.tonemapping_mask_count = create_mask_string(scene.kcycles_tonemapping_mask_items)

def set_tonemapping_mask_remove(self, value):
    scene = bpy.context.scene
    kscene = bpy.context.scene.kcycles_postfx
    camera = scene.camera
    if camera is not None and kscene.camera_mode:
        scene = bpy.data.cameras[camera.data.name]
        kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

    if len(scene.kcycles_tonemapping_mask_items) > 0:
        i = kscene.tonemapping_mask
        scene.kcycles_tonemapping_mask_items.remove(int(i))
        if (int(i) != 0 and int(i) == len(scene.kcycles_tonemapping_mask_items)):
            kscene.tonemapping_mask = str(len(scene.kcycles_tonemapping_mask_items) - 1)

    kscene.tonemapping_mask_string, kscene.tonemapping_mask_count = create_mask_string(scene.kcycles_tonemapping_mask_items)

def update_mask(context, node_group, nodes_postfx, type, mask_string, mask_invert):
    kc_mask_name = "KC_Mask_" + type
    input_mask_name = "Mask " + type
    invert_mask_name = "Invert_Mask_" + type
    mask_mix_name = "Mask_" + type + "_Mix"

    # Add or remove the mask
    if (not (kc_mask_name in node_group.nodes)) and len(mask_string) > 0:
        cryptomatte_node = node_group.nodes.new(type='CompositorNodeCryptomatteV2')
        cryptomatte_node.name = kc_mask_name
        cryptomatte_node.hide = True
        cryptomatte_node.width = 1
        cryptomatte_node.location.x = node_group.nodes["KC_PostFX"].location.x
        cryptomatte_node.location.y = node_group.nodes["KC_PostFX"].location.y + (cryptomatte_node.height / 4) + 10

        node_group.links.new(node_group.nodes[kc_mask_name].outputs["Matte"], node_group.nodes["KC_PostFX"].inputs[input_mask_name])
        nodes_postfx[invert_mask_name].mute = False
        nodes_postfx[mask_mix_name].mute = False

        # Get the active view layer and enable Cryptomatte pass
        view_layer = context.view_layer
        view_layer.use_pass_cryptomatte_object = True

    if (kc_mask_name in node_group.nodes):
        if len(mask_string) > 0:
            node_group.nodes[kc_mask_name].matte_id = mask_string
            nodes_postfx[invert_mask_name].inputs["Invert Color"].default_value = not mask_invert
        else:
            node_group.nodes.remove(node_group.nodes[kc_mask_name])
            nodes_postfx[mask_mix_name].mute = True
            nodes_postfx[invert_mask_name].mute = True

def update_kc_tonemapping(self, context):
    kscene = context.scene.kcycles_postfx
    camera = context.scene.camera
    if camera is not None and kscene.camera_mode:
        kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

    node_group = context.scene.compositing_node_group
    nodes_postfx = node_group.nodes["KC_PostFX"].node_tree.nodes
    nodes = nodes_postfx[".KC_Tone"].node_tree.nodes
    links = nodes_postfx[".KC_Tone"].node_tree.links

    mask_string = "" if not kscene.use_tonemapping else kscene.tonemapping_mask_string
    update_mask(context, node_group, nodes_postfx, "Tone", mask_string, kscene.tonemapping_mask_invert)

    # Mute .KC_Tone if needed
    nodes_postfx[".KC_Tone"].mute = False
    if not kscene.use_tonemapping:
        node_group.nodes["KC_PostFX"].node_tree.nodes[".KC_Tone"].mute = True
        return
    node_group.nodes["KC_PostFX"].node_tree.nodes[".KC_Tone"].mute = False

    nodes["Exposure"].inputs["Exposure"].default_value = kscene.tonemapping_exposure
    nodes["Gamma"].inputs["Gamma"].default_value = kscene.tonemapping_gamma
    nodes[".KC_Contrast"].inputs["Contrast"].default_value = 1.0 + ((kscene.tonemapping_contrast * 0.5) - 0.0) * 1.0

    shadows_higlights = nodes["RGB Curves"].mapping.curves[3]
    shadow = 0.25 + ((kscene.tonemapping_shadows - 0.0) * 0.25)
    shadows_higlights.points[1].location[1] = max(0.0, min(shadow, 0.50))
    highlight =  0.75 +  ((kscene.tonemapping_highlights - 0.0) * 0.25)
    shadows_higlights.points[2].location[1] =  max(0.50, min(highlight, 1))
    nodes["RGB Curves"].mapping.update()

    nodes[".KC_Color_Boost"].inputs["Color Boost"].default_value = kscene.tonemapping_color_boost + 1.0
    nodes[".KC_Saturation"].inputs["Saturation"].default_value = kscene.tonemapping_saturation
    nodes[".KC_White_Balance"].inputs["White Balance"].default_value = kscene.tonemapping_white_balance
    nodes["Mix"].inputs["B"].default_value = (kscene.tonemapping_color_tint[0], kscene.tonemapping_color_tint[1],
                                            kscene.tonemapping_color_tint[2], 1)
    nodes[".KC_Detail"].inputs["Detail"].default_value = kscene.tonemapping_detail
    if (kscene.tonemapping_sharpen >= 0):
        nodes["Filter"].inputs["Factor"].default_value = kscene.tonemapping_sharpen * 0.1
        nodes["Relative To Pixel"].inputs[0].default_value[0] = 0.0
        nodes["Relative To Pixel"].inputs[0].default_value[1] = 0.0
    else:
        nodes["Filter"].inputs["Factor"].default_value = 0.0
        nodes["Relative To Pixel"].inputs[0].default_value[0] = kscene.tonemapping_sharpen * -0.0005
        nodes["Relative To Pixel"].inputs[0].default_value[1] = kscene.tonemapping_sharpen * -0.0005

    return

def update_kc_bloom_flare(self, context):
    kscene = context.scene.kcycles_postfx
    camera = context.scene.camera
    if camera is not None and kscene.camera_mode:
        kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

    node_group = context.scene.compositing_node_group
    nodes_postfx = node_group.nodes["KC_PostFX"].node_tree.nodes
    nodes = nodes_postfx[".KC_Glare"].node_tree.nodes
    links = nodes_postfx[".KC_Glare"].node_tree.links

    mask_string = "" if not kscene.use_bloom else kscene.bloom_mask_string
    update_mask(context, node_group, nodes_postfx, "Glare", mask_string, kscene.bloom_mask_invert)

    nodes_postfx[".KC_Glare"].mute = False
    # Mute .KC_Bloom if needed
    if not kscene.use_bloom:
        nodes_postfx[".KC_Glare"].mute = True
        return
    nodes_postfx[".KC_Glare"].mute = False

    nodes["KC_Bloom"].inputs["Threshold"].default_value = kscene.bloom_threshold
    nodes["KC_Bloom"].inputs["Strength"].default_value = kscene.bloom_intensity *  kscene.bloom_intensity
    nodes["Blend"].outputs[0].default_value = kscene.bloom_blend

    nodes["KC_Bloom"].inputs["Size"].default_value = kscene.bloom_size
    nodes["KC_Bloom"].inputs["Tint"].default_value = (kscene.bloom_color_tint[0], kscene.bloom_color_tint[1],
                                            kscene.bloom_color_tint[2], 1)

    nodes["KC_Streaks"].inputs["Threshold"].default_value = kscene.flares_threshold
    nodes["KC_Streaks"].inputs["Strength"].default_value = kscene.flares_glare_intensity * kscene.flares_glare_intensity
    nodes["KC_Streaks"].inputs["Streaks"].default_value = kscene.flares_glare_rays
    nodes["KC_Streaks"].inputs["Streaks Angle"].default_value = kscene.flares_glare_rotation * 3.14159 * 0.005556
    nodes["Dilate_Erode_Streaks"].inputs["Size"].default_value = kscene.flares_glare_thin
    nodes["KC_Streaks"].inputs["Fade"].default_value = 0 if (kscene.flares_glare_power == 0) else ((kscene.flares_glare_power * 0.3) + 0.700)
    nodes["KC_Streaks"].inputs["Color Modulation"].default_value = kscene.flares_glare_color_shift
    nodes["KC_Streaks"].inputs["Tint"].default_value = (kscene.bloom_color_tint[0], kscene.bloom_color_tint[1],
                                            kscene.bloom_color_tint[2], 1)
    nodes["Blur_Streaks"].inputs["Size"].default_value[0] = kscene.flares_glare_softness
    nodes["Blur_Streaks"].inputs["Size"].default_value[1] = kscene.flares_glare_softness

    nodes["KC_Anamorphic"].inputs["Threshold"].default_value = kscene.flares_threshold
    nodes["KC_Anamorphic"].inputs["Strength"].default_value = kscene.flares_anamorphic_intensity * kscene.flares_anamorphic_intensity
    nodes["KC_Anamorphic"].inputs["Streaks Angle"].default_value = kscene.flares_anamorphic_rotation * 3.14159 * 0.005556
    nodes["Dilate_Erode_Anamorphic"].inputs["Size"].default_value = kscene.flares_anamorphic_thin
    nodes["KC_Anamorphic"].inputs["Fade"].default_value = 0 if (kscene.flares_anamorphic_power == 0) else ((kscene.flares_anamorphic_power * 0.3) + 0.700)
    nodes["KC_Anamorphic"].inputs["Color Modulation"].default_value = kscene.flares_glare_color_shift
    nodes["KC_Anamorphic"].inputs["Tint"].default_value = (kscene.bloom_color_tint[0], kscene.bloom_color_tint[1],
                                            kscene.bloom_color_tint[2], 1)
    nodes["Blur_Anamorphic"].inputs["Size"].default_value[0] = kscene.flares_anamorphic_softness
    nodes["Blur_Anamorphic"].inputs["Size"].default_value[1] = kscene.flares_anamorphic_softness

    nodes["KC_Ghost"].inputs["Threshold"].default_value = kscene.flares_threshold
    nodes["KC_Ghost"].inputs["Strength"].default_value = kscene.flares_ghosts_intensity * kscene.flares_ghosts_intensity
    nodes["KC_Ghost"].inputs["Tint"].default_value = (kscene.bloom_color_tint[0], kscene.bloom_color_tint[1],
                                            kscene.bloom_color_tint[2], 1)
    nodes["KC_Ghost"].inputs["Color Modulation"].default_value = kscene.flares_ghosts_color_shift

    return

def update_kc_lens(self, context):
    kscene = context.scene.kcycles_postfx
    camera = context.scene.camera
    if camera is not None and kscene.camera_mode:
        kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

    node_group = context.scene.compositing_node_group
    nodes_postfx = node_group.nodes["KC_PostFX"].node_tree.nodes
    nodes = nodes_postfx[".KC_Lens"].node_tree.nodes
    links = nodes_postfx[".KC_Lens"].node_tree.links

    node_group.nodes["KC_PostFX"].node_tree.nodes[".KC_Lens"].mute = False

    # Mute .KC_Lens if needed
    if not kscene.use_lens:
        nodes_postfx[".KC_Lens"].mute = True
        return

    nodes_postfx[".KC_Lens"].mute = False

    nodes["Lens_Distortion"].inputs["Distortion"].default_value = kscene.lens_distortion * 0.15
    nodes["Lens_Axial_CA"].inputs["Dispersion"].default_value = kscene.lens_axial_ca
    nodes["Lens_Distortion"].inputs["Dispersion"].default_value = kscene.lens_lateral_ca * 0.1

    nodes["KC_Vignette_Strength"].outputs[0].default_value = kscene.lens_vignette_intensity
    nodes["KC_Vignette_Size"].outputs[0].default_value = kscene.lens_vignette_size
    nodes["KC_Luma_Noise"].outputs[0].default_value = kscene.lens_film_grain

    return

def append_kcycles_node(node_name):
    path = os.path.join(bpy.utils.resource_path('LOCAL'), "datafiles", "kcycles")
    blendfile = "kcycles_assets.blend"
    filepath = path + os.path.sep + blendfile

    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.node_groups = [node_name]

def get_node_id(nodes, id_name):
    node_id = []
    for node in nodes:
        if node.bl_idname == id_name:
            node_id = node
    return node_id

def update_use_postfx(self, context):
    #print("update_use_postfx")
    view_layer = context.view_layer
    scene = context.scene
    cscene = context.scene.cycles
    scene.render.compositor_device = "GPU" if not scene.render.compositor_device == "GPU" else "CPU"

    kscene = scene.kcycles_postfx
    camera = scene.camera
    if camera is not None and kscene.camera_mode:
        kscene = bpy.data.cameras[camera.data.name].kcycles_postfx
    
    # Create or get the compositing node group only post_fx is enable
    node_group = []
    if not scene.compositing_node_group:
        if kscene.use_postfx:
            node_group = scene.compositing_node_group = bpy.data.node_groups.new('Compositing Nodes', 'CompositorNodeTree')
        else:
            return
    else:
        node_group = scene.compositing_node_group

    # Create or get the render layers and output nodes.
    render_layers = get_node_id(node_group.nodes, "CompositorNodeRLayers")
    if not render_layers:
        render_layers = node_group.nodes.new(type="CompositorNodeRLayers")
        render_layers.select = False
    group_output = get_node_id(node_group.nodes, "NodeGroupOutput")
    if not group_output:
        group_output = node_group.nodes.new(type="NodeGroupOutput")
        node_group.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        group_output.select = False
    viewer_output = get_node_id(node_group.nodes, "CompositorNodeViewer")
    if not viewer_output:
        viewer_output = node_group.nodes.new(type="CompositorNodeViewer")
        viewer_output.select = False
 

    # Hide KC_PostFX
    if not kscene.use_postfx:
        if "KC_PostFX" in node_group.nodes:
             node_group.nodes["KC_PostFX"].mute = True
             for node in node_group.nodes:
                if "KC_Mask_" in node.name:
                    node.mute = True
             return
        """
        for node in node_group.nodes:
            if "KC_" in node.name:
                node_group.nodes.remove(node)
        for node in bpy.data.node_groups:
            if "KC_" in node.name:
               bpy.data.node_groups.remove(node)
        node_group.links.new(render_layers.outputs[0], node_group.nodes['Group Output'].inputs[0])
        if ("Viewer" in  node_group.nodes):
            node_group.links.new(render_layers.outputs[0], node_group.nodes['Viewer'].inputs[0])
        return
        """
    else:
        if not "KC_PostFX" in node_group.nodes:
            if not scene.render.use_compositing:
                scene.render.use_compositing = True            

            # Append and create a KC_PostFX node group
            if not "KC_PostFX" in bpy.data.node_groups:
                append_kcycles_node(node_name="KC_PostFX")

            kc_postfx_node = node_group.nodes.new("CompositorNodeGroup")
            kc_postfx_node.name = "KC_PostFX"
            kc_postfx_node.node_tree = bpy.data.node_groups["KC_PostFX"]
            kc_postfx_node.node_tree.name = "KC_PostFX"
            kc_postfx_node.location = (render_layers.location[0] + 350, render_layers.location[1] - 50)
            kc_postfx_node.select = False

            # Link kc_postfx_node to Render Layer, Composite and Viewer nodes
            link_input = kcycles_playback.node_input_socket_link(node_group, "Group Output", "Image")
            if (link_input != None):
                node_group.links.new(kc_postfx_node.inputs[0], link_input.from_node.outputs[link_input.from_socket.name])
            else:
                node_group.links.new(kc_postfx_node.inputs[0], node_group.nodes["Render Layers"].outputs[0])
            node_group.links.new(kc_postfx_node.outputs[0], node_group.nodes["Group Output"].inputs[0])
            node_group.nodes["Group Output"].location = (kc_postfx_node.location.x + kc_postfx_node.width + 50, kc_postfx_node.location.y)

            if ("KC_ScaleView" in node_group.nodes):
                node_group.links.new(kc_postfx_node.outputs[0], node_group.nodes['KC_ScaleView'].inputs["Image"])
            else:
                node_group.links.new(kc_postfx_node.outputs[0], node_group.nodes['Viewer'].inputs[0])
            node_group.nodes['Viewer'].location = (node_group.nodes['Group Output'].location.x, node_group.nodes['Group Output'].location.y - node_group.nodes['Viewer'].height)

        node_group.nodes["KC_PostFX"].mute = False
        for node in node_group.nodes:
            if "KC_Mask_" in node.name:
                node.mute = False

        # Viewport compositor
        if (context.scene.kcycles_playback.use_playback):
            kcycles_playback.set_viewport_compositor(self, context)
        else:
            for workspace in bpy.data.workspaces:
                for screen in workspace.screens:
                    for area in screen.areas:
                        if area.type == 'VIEW_3D':
                            area.spaces[0].shading.use_compositor = 'ALWAYS'

        # Update the postfx values
        update_kc_bloom_flare(self, context)
        update_kc_tonemapping(self, context)
        update_kc_lens(self, context)

class KCyclesPostFXSettings(bpy.types.PropertyGroup):
    camera_mode: BoolProperty(
        name="相机模式后期特效",
        description="每个相机拥有独立的后期特效设置",
        default=False,
        update=update_use_postfx,
    )

    use_postfx: BoolProperty(
        name="使用后期特效",
        description="启用/禁用所有后期特效",
        default=False,
        update=update_use_postfx,
    )

    extend_alpha_film_transparent: BoolProperty(
        name="扩展透明胶片 Alpha",
        description="为透明胶片扩展后期特效的 Alpha",
        default=True,
    )

    use_bloom: BoolProperty(
        name="使用辉光和光晕",
        description="高亮度像素产生发光和光晕效果",
        default=False,
        update=update_kc_bloom_flare,
    )

    bloom_threshold: FloatProperty(
        name="辉光阈值",
        description="过滤低于亮度阈值的像素",
        min=0.0, max=100000.0, soft_min=0.0, soft_max=10.0, precision=2,
        default=1.0,
        update=update_kc_bloom_flare,
    )

    bloom_blend: FloatProperty(
        name="混合",
        description="将辉光效果混合到场景中",
        min=0.0, max=1.0,
        default=0.5,
        update=update_kc_bloom_flare,
    )

    bloom_size: FloatProperty(
        name="大小",
        description="辉光扩散距离",
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, precision=2,
        default=0.15,
        update=update_kc_bloom_flare,
    )

    bloom_color_tint: FloatVectorProperty(
        name="色彩色调",
        subtype="COLOR",
        description="调整辉光效果的整体色彩色调",
        size=3,
        min=0.0, max=1.0,
        default=(1.0,1.0,1.0),
        update=update_kc_bloom_flare,
    )

    bloom_intensity: FloatProperty(
        name="强度",
        description="辉光的亮度",
        min=0.0, max=100.0, soft_min=0.0, soft_max=5.0, precision=2,
        default=0.0,
        update=update_kc_bloom_flare,
    )

    bloom_mask: EnumProperty(
        name="遮罩",
        description="遮罩列表",
        items=enum_kcycles_bloom_mask_items,
    )

    bloom_mask_string: StringProperty(
        default="",
    )

    bloom_mask_count: IntProperty(
        name="遮罩数量",
        subtype="UNSIGNED",
        description="辉光遮罩项目总数",
        default=0,
    )

    bloom_mask_invert: BoolProperty(
        name="遮罩反转",
        description="反转遮罩",
        default=False,
        update=update_kc_bloom_flare,
    )

    bloom_mask_add: BoolProperty(
        name="添加遮罩项",
        description="添加遮罩项到辉光",
        set=set_bloom_mask_add,
        get=get_false,
        default=False,
        update=update_kc_bloom_flare,
    )

    bloom_mask_remove: BoolProperty(
        name="移除遮罩项",
        description="从辉光中移除遮罩项",
        set=set_bloom_mask_remove,
        get=get_false,
        default=False,
        update=update_kc_bloom_flare,
    )

    flares_threshold: FloatProperty(
        name="光晕阈值",
        description="过滤低于亮度阈值的像素",
        min=0.0, max=100000.0, soft_min=0.0, soft_max=10.0, precision=2,
        default=1.0,
        update=update_kc_bloom_flare,
    )

    flares_glare_intensity: FloatProperty(
        name="强度",
        description="眩光光晕的亮度",
        min=0.0, max=10.0, soft_min=0.0, soft_max=5.0, precision=2,
        default=0.0,
        update=update_kc_bloom_flare,
    )

    flares_glare_power: FloatProperty(
        name="大小",
        description="眩光光晕的大小",
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, precision=2,
        default=0.5,
        update=update_kc_bloom_flare,
    )

    flares_glare_rays: IntProperty(
        name="光线",
        subtype="UNSIGNED",
        description="眩光的光线数量",
        min=0, max=16,
        default=6,
        update=update_kc_bloom_flare,
    )

    flares_glare_rotation: FloatProperty(
        name="旋转",
        description="眩光光晕的旋转角度",
        min=-180.0, max=180.0, precision=1,
        default=30.0,
        update=update_kc_bloom_flare,
    )

    flares_glare_thin: IntProperty(
        name="厚度级别",
        subtype="UNSIGNED",
        description="减少眩光光线的厚度",
        min=-20, max=20, soft_min=-10, soft_max=10,
        default=0,
        update=update_kc_bloom_flare,
    )

    flares_glare_color_shift: FloatProperty(
        name="色彩偏移",
        description="眩光光晕的色彩变化",
        min=0.0, max=1.0, precision=2,
        default=0.0,
        update=update_kc_bloom_flare,
    )

    flares_glare_color_tint: FloatVectorProperty(
        name="色彩色调",
        subtype="COLOR",
        description="调整眩光光晕的整体色彩色调",
        size=3,
        min=0.0, max=1.0,
        default=(1.0,1.0,1.0),
        update=update_kc_bloom_flare,
    )

    flares_glare_softness: IntProperty(
        name="柔和度",
        subtype="UNSIGNED",
        description="眩光光晕的柔和度级别",
        min=0, max=100, soft_min=0, soft_max=25,
        default=0,
        update=update_kc_bloom_flare,
    )

    flares_anamorphic_intensity: FloatProperty(
        name="强度",
        description="变形光晕的亮度",
        min=0.0, max=10.0, soft_min=0.0, soft_max=5.0, precision=2,
        default=0.0,
        update=update_kc_bloom_flare,
    )
    
    flares_anamorphic_power: FloatProperty(
        name="大小",
        description="变形光晕的大小",
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, precision=2,
        default=0.5,
        update=update_kc_bloom_flare,
    )

    flares_anamorphic_rotation: FloatProperty(
        name="旋转",
        description="变形光晕的旋转角度",
        min=-180.0, max=180.0, precision=1,
        default=0.0,
        update=update_kc_bloom_flare,
    )

    flares_anamorphic_thin: IntProperty(
        name="厚度级别",
        subtype="UNSIGNED",
        description="减少变形光晕的厚度",
        min=-20, max=20, soft_min=-10, soft_max=10,
        default=0,
        update=update_kc_bloom_flare,
    )

    flares_anamorphic_color_shift: FloatProperty(
        name="色彩偏移",
        description="变形光晕的色彩变化",
        min=0.0, max=1.0, precision=2,
        default=0.0,
        update=update_kc_bloom_flare,
    )

    flares_anamorphic_color_tint: FloatVectorProperty(
        name="色彩色调",
        subtype="COLOR",
        description="调整变形光晕的整体色彩色调",
        size=3,
        min=0.0, max=1.0,
        default=(1.0,1.0,1.0),
        update=update_kc_bloom_flare,
    )

    flares_anamorphic_softness: IntProperty(
        name="柔和度",
        subtype="UNSIGNED",
        description="变形光晕的柔和度级别",
        min=0, max=100, soft_min=0, soft_max=25,
        default=0,
        update=update_kc_bloom_flare,
    )

    flares_ghosts_intensity: FloatProperty(
        name="强度",
        description="鬼影光晕的强度",
        min=0.0, max=10.0, soft_min=0.0, soft_max=5.0, precision=2,
        default=0.0,
        update=update_kc_bloom_flare,
    )

    flares_ghosts_color_shift: FloatProperty(
        name="色彩偏移",
        description="鬼影光晕的色彩变化",
        min=0.0, max=1.0, precision=2,
        default=0.0,
        update=update_kc_bloom_flare,
    )

    flares_ghosts_color_tint: FloatVectorProperty(
        name="色彩色调",
        subtype="COLOR",
        description="调整鬼影光晕的整体色彩色调",
        size=3,
        min=0.0, max=1.0,
        default=(1.0,1.0,1.0),
        update=update_kc_bloom_flare,
    )

    use_lens: BoolProperty(
        name="使用镜头",
        description="使用镜头",
        default=False,
        update=update_kc_lens,
    )

    lens_distortion: FloatProperty(
        name="畸变",
        description="调整图像中心的凸起或收缩效果",
        min=-2.0, max=2.0, soft_min=-1.0, soft_max=1.0, precision=2,
        default=0.0,
        update=update_kc_lens,
    )

    lens_axial_ca: FloatProperty(
        name="轴向色差",
        description="调整轴向色差，即每种波长光的长度变化",
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, precision=2,
        default=0.0,
        update=update_kc_lens,
    )

    lens_lateral_ca: FloatProperty(
        name="横向色差",
        description="调整横向色差色边。仅影响图像边缘",
        min=0.0, max=3.0, soft_min=0.0, soft_max=3.0, precision=2,
        default=0.0,
        update=update_kc_lens,
    )

    lens_vignette_intensity: FloatProperty(
        name="暗角强度",
        description="调整图像边缘亮度降低的程度",
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, precision=2,
        default=0.0,
        update=update_kc_lens,
    )

    lens_vignette_size: FloatProperty(
        name="暗角大小",
        description="调整暗角的大小",
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, precision=2,
        default=0.5,
        update=update_kc_lens,
    )

    lens_film_grain: FloatProperty(
        name="胶片颗粒",
        description="为图像添加摄影颗粒/噪点",
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, precision=2,
        default=0.0,
        update=update_kc_lens,
    )

    use_tonemapping: BoolProperty(
        name="使用色调映射",
        description="使用色调映射",
        default=False,
        update = update_kc_tonemapping,
    )

    tonemapping_mask: EnumProperty(
        name="遮罩",
        description="遮罩列表",
        items=enum_kcycles_tonemapping_mask_items,
    )

    tonemapping_mask_string: StringProperty(
        default="",
    )

    tonemapping_mask_count: IntProperty(
        name="遮罩数量",
        subtype="UNSIGNED",
        description="色调映射遮罩项目总数",
        default=0,
    )

    tonemapping_mask_invert: BoolProperty(
        name="遮罩反转",
        description="反转遮罩",
        default=False,
        update = update_kc_tonemapping,
    )

    tonemapping_mask_add: BoolProperty(
        name="添加遮罩项",
        description="添加遮罩项到色调映射",
        set=set_tonemapping_mask_add,
        get=get_false,
        default=False,
        update = update_kc_tonemapping,
    )

    tonemapping_mask_remove: BoolProperty(
        name="移除遮罩项",
        description="从色调映射中移除遮罩项",
        set=set_tonemapping_mask_remove,
        get=get_false,
        default=False,
        update = update_kc_tonemapping,
    )

    tonemapping_exposure: FloatProperty(
        name="曝光",
        description="调整图像的整体曝光",
        min=-10.0, max=10.0, soft_min=-5.0, soft_max=5.0, precision=2,
        default=0.0,
        update = update_kc_tonemapping,
    )

    tonemapping_gamma: FloatProperty(
        name="伽马",
        description="调整图像的整体伽马值",
        min=0.0, max=5.0, soft_min=0.0, soft_max=5.0, precision=2,
        default=1.0,
        update = update_kc_tonemapping,
    )

    tonemapping_contrast: FloatProperty(
        name="对比度",
        description="调整图像的对比度",
        min=-1.0, max=1.0, soft_min=-1.0, soft_max=1.0, precision=2,
        default=0.0,
        update = update_kc_tonemapping,
    )

    tonemapping_highlights: FloatProperty(
        name="高光",
        description="调整图像的亮部区域",
        min=-1.0, max=1.0, soft_min=-1.0, soft_max=1.0, precision=2,
        default=0.0,
        update = update_kc_tonemapping,
    )

    tonemapping_shadows: FloatProperty(
        name="阴影",
        description="调整图像的暗部区域",
        min=-1.0, max=1.0, soft_min=-1.0, soft_max=1.0, precision=2,
        default=0.0,
        update = update_kc_tonemapping,
    )

    tonemapping_saturation: FloatProperty(
        name="饱和度",
        description="调整渲染的色彩饱和度",
        min=0.0, max=10.0, soft_min=0.0, soft_max=3.0, precision=2,
        default=1.0,
        update = update_kc_tonemapping,
    )

    tonemapping_color_boost: FloatProperty(
        name="色彩增强",
        description="调整渲染的色彩增强程度",
        min=0.0, max=5.0, soft_min=0.0, soft_max=2.0, precision=2,
        default=0.0,
        update = update_kc_tonemapping,
    )

    tonemapping_white_balance: FloatProperty(
        name="白平衡",
        description="控制图像的白平衡",
        min=-1.0, max=1.0, precision=2,
        default=0.0,
        update = update_kc_tonemapping,
    )

    tonemapping_color_tint: FloatVectorProperty(
        name="色彩色调",
        subtype="COLOR",
        description="调整图像的整体色彩色调",
        size=3,
        min=0.0, max=1.0,
        default=(1.0,1.0,1.0),
        update = update_kc_tonemapping,
    )

    tonemapping_detail: FloatProperty(
        name="细节",
        description="调整图像的细节量",
        min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, precision=2,
        default=0.0,
        update = update_kc_tonemapping,
    )

    tonemapping_sharpen: FloatProperty(
        name="锐化",
        description="调整图像的锐化程度",
        min=-20.0, max=20.0, soft_min=-10.0, soft_max=10.0, precision=2,
        default=0.0,
        update = update_kc_tonemapping,
    )

class CYCLES_PT_kcycles_postfx_presets(RenderPresetPanel):
    bl_label = "K-Cycles 后期特效预设"
    preset_subdir = "cycles/kcycles_postfx"
    preset_add_operator = "render.cycles_kcycles_postfx_preset_add"

class CYCLES_PT_kcycles_bloom_presets(RenderPresetPanel):
    bl_label = "K-Cycles 辉光预设"
    preset_subdir = "cycles/kcycles_bloom"
    preset_add_operator = "render.cycles_kcycles_bloom_preset_add"

class CYCLES_PT_kcycles_tonemapping_presets(RenderPresetPanel):
    bl_label = "K-Cycles 色调映射预设"
    preset_subdir = "cycles/kcycles_tonemapping"
    preset_add_operator = "render.cycles_kcycles_tonemapping_preset_add"

class CYCLES_PT_kcycles_lens_presets(RenderPresetPanel):
    bl_label = "K-Cycles 镜头预设"
    preset_subdir = "cycles/kcycles_lens"
    preset_add_operator = "render.cycles_kcycles_lens_preset_add"

class RENDER_PT_kcycles_postfx(RenderButtonsPanel, Panel):
    bl_label = "后期特效"
    bl_parent_id = "RENDER_PT_kcycles"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header_preset(self, context):
        CYCLES_PT_kcycles_postfx_presets.draw_panel_header(self.layout)

    def draw_header(self, context):
        kscene = context.scene.kcycles_postfx
        camera = context.scene.camera
        if camera is not None and kscene.camera_mode:
            kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

        self.layout.prop(kscene, "use_postfx", text="")
        self.layout.prop(context.scene.kcycles_postfx, "camera_mode", icon="OUTLINER_DATA_CAMERA", text="")

    def draw(self, context):
        layout = self.layout
        kscene = context.scene.kcycles_postfx
        camera = context.scene.camera
        if camera is not None and kscene.camera_mode:
            kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

        #if (context.scene.render.film_transparent):
        #    row = layout.row(align=False)
        #    split = row.split(factor = 0.1, align=False)
        #    split.active = kscene.use_postfx
        #    split.label(text = "")
        #    split.prop(kscene, "extend_alpha_film_transparent", text="Extend Alpha for Film Transparent")
        return

class RENDER_PT_kcycles_effects_viewport_match(RenderButtonsPanel, Panel):
    bl_label = "视口匹配输出分辨率"
    bl_parent_id = "RENDER_PT_kcycles_postfx"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        cscene = context.scene.cycles

        layout.prop(cscene, "kcycles_viewport_match_output_resolution", text="")

    def draw(self, context):
        layout = self.layout
        cscene = context.scene.cycles
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.active = cscene.kcycles_viewport_match_output_resolution
        col.prop(cscene, "kcycles_viewport_pan_horizontal", text="水平平移")
        col.prop(cscene, "kcycles_viewport_pan_vertical", text="垂直平移")

class RENDER_PT_kcycles_effects_bloom_flares(RenderButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "RENDER_PT_kcycles_postfx"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header_preset(self, context):
        CYCLES_PT_kcycles_bloom_presets.draw_panel_header(self.layout)

    def draw_header(self, context):
        layout = self.layout
        kscene = context.scene.kcycles_postfx
        camera = context.scene.camera
        if camera is not None and kscene.camera_mode:
            kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

        layout.active = kscene.use_postfx
        layout.prop(kscene, "use_bloom", text="辉光和光晕")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        kscene = context.scene.kcycles_postfx
        camera = context.scene.camera
        if camera is not None and kscene.camera_mode:
            kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

        layout.active = kscene.use_postfx and kscene.use_bloom

        layout.use_property_split = False
        layout.use_property_decorate = False
        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_x = 1.30
        row.prop(kscene, "bloom_mask", text="遮罩", icon="MOD_MASK")
        sub = row.row(align=True)
        sub.alignment = 'RIGHT'
        sub.scale_x = 1.0
        sub.prop(kscene, "bloom_mask_add", text="", icon="ADD")
        sub.prop(kscene, "bloom_mask_remove", text="", icon="REMOVE")
        sub.prop(kscene, "bloom_mask_invert", icon="ARROW_LEFTRIGHT", text="")

        box = self.layout.box()
        col = box.column()
        row = col.split(factor=0.19, align = True)
        row.label(text='  混合')
        row = row.split(factor=0.55, align = True)
        row.prop(kscene, "bloom_blend", text="", slider=True)
        row.label(text='')

        row = col.split(factor=0.19, align = True)
        row.label(text='  阈值,')
        row = row.split(factor=0.53, align = True)
        row.prop(kscene, "bloom_threshold", text="辉光", slider=True)
        row.prop(kscene, "flares_threshold", text="光晕", slider=True)

        row = col.split(factor=0.19, align = True)
        row.label(text='  颜色')
        row = row.split(factor=0.53, align = True)
        row.prop(kscene, "bloom_color_tint", text="")
        row.prop(kscene, "flares_glare_color_shift", text="偏移", slider=True)

        layout.active = kscene.use_postfx and kscene.use_bloom
        box = self.layout.box()
        col = box.column()
        row = col.split(factor=0.19, align = True)
        row.label(text='  辉光')
        row = row.split(factor=0.53, align = True)
        row.prop(kscene, "bloom_intensity", text="强度", slider=True)
        row.prop(kscene, "bloom_size", text="大小", slider=True)

        box = self.layout.box()
        col = box.column()
        row = col.split(factor=0.19, align = True)
        row.label(text='  条纹')
        row = row.split(factor=0.53, align = True)
        row.prop(kscene, "flares_glare_intensity", text="强度", slider=True)
        row.prop(kscene, "flares_glare_power", text="长度", slider=True)

        row = col.split(factor=0.19, align = True)
        row.label(text='')
        row = row.split(factor=0.53, align = True)
        row.enabled = kscene.flares_glare_intensity > 0
        row.prop(kscene, "flares_glare_rays", text="光线", slider=True)
        row.prop(kscene, "flares_glare_rotation", text="角度", slider=True)

        row = col.split(factor=0.19, align = True)
        row.label(text='')
        row = row.split(factor=0.52, align = True)
        row.enabled = kscene.flares_glare_intensity > 0
        row.prop(kscene, "flares_glare_thin", text="细度  ", slider=True)
        row.prop(kscene, "flares_glare_softness", text="柔和  ", slider=True)

        box = self.layout.box()
        col = box.column()
        row = col.split(factor=0.19, align = True)
        row.label(text='  变形')
        row = row.split(factor=0.55, align = True)
        row.prop(kscene, "flares_anamorphic_intensity", text="强度", slider=True)
        row.label(text='')

        row = col.split(factor=0.19, align = True)
        row.label(text='')
        row = row.split(factor=0.53, align = True)
        row.enabled = kscene.flares_anamorphic_intensity > 0
        row.prop(kscene, "flares_anamorphic_power", text="长度", slider=True)
        row.prop(kscene, "flares_anamorphic_rotation", text="角度", slider=True)

        row = col.split(factor=0.19, align = True)
        row.label(text='')
        row = row.split(factor=0.53, align = True)
        row.enabled = kscene.flares_anamorphic_intensity > 0
        row.prop(kscene, "flares_anamorphic_thin", text="细度  ", slider=True)
        row.prop(kscene, "flares_anamorphic_softness", text="柔和  ", slider=True)

        box = self.layout.box()
        col = box.column()
        row = col.split(factor=0.19, align = True)
        row.label(text='  鬼影')
        row = row.split(factor=0.55, align = True)
        row.prop(kscene, "flares_ghosts_intensity", text="强度", slider=True)
        row.prop(kscene, "flares_ghosts_color_shift", text="偏移", slider=True)

class RENDER_PT_kcycles_effects_tonemapping(RenderButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "RENDER_PT_kcycles_postfx"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header_preset(self, context):
        CYCLES_PT_kcycles_tonemapping_presets.draw_panel_header(self.layout)

    def draw_header(self, context):
        layout = self.layout
        kscene = context.scene.kcycles_postfx
        camera = context.scene.camera
        if camera is not None and kscene.camera_mode:
            kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

        layout.active = kscene.use_postfx
        layout.prop(kscene, "use_tonemapping", text="色调和颜色")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        kscene = context.scene.kcycles_postfx
        camera = context.scene.camera
        if camera is not None and kscene.camera_mode:
            kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

        layout.active = kscene.use_postfx and kscene.use_tonemapping
        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row()
        row.prop(kscene, "tonemapping_mask", text="遮罩", icon="MOD_MASK")
        row.prop(kscene, "tonemapping_mask_add", text="", icon="ADD")
        row.prop(kscene, "tonemapping_mask_remove", text="", icon="REMOVE")
        row.prop(kscene, "tonemapping_mask_invert", icon="ARROW_LEFTRIGHT", text="")

        col = layout.column(align=True)
        col.prop(kscene, "tonemapping_exposure", slider=True)
        col.prop(kscene, "tonemapping_gamma", slider=True)
        col.prop(kscene, "tonemapping_contrast", slider=True)
        col.prop(kscene, "tonemapping_highlights", slider=True)
        col.prop(kscene, "tonemapping_shadows", slider=True)
        col.prop(kscene, "tonemapping_color_boost", slider=True)
        col.prop(kscene, "tonemapping_saturation", slider=True)
        col.prop(kscene, "tonemapping_white_balance", slider=True)
        col.prop(kscene, "tonemapping_color_tint")
        col.prop(kscene, "tonemapping_detail", slider=True)
        col.prop(kscene, "tonemapping_sharpen", slider=True)

class RENDER_PT_kcycles_effects_lens(RenderButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "RENDER_PT_kcycles_postfx"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header_preset(self, context):
        CYCLES_PT_kcycles_lens_presets.draw_panel_header(self.layout)

    def draw_header(self, context):
        layout = self.layout
        kscene = context.scene.kcycles_postfx
        camera = context.scene.camera
        if camera is not None and kscene.camera_mode:
            kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

        layout.active = kscene.use_postfx
        layout.prop(kscene, "use_lens", text="镜头")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        kscene = context.scene.kcycles_postfx
        camera = context.scene.camera
        if camera is not None and kscene.camera_mode:
            kscene = bpy.data.cameras[camera.data.name].kcycles_postfx

        layout.active = kscene.use_postfx and kscene.use_lens
        col = layout.column(align=True)
        col.prop(kscene, "lens_distortion", slider=True)
        col.prop(kscene, "lens_axial_ca", slider=True)
        col.prop(kscene, "lens_lateral_ca", slider=True)
        col.prop(kscene, "lens_vignette_intensity", slider=True)
        col.prop(kscene, "lens_vignette_size", slider=True)
        col.prop(kscene, "lens_film_grain", slider=True)

classes = (
    RENDER_PT_kcycles_effects_viewport_match,
    RENDER_PT_kcycles_effects_tonemapping,
    RENDER_PT_kcycles_effects_bloom_flares,
    RENDER_PT_kcycles_effects_lens,
    CYCLES_PT_kcycles_postfx_presets,
    CYCLES_PT_kcycles_bloom_presets,
    CYCLES_PT_kcycles_tonemapping_presets,
    CYCLES_PT_kcycles_lens_presets,
)

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
