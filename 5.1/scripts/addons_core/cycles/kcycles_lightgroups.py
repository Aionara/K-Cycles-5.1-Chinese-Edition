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
from bpy.types import Panel, UIList, Menu
from bl_ui.utils import PresetPanel
from bpy.utils import register_class, unregister_class

class KCyclesLightItem:
    def __init__(self, typ, name, collapse, exposure, color_tint0, color_tint1, color_tint2): 
        self.typ = typ
        self.name = name
        self.collapse = collapse
        self.exposure = exposure
        self.color_tint0 = color_tint0
        self.color_tint1 = color_tint1
        self.color_tint2 = color_tint2

class CyclesPresetPanel(PresetPanel, Panel):
    COMPAT_ENGINES = {'CYCLES'}
    preset_operator = "script.execute_preset"

    @staticmethod
    def post_cb(context, _filepath):
        # Modify an arbitrary built-in scene property to force a depsgraph
        # update, because add-on properties don't. (see T62325)
        render = context.scene.render
        render.filter_size = render.filter_size

class CyclesButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {'CYCLES'}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

def collection_hide_get(context, collection_name):
    hide_get = False
    index = context.scene.kcycles_lights.find(collection_name) + 1
    kcycles_lights_size = len(context.scene.kcycles_lights)

    while index > 0 and index < kcycles_lights_size:
        obj_next = context.scene.objects.get(context.scene.kcycles_lights[index].name)
        if (not obj_next or context.scene.kcycles_lights[index].typ == 'C'):
            break
        if (obj_next.hide_get()):
            hide_get = True
        else:
            hide_get = False
            break
        index = index + 1
    return hide_get

def update_lights_collection_color(self, context):
    cscene = context.scene.cycles
    objs = kcycles_lights_collection_objects(context, self.name)
    for obj in objs:
        if (obj.type == "LIGHT"):
            obj.data.color[0:3] = self.color_tint[0:3]
        if (obj.type == "MESH"):
            node_strength, node_color, mat = emission_node_strength_color(obj)
            node_color.default_value[0:3] = self.color_tint[0:3]

def set_lights_solo(self, context, set_solo_lights):
    cscene = context.scene.cycles
    selected_light_item = context.scene.kcycles_lights[cscene.kcycles_lights_list_index]
    if ((selected_light_item.typ == 'L' or selected_light_item.typ == 'M' or selected_light_item.typ == 'W') or
        (selected_light_item.typ == 'C' and not set_solo_lights)):
        for item in context.scene.kcycles_lights:
            if ((item.typ == 'L' or item.typ == 'M') and item.name in bpy.data.objects):
                obj = bpy.data.objects[item.name]
                show_light = False if item.name == selected_light_item.name or not set_solo_lights else True
                obj.hide_set(show_light)
                obj.hide_viewport = show_light
                obj.hide_render = show_light
            if (item.typ == 'W'):
                background_node = world_background_node(item.name)
                if (background_node):
                    mute_background = False if item.name == selected_light_item.name or not set_solo_lights else True
                    background_node.mute = mute_background
    if (selected_light_item.typ == 'C' and set_solo_lights):
        for item in context.scene.kcycles_lights:
            if (item.typ == 'C'):
                show_collection_items = False if (item.name == selected_light_item.name) else True
            if ((item.typ == 'L' or item.typ == 'M') and item.name in bpy.data.objects):
                obj = bpy.data.objects[item.name]
                obj.hide_set(show_collection_items)
                obj.hide_viewport = show_collection_items
                obj.hide_render = show_collection_items
            if (item.typ == 'W'):
                background_node = world_background_node(item.name)
                if (background_node):
                    background_node.mute = True

def update_lights_index(self, context):
    cscene = context.scene.cycles
    if (cscene.kcycles_lights_solo):
        set_lights_solo(self, context, True)

def update_lights_solo_mode(self, context):
    cscene = context.scene.cycles
    if (cscene.kcycles_lights_solo):
        set_lights_solo(self, context, True)
    else:
        set_lights_solo(self, context, False)

def update_lights_mode(self, context):
    cscene = context.scene.cycles
    if (cscene.kcycles_lights_mode == "LIGHT"):
        refresh_kcycles_lights()

def find_kcycles_light_item(list, name):
    for item in list:
        if (item.name == name):
            return item
    return None

def refresh_kcycles_lights(reset = False):
    KCYCLES_OT_light_exposure_step.stop_updates = True
    kcycles_lights_collections = []

    if (not reset):
        for item in bpy.context.scene.kcycles_lights:
            if (item.typ == 'C'):
                light_item = KCyclesLightItem(item.typ, item.name, item.collapse, item.exposure, item.color_tint[0],
                    item.color_tint[1], item.color_tint[2])
                kcycles_lights_collections.append(light_item)

    for item in bpy.context.scene.kcycles_lights:
        bpy.context.scene.kcycles_lights.remove(0)
    collections_in_scene = [c for c in bpy.data.collections if bpy.context.scene.user_of_id(c)]
    for collection in collections_in_scene:
        added_collection_item = False
        for obj in collection.objects:
            is_emissive = False
            if obj.name in bpy.context.view_layer.objects and obj.type == 'MESH':
                if (emissive_material(obj, False)):
                    is_emissive = True
            if obj.name in bpy.context.view_layer.objects and obj.type == 'LIGHT' or is_emissive:
                if (added_collection_item == False):
                    added_collection_item = True
                    KCyclesLightItemList = bpy.context.scene.kcycles_lights.add()
                    KCyclesLightItemList.typ = 'C'
                    KCyclesLightItemList.name = collection.name
                    if (not reset and kcycles_lights_collections):
                        collection_item = find_kcycles_light_item(kcycles_lights_collections, collection.name)
                        if (collection_item):
                            KCyclesLightItemList.collapse = collection_item.collapse
                            KCyclesLightItemList.exposure = collection_item.exposure
                            KCyclesLightItemList.color_tint[0] = collection_item.color_tint0
                            KCyclesLightItemList.color_tint[1] = collection_item.color_tint1
                            KCyclesLightItemList.color_tint[2] = collection_item.color_tint2
                KCyclesLightItemList = bpy.context.scene.kcycles_lights.add()
                KCyclesLightItemList.typ = obj.type[0]
                KCyclesLightItemList.name = obj.name
    if (bpy.context.scene.world != None):
        for node in bpy.context.scene.world.node_tree.nodes:
            if (node.type == "BACKGROUND"):
                KCyclesLightItemList = bpy.context.scene.kcycles_lights.add()
                KCyclesLightItemList.typ = 'W'
                KCyclesLightItemList.name = node.name
    KCYCLES_OT_light_exposure_step.stop_updates = False

class CYCLES_PT_kcycles_lightgroups_presets(CyclesPresetPanel):
    bl_label = "K-Cycles 灯光组预设"
    preset_subdir = "cycles/kcycles_lightgroups"
    preset_add_operator = "render.cycles_kcycles_lightgroups_preset_add"

def lightgroups_list_delimeted():
    view_layer = bpy.context.view_layer

    lightgroups_list_delimeted = ""
    prefix = ""
    for index, lightgroup in enumerate(view_layer.lightgroups):
        view_layer_lightgroup = view_layer_lightgroup_camera(bpy.context, lightgroup.name)
        if (index > 0):
            prefix = ","
        lightgroups_list_delimeted += prefix + lightgroup.name + "," + "{:.2f}".format(view_layer_lightgroup.power) + \
            "," + "{:.2f}".format(view_layer_lightgroup.color_tint[0]) + \
            "," + "{:.2f}".format(view_layer_lightgroup.color_tint[1]) + \
            "," + "{:.2f}".format(view_layer_lightgroup.color_tint[2]) + \
            "," + "{:.2f}".format(view_layer_lightgroup.white_balance) + \
            "," + "{:.2f}".format(view_layer_lightgroup.contrast) + \
            "," + "{:.2f}".format(view_layer_lightgroup.highlights) + \
            "," + "{:.2f}".format(view_layer_lightgroup.shadows) + \
            "," + "{:.2f}".format(view_layer_lightgroup.saturation)

    return lightgroups_list_delimeted

def update_lightgroup_values(view_layer_lightgroup, power, color_r, color_g, color_b, white_balance, contrast, highlights, shadows, saturation):
    if (view_layer_lightgroup.power != power):
        view_layer_lightgroup.power = power
    if (view_layer_lightgroup.color_tint[0] != color_r):
        view_layer_lightgroup.color_tint[0] = color_r
    if (view_layer_lightgroup.color_tint[1] != color_g):
        view_layer_lightgroup.color_tint[1] = color_g
    if (view_layer_lightgroup.color_tint[2] != color_b):
        view_layer_lightgroup.color_tint[2] = color_b
    if (view_layer_lightgroup.white_balance != white_balance):
        view_layer_lightgroup.white_balance = white_balance
    if (view_layer_lightgroup.contrast != contrast):
        view_layer_lightgroup.contrast = contrast
    if (view_layer_lightgroup.highlights != highlights):
        view_layer_lightgroup.highlights = highlights
    if (view_layer_lightgroup.shadows != shadows):
        view_layer_lightgroup.shadows = shadows
    if (view_layer_lightgroup.saturation != saturation):
        view_layer_lightgroup.saturation = saturation

def apply_lightgroups_list_delimeted(value):
    if (value):
        lightgroup_list = value.split(',')
        for i in range(0, len(lightgroup_list), 10):
            if (lightgroup_list[i] in bpy.context.view_layer.lightgroups):
                view_layer_lightgroup = view_layer_lightgroup_camera(bpy.context, lightgroup_list[i])
                update_lightgroup_values(view_layer_lightgroup, float(lightgroup_list[i+1]), float(lightgroup_list[i+2]),
                    float(lightgroup_list[i+3]), float(lightgroup_list[i+4]), float(lightgroup_list[i+5]), float(lightgroup_list[i+6]),
                    float(lightgroup_list[i+7]), float(lightgroup_list[i+8]), float(lightgroup_list[i+9]))
    else:
        for lightgroup in bpy.context.view_layer.lightgroups:
            if (lightgroup.name in bpy.context.view_layer.lightgroups):
                view_layer_lightgroup = view_layer_lightgroup_camera(bpy.context, lightgroup.name)
                update_lightgroup_values(view_layer_lightgroup, 1, 1, 1, 1, 0, 1, 1, 1, 1)


def refresh_lightgroup_lights():
    cscene = bpy.context.scene.cycles

    for item in bpy.context.scene.lightgroup_lights:
        bpy.context.scene.lightgroup_lights.remove(0)

    for obj in bpy.context.scene.objects:
        if (cscene.kcycles_lightgroup != "" and obj.lightgroup == cscene.kcycles_lightgroup):
            KCyclesItemList = bpy.context.scene.lightgroup_lights.add()
            if (obj.type == 'MESH'):
                KCyclesItemList.typ = 'M'
            elif (obj.type == 'LIGHT'):
                KCyclesItemList.typ = 'L'
            KCyclesItemList.name = obj.name
        if (obj.lightgroup != ""):
            if (obj.type == 'MESH' and obj.visible_shadow != bpy.context.view_layer.lightgroups[obj.lightgroup].cast_shadow):
                 obj.visible_shadow = bpy.context.view_layer.lightgroups[obj.lightgroup].cast_shadow
            if (obj.type == 'LIGHT' and bpy.data.lights[obj.data.name].use_shadow != bpy.context.view_layer.lightgroups[obj.lightgroup].cast_shadow):
                bpy.data.lights[obj.data.name].use_shadow = bpy.context.view_layer.lightgroups[obj.lightgroup].cast_shadow
                bpy.data.lights[obj.data.name].energy = bpy.data.lights[obj.data.name].energy

    if (bpy.context.scene.world != None):
        world_lightgroup = bpy.context.scene.world.lightgroup
        if (world_lightgroup != None and world_lightgroup == cscene.kcycles_lightgroup):
            KCyclesItemList = bpy.context.scene.lightgroup_lights.add()
            KCyclesItemList.typ = 'W'
            KCyclesItemList.name = bpy.context.scene.world.name

def set_lightgroup_object_rename(self, value):
    cscene = bpy.context.scene.cycles

    for obj in bpy.context.scene.objects:
        if (cscene.kcycles_lightgroup != "" and obj.lightgroup == cscene.kcycles_lightgroup):
            obj.lightgroup = value
            obj.pass_index = obj.pass_index

    if (bpy.context.scene.world != None):
        world_lightgroup = bpy.context.scene.world.lightgroup
        if (world_lightgroup != None and world_lightgroup == cscene.kcycles_lightgroup):
            bpy.context.scene.world.cycles.lightgroup = value

    view_layer = bpy.context.view_layer
    view_layer.active_lightgroup_index = view_layer.active_lightgroup_index
    view_layer_lightgroup = view_layer.lightgroups[cscene.kcycles_lightgroup]
    sync_light_linking(bpy.context, view_layer_lightgroup)

def update_lightgroup_lights(self, context):
    refresh_lightgroup_lights()

def update_lightgroup_world(self, context):
    bpy.context.scene.world.lightgroup = bpy.context.scene.world.cycles.lightgroup

def update_lightgroup_remainder(self, context):
    view_layer = context.view_layer
    cscene = context.scene.cycles

    remainder_name = "Lightgroup_remainder"
    if (cscene.kcycles_lightgroup_remainder == True and remainder_name not in view_layer.lightgroups):
        cscene.kcycles_lightgroup = remainder_name
        lightgroup = view_layer.lightgroups.add()
        lightgroup.name = remainder_name
    elif cscene.kcycles_lightgroup_remainder == False:
        for index, item in enumerate(view_layer.lightgroups):
            if item.name == remainder_name:
                view_layer.active_lightgroup_index = index
                bpy.ops.scene.view_layer_remove_lightgroup('EXEC_DEFAULT')
                break

    cscene.kcycles_lightgroup_change += 1

def refresh_light_shadow_linking(self):
    cscene = bpy.context.scene.cycles
    view_layer = bpy.context.view_layer

    if (cscene.kcycles_lightgroup in view_layer.lightgroups):
        view_layer_lightgroup = view_layer.lightgroups[cscene.kcycles_lightgroup]
        sync_light_linking(bpy.context, view_layer_lightgroup)

def collection_unlink_remove(collection_name):
    if (collection_name in bpy.data.collections):
        collection = bpy.data.collections[collection_name]
        for obj in collection.objects:
            collection.objects.unlink(obj)
        for col in collection.children:
            collection.children.unlink(bpy.data.collections[col.name])
        bpy.data.collections.remove(collection)

def light_shadow_linking_unlink_remove(context):
    if is_kcycles_lightgroup_world_lightgroup():
        return
    collection_unlink_remove("LGLL " + context.scene.cycles.kcycles_lightgroup)
    collection_unlink_remove("LGSL " + context.scene.cycles.kcycles_lightgroup)

    for light in context.scene.lightgroup_lights:
        if (bpy.data.objects[light.name].light_linking.receiver_collection != None):
            receiver_collection = bpy.data.objects[light.name].light_linking.receiver_collection
            receiver_collection_name = receiver_collection.name
            if (receiver_collection_name[:5] == "LGLL "):
                collection_unlink_remove(receiver_collection_name)
            else:
                bpy.data.objects[light.name].light_linking.receiver_collection = None
        if (bpy.data.objects[light.name].light_linking.blocker_collection != None):
            blocker_collection = bpy.data.objects[light.name].light_linking.blocker_collection
            blocker_collection_name = blocker_collection.name
            if (blocker_collection_name[:5] == "LGSL "):
                collection_unlink_remove(blocker_collection_name)
            else:
                bpy.data.objects[light.name].light_linking.blocker_collection = None

def new_collection_add_linked_objects(view_layer_lightgroup, collection_name):
    if (collection_name not in bpy.data.collections):
        collection = bpy.data.collections.new(collection_name)
        for linked_object in view_layer_lightgroup.linked_objects:
            if linked_object.typ == 'M' and linked_object.name in bpy.data.objects:
                collection.objects.link(bpy.data.objects[linked_object.name])
                if linked_object.include == True and collection_name[:5] == "LGLL " or linked_object.cast_shadow == True and collection_name[:5] == "LGSL ":                        
                    collection.collection_objects[len(collection.collection_objects) - 1].light_linking.link_state = 'INCLUDE'
                else:
                    collection.collection_objects[len(collection.collection_objects) - 1].light_linking.link_state = 'EXCLUDE'
            if linked_object.typ == 'C' and linked_object.name in bpy.data.collections:
                collection.children.link(bpy.data.collections[linked_object.name])
                if linked_object.include == True and collection_name[:5] == "LGLL " or linked_object.cast_shadow == True and collection_name[:5] == "LGSL ":                        
                    collection.collection_children[len(collection.collection_children) - 1].light_linking.link_state = 'INCLUDE'
                else:
                    collection.collection_children[len(collection.collection_children) - 1].light_linking.link_state = 'EXCLUDE'

def is_kcycles_lightgroup_world_lightgroup():
    if (bpy.context.scene.world != None):
        world_lightgroup = bpy.context.scene.world.lightgroup
        if (world_lightgroup != None and world_lightgroup == bpy.context.scene.cycles.kcycles_lightgroup):
            return True
        else:
            return False
    else:
        return False

def sync_light_linking(context, view_layer_lightgroup):
    if (is_kcycles_lightgroup_world_lightgroup()):
        return
    cscene = context.scene.cycles
    light_shadow_linking_unlink_remove(context)

    if (len(view_layer_lightgroup.linked_objects) > 0):
        if (view_layer_lightgroup.use_light_linking):
            receiver_collection_name = "LGLL " + cscene.kcycles_lightgroup
            new_collection_add_linked_objects(view_layer_lightgroup, receiver_collection_name)
            for light in context.scene.lightgroup_lights:
                if (receiver_collection_name in bpy.data.collections):
                    bpy.data.objects[light.name].light_linking.receiver_collection = bpy.data.collections[receiver_collection_name]
        if (view_layer_lightgroup.use_shadow_linking):
            blocker_collection_name = "LGSL " + cscene.kcycles_lightgroup
            new_collection_add_linked_objects(view_layer_lightgroup, blocker_collection_name)
            if (blocker_collection_name in bpy.data.collections):
                for light in context.scene.lightgroup_lights:
                    bpy.data.objects[light.name].light_linking.blocker_collection = bpy.data.collections[blocker_collection_name]

def set_refresh_lightgroup_lights(self, value):
    refresh_lightgroup_lights()

def update_lightgroup_change(self, context):
    cscene = context.scene.cycles
    if (context.scene.cycles.kcycles_lightgroup_change >= 1024):
        context.scene.cycles.kcycles_lightgroup_change = 0

def set_refresh_lightgroup_compositor(self, value):
    refresh_lightgroup_compositor()

def set_refresh_light_shadow_linking(self, value):
    refresh_light_shadow_linking(self)

def refresh_lightgroup_compositor():
    cscene = bpy.context.scene.cycles
    if cscene.kcycles_lightgroup_compositor:
        for node in bpy.data.node_groups["KCL_LightGroups"].nodes:
            if node.type == "MIX" and node.blend_type == "MULTIPLY":
                if ((not cscene.kcycles_lightgroup_solo and bpy.context.view_layer.lightgroups[node.name].show_lightgroup)
                    or (cscene.kcycles_lightgroup_solo and cscene.kcycles_lightgroup == node.name)):
                    view_layer_lightgroup = view_layer_lightgroup_camera(bpy.context, node.name)
                    power = view_layer_lightgroup.power
                    power *= power
                    blueWB = 1.0
                    redWB = 1.0
                    white_balance = view_layer_lightgroup.white_balance
                    if (white_balance < 0.0):
                         blueWB = white_balance + 1.0
                    else:
                        redWB = (1.0 - white_balance)
                    redWB = max(redWB, 0.05)
                    blueWB = max(blueWB, 0.05)

                    averageWB = (blueWB + redWB) / 2.0
                    tempertureTintRGB = (averageWB / redWB, 1.0, averageWB / blueWB)

                    color_tint = view_layer_lightgroup.color_tint[0:3]
                    node.inputs["A"].default_value = (color_tint[0] * tempertureTintRGB[0] * power,
                                                    color_tint[1] * tempertureTintRGB[1] * power,
                                                    color_tint[2] * tempertureTintRGB[2] * power, 1)
                else:
                    node.inputs["A"].default_value = (0, 0, 0, 1)
    return

def get_node_id(nodes, id_name):
    node_id = []
    for node in nodes:
        if node.bl_idname == id_name:
            node_id = node
    return node_id

def update_lightgroup_compositor(self, context):
    view_layer = context.view_layer
    scene = context.scene
    cscene = context.scene.cycles

    node_group = []
    if not scene.compositing_node_group:
        node_group = scene.compositing_node_group = bpy.data.node_groups.new('Compositing Nodes', 'CompositorNodeTree')
    else:
        node_group = scene.compositing_node_group
    scene.render.use_compositing = True

    render_layers = get_node_id(node_group.nodes, "CompositorNodeRLayers")
    if  not render_layers:
        render_layers = node_group.nodes.new(type="CompositorNodeRLayers")
    group_output = get_node_id(node_group.nodes, "NodeGroupOutput")
    if not group_output:
        group_output = node_group.nodes.new(type="NodeGroupOutput")
        node_group.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    viewer_output = get_node_id(node_group.nodes, "CompositorNodeViewer")
    if not viewer_output:
        viewer_output = node_group.nodes.new(type="CompositorNodeViewer")

    # Get lightgroup names
    lg_names = [lightgroup_item.name for lightgroup_item in view_layer.lightgroups]

    # Check for a at least two lightgroups
    if len(lg_names) == 0 or len(lg_names) == 1:
        return

    # Remove KCL_LightGroups
    if not cscene.kcycles_lightgroup_compositor:
        for node in node_group.nodes:
            if "KCL_" in node.name:
                node_group.nodes.remove(node)
        for node in bpy.data.node_groups:
            if "KCL_" in node.name:
                bpy.data.node_groups.remove(node)
        node_group.links.new(render_layers.outputs[0], node_group.nodes['Group Output'].inputs[0])
        if ("Viewer" in node_group.nodes):
            node_group.links.new(render_layers.outputs[0], node_group.nodes['Viewer'].inputs[0])
        return

    # Create K-Cycles Light Groups group node
    kcl_lightgroups_node = node_group.nodes.new('CompositorNodeGroup')
    kcl_lightgroups_node.name = "KCL_LightGroups"
    kcl_lightgroups_node.location = (render_layers.location[0] + 350, render_layers.location[1] - 50)
    kcl_lightgroups = bpy.data.node_groups.new(name="KCL_LightGroups", type="CompositorNodeTree")
    kcl_lightgroups_node.node_tree = kcl_lightgroups

    for i in range(len(lg_names)):
        kcl_lightgroups.interface.new_socket(socket_type="NodeSocketColor", name=lg_names[i], in_out='INPUT')

    # Create group input node and output node
    group_input_node = kcl_lightgroups.nodes.new('NodeGroupInput')
    group_output_node = kcl_lightgroups.nodes.new('NodeGroupOutput')
    group_input_node.location = (-500, 0)
    group_output_node.location = (500 + group_output_node.width, 0)

    # Create all the nodes inside kcl_lightgroups
    prev_add_node = None
    for i in range(len(lg_names)):
        add_node = create_mix_RGB_node(kcl_lightgroups, "ADD", location=(
            render_layers.location[0] + (i + 2) * 175, render_layers.location[1] - (i + 1) * 100))
        add_node.inputs["Factor"].default_value = 1

        if prev_add_node is None:
            # set black color for the first node
            add_node.inputs["A"].default_value = (0, 0, 0, 1)
        else:
            kcl_lightgroups.links.new(prev_add_node.outputs["Result"], add_node.inputs["A"])
        prev_add_node = add_node

        multipy_node = create_mix_RGB_node(kcl_lightgroups, "MULTIPLY", location=(
            render_layers.location[0] + (i + 2) * 175 - 200, render_layers.location[1] - (i + 1) * 200))
        multipy_node.name = lg_names[i]
        multipy_node.inputs["A"].default_value = (1, 1, 1, 1)
        multipy_node.inputs["Factor"].default_value = 1
        kcl_lightgroups.links.new(group_input_node.outputs[i], multipy_node.inputs["B"])
        kcl_lightgroups.links.new(multipy_node.outputs["Result"], add_node.inputs["B"])

    # Link to output
    kcl_lightgroups_node.node_tree.interface.new_socket(socket_type="NodeSocketColor", name="Image", in_out='OUTPUT')
    kcl_lightgroups.links.new(prev_add_node.outputs["Result"], group_output_node.inputs[0])

    # Link render_layers to kcl_lightgroups_node
    for i, lg_name in enumerate(lg_names):
        node_group.links.new(render_layers.outputs["Combined_" + lg_name], kcl_lightgroups_node.inputs[i])

    # Link kcl_lightgroups_node to Group Output and Viewer nodes
    node_group.links.new(kcl_lightgroups_node.outputs[0], node_group.nodes['Group Output'].inputs["Image"])
    node_group.nodes['Group Output'].location = (kcl_lightgroups_node.location.x + kcl_lightgroups_node.width + 50, kcl_lightgroups_node.location.y)
    if ("Viewer" in  node_group.nodes):
        node_group.links.new(kcl_lightgroups_node.outputs[0], node_group.nodes['Viewer'].inputs[0])
        node_group.nodes['Viewer'].location = (kcl_lightgroups_node.location.x + kcl_lightgroups_node.width + 50, kcl_lightgroups_node.location.y - node_group.nodes['Group Output'].height - 50)

    # Update the compositor values
    refresh_lightgroup_compositor()

def create_mix_RGB_node(node_group, blend_type, location=(0, 0)):
    add_node = node_group.nodes.new('ShaderNodeMix')
    add_node.blend_type = blend_type
    add_node.data_type = "RGBA"
    add_node.clamp_factor = False
    add_node.location = location
    return add_node

def emissive_material(obj, check_node_groups):
    emissive_material = False

    if not obj.material_slots:
        return emissive_material

    for mat in obj.material_slots:
        if mat.material and mat.material.node_tree and mat.material.node_tree.nodes:
            for node in mat.material.node_tree.nodes:
                if (node.type == "BSDF_PRINCIPLED" and ((node.inputs["Emission Strength"].default_value > 0 and
                    node.inputs["Emission Color"].default_value[:3] != (0, 0, 0)) or
                    node.inputs["Emission Strength"].is_linked or node.inputs["Emission Color"].is_linked)):
                    emissive_material = True
                elif (node.type == "EMISSION" and node.outputs["Emission"].is_linked):
                    emissive_material = True
                elif check_node_groups and node.type == "GROUP" and node.node_tree and node.node_tree.nodes:
                    for group_node in node.node_tree.nodes:
                        if (group_node.type == "BSDF_PRINCIPLED" and ((group_node.inputs["Emission Strength"].default_value > 0 and
                            group_node.inputs["Emission Color"].default_value[:3] != (0, 0, 0)) or
                            group_node.inputs["Emission Strength"].is_linked)):
                            emissive_material = True
                            break
                        if (group_node.type == "EMISSION" and group_node.outputs["Emission"].is_linked):
                            emissive_material = True
                            break
                if (emissive_material):
                    break
    return emissive_material

def add_lightgroup_lights(self, list):
    lights_add = False
    for item in list:
        if item.bl_rna.identifier == "Object" and item.name in bpy.context.view_layer.objects:
            if item.type == 'LIGHT':
                print(item.name)
                item.lightgroup = bpy.context.scene.cycles.kcycles_lightgroup
                item.pass_index = item.pass_index
                lights_add = True
            if item.type == 'MESH':
                if (emissive_material(item, True)):
                    item.lightgroup = bpy.context.scene.cycles.kcycles_lightgroup
                    item.pass_index = item.pass_index
                    lights_add = True

    return lights_add

def add_lighgroup_cameras(self, lightgroup):
    for obj_camera in bpy.context.scene.objects:
        if obj_camera.type == "CAMERA":
            lightgroup_camera = lightgroup.cameras.add()
            lightgroup_camera.name = obj_camera.name


class CYCLES_RENDER_OT_kcycles_lightgroup_lights_add(bpy.types.Operator):
    bl_idname = "kcycles.lightgroup_lights_add"
    bl_label = "添加"
    bl_description = "添加灯光组灯光"

    def execute(self, context):
        scene = context.scene
        cscene = scene.cycles
        view_layer = context.view_layer
        view_layer_lightgroup = view_layer.lightgroups[cscene.kcycles_lightgroup]

        if (cscene.kcycles_lightgroup in view_layer.lightgroups):
            if (len(bpy.context.selected_objects) == 0 and len(bpy.context.collection.name) > 0):
                if (bpy.context.collection.name in bpy.data.collections):
                    add_lightgroup_lights(self, bpy.data.collections[bpy.context.collection.name].objects)
            else:
                add_lightgroup_lights(self, bpy.context.selected_objects)
            view_layer_lightgroup.active_light_index = len(scene.lightgroup_lights) - 1
            cscene.kcycles_lightgroup = cscene.kcycles_lightgroup
            sync_light_linking(context, view_layer_lightgroup)
        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_lightgroup_lights_remove(bpy.types.Operator):
    bl_idname = "kcycles.lightgroup_lights_remove"
    bl_label = "移除"
    bl_description = "移除灯光组灯光"

    def execute(self, context):
        scene = bpy.context.scene
        cscene = scene.cycles
        view_layer = bpy.context.view_layer
        view_layer_lightgroup = view_layer.lightgroups[cscene.kcycles_lightgroup]

        if (cscene.kcycles_lightgroup in view_layer.lightgroups):
            light_shadow_linking_unlink_remove(context)
            total_objects = len(scene.lightgroup_lights)
            if (view_layer_lightgroup.active_light_index < total_objects and
                view_layer_lightgroup.active_light_index >= 0):

                obj_name = scene.lightgroup_lights[view_layer_lightgroup.active_light_index].name
                obj_type = scene.lightgroup_lights[view_layer_lightgroup.active_light_index].typ
                if (obj_name in scene.objects or obj_type == "W"):
                    light_removed = False
                    if (obj_type != "W"):
                        light_object = scene.objects[obj_name]
                        if (light_object != None):
                            light_object.lightgroup = ""
                            light_object.pass_index = light_object.pass_index
                            light_removed = True
                    elif (bpy.context.scene.world != None):
                        scene.world.cycles.lightgroup = ""
                        light_removed = True

                    if (total_objects == 1 and light_removed == True):
                        view_layer_lightgroup.active_light_index = -1
                    elif (view_layer_lightgroup.active_light_index == (total_objects - 1)):
                         view_layer_lightgroup.active_light_index = view_layer_lightgroup.active_light_index-1
                    cscene.kcycles_lightgroup = cscene.kcycles_lightgroup
                    sync_light_linking(context, view_layer_lightgroup)
        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_lightgroup_lights_select(bpy.types.Operator):
    bl_idname = "kcycles.lightgroup_lights_select"
    bl_label = "在大纲/视图中选择灯光"
    bl_description = "在大纲和视图中选择灯光"

    def execute(self, context):
        scene = context.scene
        cscene = context.scene.cycles
        view_layer = context.view_layer
        view_layer_lightgroup = view_layer.lightgroups[cscene.kcycles_lightgroup]

        if (len(scene.lightgroup_lights) > 0 and view_layer_lightgroup.active_light_index >= 0):
            object_name = scene.lightgroup_lights[view_layer_lightgroup.active_light_index].name
            if (object_name in bpy.context.scene.objects):
                object = bpy.context.scene.objects[object_name]
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = object
                object.select_set(True)
                for area in bpy.context.window.screen.areas:
                    if area.type == 'OUTLINER':
                        with bpy.context.temp_override(area=area,
                            region=next(region for region in area.regions if region.type == 'WINDOW')):
                            bpy.ops.outliner.show_active() 
        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_linked_objects_add(bpy.types.Operator):
    bl_idname = "kcycles.linked_objects_add"
    bl_label = "添加"
    bl_description = "添加灯光组链接对象"

    def execute(self, context):
        cscene = context.scene.cycles
        view_layer = context.view_layer
        view_layer_lightgroup = view_layer.lightgroups[cscene.kcycles_lightgroup]

        if (cscene.kcycles_lightgroup in view_layer.lightgroups):
            outliner_collections = outliner_selected_collections()
            if (len(outliner_collections) > 0):
                for collection in outliner_collections:
                    if collection.name not in view_layer_lightgroup.linked_objects:
                        linked_object = view_layer_lightgroup.linked_objects.add()
                        linked_object.typ = 'C'
                        linked_object.name = collection.name
                        cscene.kcycles_lightgroup_change += 1

            for item in bpy.context.selected_objects:
                if item.bl_rna.identifier == "Object":
                    if item.type == 'MESH':
                        if item.name not in view_layer_lightgroup.linked_objects:
                            linked_object = view_layer_lightgroup.linked_objects.add()
                            linked_object.typ = 'M'
                            linked_object.name = item.name
                            linked_object.cast_shadow = True
                            cscene.kcycles_lightgroup_change += 1
            view_layer_lightgroup.active_linking_index = len(view_layer_lightgroup.linked_objects) - 1
        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_linked_objects_remove(bpy.types.Operator):
    bl_idname = "kcycles.linked_objects_remove"
    bl_label = "移除"
    bl_description = "移除灯光组链接对象"

    def execute(self, context):
        cscene = context.scene.cycles
        view_layer = context.view_layer
        view_layer_lightgroup = view_layer.lightgroups[cscene.kcycles_lightgroup]

        if (cscene.kcycles_lightgroup in view_layer.lightgroups):
            total_objects = len(view_layer_lightgroup.linked_objects)
            if (view_layer_lightgroup.active_linking_index < total_objects and view_layer_lightgroup.active_linking_index >= 0):
                linked_object = view_layer_lightgroup.linked_objects[view_layer_lightgroup.active_linking_index]
                view_layer_lightgroup.linked_objects.remove(linked_object)
                if (total_objects == 1):
                    view_layer_lightgroup.active_linking_index = -1
                elif (view_layer_lightgroup.active_linking_index == (total_objects - 1)):
                     view_layer_lightgroup.active_linking_index =  view_layer_lightgroup.active_linking_index -1
            sync_light_linking(context, view_layer_lightgroup)
        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_lightgroups_camera_sync(bpy.types.Operator):
    bl_idname = "kcycles.lightgroups_camera_sync"
    bl_label = "相机同步"
    bl_description = "同步所有灯光组相机数据"

    def execute(self, context):
        view_layer = context.view_layer

        # Add lightgroup cameras
        for lightgroup in view_layer.lightgroups:
            for obj_camera in bpy.context.scene.objects:
                if obj_camera.type == "CAMERA" and obj_camera.name not in lightgroup.cameras:
                    lightgroup_camera = lightgroup.cameras.add()
                    lightgroup_camera.name = obj_camera.name
                    context.scene.cycles.kcycles_lightgroup_change += 1

        # Remove lightgroup cameras
        for lightgroup in view_layer.lightgroups:
            for camera in lightgroup.cameras:
                if camera.name not in bpy.context.scene.objects:
                    lightgroup.cameras.remove(camera)
                    context.scene.cycles.kcycles_lightgroup_change += 1

        return{'FINISHED'}


class CYCLES_RENDER_OT_kcycles_lightgroup_apply_changes_to_lights(bpy.types.Operator):
    bl_idname = "kcycles.lightgroup_apply_changes_to_lights"
    bl_label = "将更改应用到灯光"
    bl_description = "将所有灯光组混合器更改应用回所有灯光"

    def execute(self, context):
        scene = bpy.context.scene
        cscene = scene.cycles
        view_layer = bpy.context.view_layer

        # Update all the lights
        obj_data_applied = []
        material_applied = []
        for obj in bpy.context.scene.objects:
            if (obj.lightgroup != ""):
                view_layer_lightgroup = view_layer_lightgroup_camera(context, obj.lightgroup)
                if (view_layer_lightgroup != None):
                    power = view_layer_lightgroup.power * view_layer_lightgroup.power
                    if (obj.type == 'MESH'):
                        for mat in obj.material_slots:
                            if mat.material and mat.material.node_tree and mat.material.node_tree.nodes and mat not in material_applied:
                                for node in mat.material.node_tree.nodes:
                                    if (node.type == "BSDF_PRINCIPLED" and ((node.inputs["Emission"].default_value[:3] != (0, 0, 0))
                                        or node.inputs["Emission"].is_linked)):
                                        node.inputs["Emission Strength"].default_value *= power
                                        view_layer_lightgroup.power = 1.0
                                        color = lightgroup_tempertureTintRGB(view_layer_lightgroup, node.inputs["Emission"].default_value)
                                        node.inputs["Emission"].default_value = (color[0], color[1], color[2], 1)
                                        material_applied.append(mat)
                                    elif (node.type == "EMISSION" and node.outputs["Emission"].is_linked):
                                        node.inputs["Strength"].default_value *= power
                                        view_layer_lightgroup.power = 1.0
                                        color = lightgroup_tempertureTintRGB(view_layer_lightgroup, node.inputs["Color"].default_value)
                                        node.inputs["Color"].default_value = (color[0], color[1], color[2], 1)
                                        material_applied.append(mat)

                    elif (obj.type == 'LIGHT' and obj.data not in obj_data_applied):
                        obj.data.energy *= power
                        view_layer_lightgroup.power = 1.0
                        obj.data.color = lightgroup_tempertureTintRGB(view_layer_lightgroup, obj.data.color)
                        obj_data_applied.append(obj.data)

        # Update the world
        if (bpy.context.scene.world != None):
            world = bpy.context.scene.world
            if (world.lightgroup != None and world.lightgroup != ""):
                view_layer_lightgroup = view_layer_lightgroup_camera(context, world.lightgroup)
                if (view_layer_lightgroup != None):
                    power = view_layer_lightgroup.power * view_layer_lightgroup.power
                    for node in world.node_tree.nodes:
                        if (node.type == "BACKGROUND"):
                            node.inputs["Strength"].default_value *= power
                            view_layer_lightgroup.power = 1.0
                            color = lightgroup_tempertureTintRGB(view_layer_lightgroup, node.inputs["Color"].default_value)
                            node.inputs["Color"].default_value = (color[0], color[1], color[2], 1)
        return{'FINISHED'}

def lightgroup_tempertureTintRGB(view_layer_lightgroup, color):
    blueWB = 1.0
    redWB = 1.0

    white_balance = view_layer_lightgroup.white_balance
    if (white_balance < 0.0):
            blueWB = white_balance + 1.0
    else:
        redWB = (1.0 - white_balance)
    redWB = max(redWB, 0.05)
    blueWB = max(blueWB, 0.05)

    averageWB = (blueWB + redWB) / 2.0
    tempertureRGB = (averageWB / redWB, 1.0, averageWB / blueWB)
    color_tint = view_layer_lightgroup.color_tint[0:3]
    color_tint_RGB = (color_tint[0] * tempertureRGB[0] * color[0], color_tint[1] * tempertureRGB[1] * color[1],
                  color_tint[2] * tempertureRGB[2] * color[2])

    view_layer_lightgroup.white_balance = 0
    view_layer_lightgroup.color_tint = (1, 1, 1)

    return color_tint_RGB

class CYCLES_RENDER_UL_lightgroup_linking(UIList):
    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname):
        cscene = bpy.context.scene.cycles
        col = layout.column()
        icon = 'OUTLINER_OB_MESH'
        if (item.typ == 'C'):
            icon = 'OUTLINER_COLLECTION'
        row = col.split(factor=0.8)
        if (cscene.kcycles_lightgroup in _context.view_layer.lightgroups):
            view_layer_lightgroup = _context.view_layer.lightgroups[cscene.kcycles_lightgroup]
            row.active = view_layer_lightgroup.use_light_linking or view_layer_lightgroup.use_shadow_linking
            row.label(text=item.name, icon=icon)
            row = layout.row()
            row.scale_x = 0.85
            if (view_layer_lightgroup.use_light_linking):
                if (item.include):
                    row.prop(item, "include", text="", icon="OUTLINER_OB_LIGHT", emboss=False)
                else:
                    row.prop(item, "include", text="", icon="LIGHT_DATA", emboss=False)
            if (view_layer_lightgroup.use_shadow_linking):
                if (item.cast_shadow):
                    row.prop(item, "cast_shadow", text="", icon="HOLDOUT_ON", emboss=False)
                else:
                    row.prop(item, "cast_shadow", text="", icon="HOLDOUT_OFF", emboss=False)

def emission_node_strength_color(object):
    for mat in object.material_slots:
        if mat.material and mat.material.node_tree and mat.material.node_tree.nodes:
            for node in mat.material.node_tree.nodes:
                if (node.type == "BSDF_PRINCIPLED" and ((node.inputs["Emission Color"].default_value[:3] != (0, 0, 0))
                    or node.inputs["Emission Color"].is_linked)):
                    node_strength = node.inputs["Emission Strength"]
                    node_color = node.inputs["Emission Color"]
                    mat_used = mat
                elif (node.type == "EMISSION" and node.outputs["Emission"].is_linked):
                    node_strength = node.inputs["Strength"]
                    node_color = node.inputs["Color"]
                    mat_used = mat
    return node_strength, node_color, mat

def world_background_node(node_name):
    node_background = None
    if (bpy.context.scene.world != None):
        world = bpy.context.scene.world
        for node in world.node_tree.nodes:
            if (node.type == "BACKGROUND" and node.name == node_name):
                node_background = node
    return node_background

class CYCLES_RENDER_UL_lightgroup_lights(UIList):
    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname):
        scene = bpy.context.scene
        cscene = scene.cycles
        view_layer = bpy.context.view_layer

        icon = 'OUTLINER_DATA_LIGHT'
        if (item.typ == 'M'):
            icon = 'OUTLINER_OB_MESH'
        elif (item.typ == 'W'):
            icon = 'WORLD'

        lightgroup_name = ""
        if (item.typ == "M" or item.typ == "L"):
            if (item.name in scene.objects):
                lightgroup_name = scene.objects[item.name].lightgroup
        elif (item.typ == "W"):
            if (bpy.context.scene.world != None):
                lightgroup_name = bpy.context.scene.world.lightgroup
        if (lightgroup_name == cscene.kcycles_lightgroup):
            col = layout.column()
            row = col.split(factor=0.4)
            row.prop(item, "name", text="", icon=icon, emboss=False)
            if (item.typ == "L"):
                light_object = scene.objects[item.name]
                row.prop(light_object.data, "energy", text="")
                row.prop(light_object.data, "color", text="")
            elif (item.typ == "M"):
                light_object = scene.objects[item.name]
                for mat in light_object.material_slots:
                    if mat.material and mat.material.node_tree and mat.material.node_tree.nodes:
                        for node in mat.material.node_tree.nodes:
                            if (node.type == "BSDF_PRINCIPLED" and ((node.inputs["Emission Color"].default_value[:3] != (0, 0, 0))
                                or node.inputs["Emission Color"].is_linked)):
                                row.prop(node.inputs["Emission Strength"], "default_value", text="")
                                row.prop(node.inputs["Emission Color"], "default_value", text="")
                            elif (node.type == "EMISSION" and node.outputs["Emission"].is_linked):
                                row.prop(node.inputs["Strength"], "default_value", text="")
                                row.prop(node.inputs["Color"], "default_value", text="")
            elif (item.typ == "W"):
                if (bpy.context.scene.world != None):
                    world = bpy.context.scene.world
                    for node in world.node_tree.nodes:
                        if (node.type == "BACKGROUND"):
                            row.prop(node.inputs["Strength"], "default_value", text="")
                            row.prop(node.inputs["Color"], "default_value", text="")

def outliner_selected_collections():
    selected_collections = []
    for area in bpy.context.window.screen.areas:
        if area.type == 'OUTLINER':
            with bpy.context.temp_override(window=bpy.context.window, area=area,
                region=next(region for region in area.regions if region.type == 'WINDOW'),
                screen=bpy.context.window.screen):
                selected_collections = []
                for c in bpy.context.selected_ids:
                    if c and c.name in bpy.data.collections:
                        selected_collections.append(c)
    return selected_collections

def kcycles_lights_collection_objects(context, collection_name):
    objs = []
    collection_children = False
    for item in context.scene.kcycles_lights:
        if (item.typ == 'C'):
            if (item.name == collection_name):
                collection_children = True
            else:
                collection_children = False
        if (collection_children and (item.typ == 'L' or item.typ == 'M') and item.name in bpy.data.objects):
            objs.append(bpy.data.objects[item.name])
    return objs

def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

def find_layer_collection(layer_collection, name):
    for coll in traverse_tree(layer_collection):
        if coll.name == name:
            return coll

class KCYCLES_OT_light_exposure_step(bpy.types.Operator):
    bl_idname = "kcycles.light_exposure_step"
    bl_label = "曝光步进增加/减少"
    bl_description = "曝光调整 1/2x 步进。\nShift : 曝光调整 1/4x 步进"
    bl_options = {"REGISTER","UNDO"}

    typ : StringProperty(name = "Typ")
    name : StringProperty(name="Name")
    step_up : BoolProperty(default=True, name = "Step Up")
    direct_adjustment : FloatProperty(name="Exposure", precision=2, default=0.0)
    stop_updates = False

    def invoke(self, context, event):
        half_exposure = 0.5
        quarter_exposure = 0.25
        exposure_change = quarter_exposure if event.shift else half_exposure
        objs = []

        if (KCYCLES_OT_light_exposure_step.stop_updates):
            return{'FINISHED'}

        if self.step_up:
            exposure_adjustment = pow(2, self.direct_adjustment if self.typ == "COLLECTION_DIRECT" else exposure_change)
        else:
            exposure_adjustment = 1.0/(pow(2, self.direct_adjustment if self.typ == "COLLECTION_DIRECT" else exposure_change))

        if (self.typ == "LIGHTGROUP"):
            obj_data = view_layer_lightgroup_camera(context, self.name)
            if self.step_up:
                if event.shift:
                    obj_data.power += .10
                else:
                    obj_data.power += .20
            else:
                if event.shift:
                    obj_data.power -= .10
                else:
                    obj_data.power -= .20
        if (self.typ == "COLLECTION" or self.typ == "COLLECTION_DIRECT"):
            objs = kcycles_lights_collection_objects(context, self.name)
            item = bpy.context.scene.kcycles_lights[self.name]
            if self.typ == "COLLECTION":
                KCYCLES_OT_light_exposure_step.stop_updates = True
                item.exposure = item.exposure + (exposure_change if (self.step_up) else -exposure_change)
                KCYCLES_OT_light_exposure_step.stop_updates = False
        if (self.typ == "LIGHT" or self.typ == "MESH"):
            objs.append(bpy.data.objects[self.name])
        obj_data_applied = []
        material_applied = []
        for obj in objs:
            if (obj.type == "LIGHT" and obj.data not in obj_data_applied):
                obj.data.energy *= exposure_adjustment
                obj_data_applied.append(obj.data)
            if (obj.type == "MESH"):
                node_strength, node_color, mat = emission_node_strength_color(obj)
                if (mat.name not in material_applied):
                    node_strength.default_value *= exposure_adjustment
                    material_applied.append(mat.name)
        if (self.typ == "WORLD"):
            background_node = world_background_node(self.name)
            if (background_node):
                background_node.inputs["Strength"].default_value *= exposure_adjustment
        return{'FINISHED'}
    def execute(self,context):
        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_light_select(bpy.types.Operator):
    bl_idname = "kcycles.light_select"
    bl_label = "选择"
    bl_description = "选择集合/灯光。\nShift : 扩展选择。\nCtrl : 仅对单个灯光切换选择"
    bl_options = {"UNDO"}

    typ : StringProperty(name = "Typ")
    name : StringProperty(name = "Name")

    def invoke(self, context, event):
        if self.typ == "OBJECT":
            obj = bpy.data.objects[self.name]
            if not event.shift and not event.ctrl:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
            elif event.shift:
                obj.select_set(True)
            elif event.ctrl:
                obj.select_set(not obj.select_get())
        elif self.typ == "COLLECTION":
            if bpy.context.selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
            collection = bpy.data.collections[self.name]
            layer_collection = find_layer_collection(bpy.context.view_layer.layer_collection, self.name)
            for area in bpy.context.window.screen.areas:
                if area.type == 'OUTLINER':
                    with bpy.context.temp_override(window=bpy.context.window, area=area,
                        region=next(region for region in area.regions if region.type == 'WINDOW'),
                        screen=bpy.context.window.screen):
                        bpy.context.view_layer.active_layer_collection = layer_collection

        return{'FINISHED'}
    def execute(self,context):
        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_light_show(bpy.types.Operator):
    bl_idname = "kcycles.light_show"
    bl_label = "显示灯光"
    bl_description = "切换单个或集合的显示/隐藏"
    bl_options = {"UNDO"}

    typ : StringProperty(name = "Typ")
    name : StringProperty(name = "Name")

    def execute(self, context):
        show_light = True
        if self.typ == "LIGHT":
            obj = bpy.data.objects[self.name]
            if ((obj.hide_get() or obj.hide_viewport) and obj.hide_render):
                show_light = False
            obj.hide_set(show_light)
            obj.hide_viewport = show_light
            obj.hide_render = show_light
        elif self.typ == "COLLECTION":
            collection_children = False
            for index, item in enumerate(context.scene.kcycles_lights):
                if (item.typ == 'C'):
                    if (item.name == self.name):
                        collection_children = True
                        obj_next = context.scene.objects.get(context.scene.kcycles_lights[index+1].name)
                        if (obj_next):
                            show_collection_items = not obj_next.hide_get()
                    else:
                        collection_children = False
                if (collection_children and (item.typ == 'L' or item.typ == 'M') and item.name in bpy.data.objects):
                    obj = bpy.data.objects[item.name]
                    obj.hide_set(show_collection_items)
                    obj.hide_viewport = show_collection_items
                    obj.hide_render = show_collection_items
        if self.typ == "WORLD":
            node_background = world_background_node(self.name)
            if (node_background):
                node_background.mute = not node_background.mute
        return{'FINISHED'}

class KCYCLES_OT_light_delete(bpy.types.Operator):
    bl_idname = "kcycles.light_delete"
    bl_label = "删除灯光"
    bl_description = "删除单个或集合的灯光"
    bl_options = {"UNDO"}

    typ : StringProperty(name = "Typ")
    name : StringProperty(name = "Name")

    def execute(self, context):
        if self.typ == "LIGHT":
            obj = bpy.data.objects.get(self.name)
            if (obj):
                bpy.data.objects.remove(obj, do_unlink=True)
        elif self.typ == "MESH":
            obj = bpy.data.objects.get(self.name)
            if (obj):
                bpy.data.objects.remove(obj, do_unlink=True)

        elif self.typ == "COLLECTION":

            objs = kcycles_lights_collection_objects(context, self.name)
            for obj in objs:
                bpy.data.objects.remove(obj, do_unlink=True)
        return{'FINISHED'}

def row_light_item(self, row, _context, item):
    cscene = bpy.context.scene.cycles
    # print("Globally Viewport: " + str(obj.hide_viewport))
    # print("Viewport: " + str(obj.hide_get()))
    # print("Render: " + str(obj.hide_render))

    obj = bpy.context.scene.objects.get(item.name)
    if (not obj and (item.typ == 'L' or item.typ == 'M')):
        row.label(text=str("**** 需要刷新灯光: ") + str(item.name + " ****"))
        return

    icon = 'OUTLINER_DATA_LIGHT'
    if (item.typ == 'M'):
        icon = 'OUTLINER_OB_MESH'
        node_strength, node_color, mat = emission_node_strength_color(obj)
    elif (item.typ == 'W'):
        icon = 'WORLD'
        node_background = world_background_node(item.name)
        if (not node_background):
            row.label(text=str("**** 需要刷新灯光: ") + str(item.name + " ****"))
            return

    #row.scale_x = 0.40
    if (item.typ == 'W'):
        row.scale_x = 0.85
        row.label(text="", icon="WORLD")
    row.scale_x = 0.25
    row.label(text="", icon="BLANK1")

    row.scale_x = .90
    if (cscene.kcycles_lights_solo):
        row.active = False
        if (item.name == bpy.context.scene.kcycles_lights[cscene.kcycles_lights_list_index].name):
            row.operator("kcycles.light_show", text="", icon="EVENT_S", emboss=False).typ = ""
        else:
            row.operator("kcycles.light_show", text="", icon="HIDE_ON", emboss=False).typ = ""
        row.active = True
    else:
        if ((item.typ == 'W' and node_background.mute) or (obj and (obj.hide_get() or obj.hide_viewport) and obj.hide_render)):
            show = row.operator("kcycles.light_show", text="", icon="HIDE_ON", emboss=False)
        else:
            show = row.operator("kcycles.light_show", text="", icon="HIDE_OFF", emboss=False)
        show.typ = "LIGHT" if item.typ != 'W' else "WORLD"
        show.name = item.name

    if (item.typ != 'W'):
        row_select = row.row(align=True)
        row_select.scale_x = 0.80
        if (obj and obj.select_get()):
            sel = row_select.operator("kcycles.light_select", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
        else:
            sel = row_select.operator("kcycles.light_select", text="", icon="RESTRICT_SELECT_ON", emboss=False)
        sel.typ = "OBJECT" if obj else "WORLD"
        sel.name = item.name

    split_icon = row.row(align=True)
    split_icon.scale_x = 0.95
    if (item.typ != 'W'):
        split_icon.label(text="", icon=icon)

    split_name = row.split(align=True, factor=1)
    split_name.ui_units_x = 6.4 if (item.typ != 'W') else 7.0
    split_name.prop(item, "name", text="", emboss=False)

    row_main = row.row(align=True)
    row_main.scale_x = 0.75
    if (item.typ == 'L'):
        row_main.prop(obj.data, "energy", text="", emboss=True)
        ops_type = "LIGHT"
    elif (item.typ == 'M'):
        row_main.prop(node_strength, "default_value", text="")
        ops_type = "MESH"
    elif (item.typ == 'W'):        
        row_main.prop(node_background.inputs["Strength"], "default_value", text="")
        ops_type = "WORLD"

    col = row_main.column(align=True)
    col.scale_x = 1.05
    col.scale_y = 0.5
    
    exp_step_up = col.operator("kcycles.light_exposure_step",text="",icon="TRIA_UP", emboss=False)
    exp_step_up.typ = ops_type
    exp_step_up.name = item.name
    exp_step_up.step_up = True
    exp_step_down = col.operator("kcycles.light_exposure_step",text="",icon="TRIA_DOWN", emboss=False)
    exp_step_down.typ = ops_type
    exp_step_down.name = item.name
    exp_step_down.step_up = False

    row_color = row_main.row()
    row_color.scale_x = .37
    if (item.typ == 'L'):
        row_color.prop(obj.data, "color", text="")
    elif (item.typ == 'M'):
        row_color.prop(node_color, "default_value", text="")
    elif (item.typ == 'W'):
        row_color.prop(node_background.inputs["Color"], "default_value", text="")

    row_delete = row_main.row(align=True)
    row_delete.scale_x = 0.75
    row_delete.active = False if (item.typ == 'W') else True
    light_delete = row_delete.operator("kcycles.light_delete", text="", icon="X", emboss=False)
    light_delete.typ = ops_type
    light_delete.name = item.name

def row_light_collection_item(self, row, _context, item):
    cscene = bpy.context.scene.cycles

    row_split = row.split(align=True, factor=1)
    row_split.scale_x = 0.50
    if (item.collapse):
        row_split.prop(item, "collapse", text="", icon="TRIA_RIGHT", emboss=False)
    else:
        row_split.prop(item, "collapse", text="", icon="TRIA_DOWN", emboss=False)

    row.scale_x = 0.90
    row.label(text="", icon="OUTLINER_COLLECTION")

    coll = bpy.data.collections[item.name]
    # print("Collection Viewport: " + str(find_layer_collection(_context.view_layer.layer_collection, item.name).hide_viewport)
    # print("Collection All Viewport: "+ str(bpy.data.collections[item.name].hide_viewport))
    # print("Collection Render: "+ str(bpy.data.collections[item.name].hide_render))

    row.scale_x = 0.45
    if (cscene.kcycles_lights_solo):
        row.active = False
        if (item.name == bpy.context.scene.kcycles_lights[cscene.kcycles_lights_list_index].name):
            row.operator("kcycles.light_show", text="", icon="EVENT_S", emboss=False).typ = ""
        else:
            row.operator("kcycles.light_show", text="", icon="HIDE_ON", emboss=False).typ = ""
        row.active = True
    else:
        if (collection_hide_get(_context, item.name)):
            show = row.operator("kcycles.light_show", text="", icon="HIDE_ON", emboss=False)
        else:
            show = row.operator("kcycles.light_show", text="", icon="HIDE_OFF", emboss=False)
        show.typ = "COLLECTION"
        show.name = item.name

    row.scale_x = 1.2
    row_select = row.row(align=True)
    row_select.scale_x = 0.85
    selected_collections = outliner_selected_collections()
    if coll in selected_collections or bpy.context.view_layer.active_layer_collection.name == item.name:
        sel = row_select.operator("kcycles.light_select", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
    else:
        sel = row_select.operator("kcycles.light_select", text="", icon="RESTRICT_SELECT_ON", emboss=False)
    sel.typ = "COLLECTION"
    sel.name = item.name 

    split_name = row.row(align=True)
    split_name.ui_units_x = 4.6
    split_name.prop(item, "name", text="", emboss=False)

    row_main = row.row(align=True)
    row_main.scale_x = 0.65
    row_main.prop(item, "exposure", text="", slider=True, emboss=True)

    col = row_main.column(align=True)
    col.scale_x = 1.05
    col.scale_y = 0.5
    exp_step_up = col.operator("kcycles.light_exposure_step",text="",icon="TRIA_UP", emboss=False)
    exp_step_up.typ = "COLLECTION"
    exp_step_up.name = item.name
    exp_step_up.step_up = True
    exp_step_down = col.operator("kcycles.light_exposure_step",text="",icon="TRIA_DOWN", emboss=False)
    exp_step_down.typ = "COLLECTION"
    exp_step_down.name = item.name
    exp_step_down.step_up = False

    row_color = row_main.row()
    row_color.scale_x = .37
    row_color.prop(item, "color_tint", text="")

    row_delete = row_main.row(align=True)
    row_delete.scale_x = 0.75
    light_delete = row_delete.operator("kcycles.light_delete", text="", icon="X", emboss=False)
    light_delete.typ = "COLLECTION"
    light_delete.name = item.name

class CYCLES_RENDER_UL_lights(UIList):
    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname):
        scene = bpy.context.scene

        col = layout.column(align=True)   
        col_row = col.row(align = True)
        row = col_row.row(align=True)

        if item.typ == "C":
            row_light_collection_item(self, row, _context, item)
        elif item.typ == "L" or item.typ == "M" or item.typ == "W":
            row_light_item(self, row, _context, item)

    def filter_items(self, context, data, propname):
        #print("filter_items")
        cscene = bpy.context.scene.cycles
        filtered = []
        ordered = []
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        # Initialize with all items visible
        filtered = [self.bitflag_filter_item] * len(items)

        #self.use_filter_sort_reverse = False
        #ordered = helper_funcs.sort_items_by_name(items, "name")
        if (cscene.kcycles_lights_filter_use_collections):
            ordered = list(range(len(items)))
        else:
            ordered = helper_funcs.sort_items_by_name(items, "name")        

        filtered_items = []
        add_collection = True if cscene.kcycles_lights_filter_use_collections else False
        for index, item in enumerate(items):
            if item.typ == 'C' and cscene.kcycles_lights_filter_use_collections:
                add_collection = True
                new_collection = item
                # if ((cscene.kcycles_lights_filter_use_lights and items[index+1].typ == 'L') or
                    # (cscene.kcycles_lights_filter_use_mesh_lights and items[index+1].typ == 'M')):
                    # filtered_items.append(item)
                if item.collapse:
                    collection_collapse = True
                else:
                    collection_collapse = False
            if (((item.typ == 'L' and cscene.kcycles_lights_filter_use_lights) or
                (item.typ == 'M' and cscene.kcycles_lights_filter_use_mesh_lights)) and add_collection):
                filtered_items.append(new_collection)
                add_collection = False
            
            if (((item.typ == 'L' and cscene.kcycles_lights_filter_use_lights) or
                (item.typ == 'M' and cscene.kcycles_lights_filter_use_mesh_lights)) and
                (not cscene.kcycles_lights_filter_use_collections or not collection_collapse) or
                (item.typ == 'W' and cscene.kcycles_lights_filter_use_world)):
                filtered_items.append(item)

        for i, item in enumerate(items):
            if not item in filtered_items:
                filtered[i] &= ~self.bitflag_filter_item

        return filtered,ordered

def view_layer_lightgroup_camera(context, lightgroup_name):
    cscene = context.scene.cycles
    view_layer = context.view_layer
    camera = context.scene.camera

    view_layer_lightgroup = view_layer.lightgroups[lightgroup_name]
    if camera is not None and camera.name in view_layer_lightgroup.cameras and cscene.kcycles_lightgroup_camera_mode:
        view_layer_lightgroup = view_layer_lightgroup.cameras[camera.name]

    return view_layer_lightgroup

class CYCLES_RENDER_UL_lightgroups(UIList):
    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname):
        cscene = _context.scene.cycles

        col = layout.column(align=True)   
        col_row = col.row(align = True)
        row = col_row.row(align=True)
        row.scale_x = 0.80

        row_visible = row.split(align=True, factor=0.90)
        row_visible.scale_x = 0.90
        if (cscene.kcycles_lightgroup_solo):
            row_visible.active = False
            if (item.name == _context.view_layer.active_lightgroup.name):
                row_visible.prop(item, "show_lightgroup", text="", icon="EVENT_S", emboss=False)
            else:
                row_visible.prop(item, "show_lightgroup", text="", icon="HIDE_ON", emboss=False)
            row_visible.active = True
        elif (item.show_lightgroup):
            row_visible.prop(item, "show_lightgroup", text="", icon="HIDE_OFF", emboss=False)
        else:
            row_visible.prop(item, "show_lightgroup", text="", icon="HIDE_ON", emboss=False)        

        row_split = row.split(align=False, factor=1.0)
        row_split.ui_units_x = 6.5 if cscene.kcycles_lightgroup_advanced_tonemapping else 6.1
        row_split.prop(item, "name", text="", emboss=False)

        view_layer_lightgroup = view_layer_lightgroup_camera(_context, item.name)

        if cscene.kcycles_lightgroup_advanced_tonemapping:
            row_main = row.row(align=True)
            row_main.scale_x = 0.65
            row_main.prop(view_layer_lightgroup, "contrast", text="", slider=True, emboss=True)

            row_color = row_main.row()
            row_color.scale_x = .80
            row_color.prop(view_layer_lightgroup, "highlights", text="", slider=True, emboss=True)

            row_wb = row_main.row()
            row_wb.scale_x = 0.82
            row_wb.prop(view_layer_lightgroup, "shadows",text="", slider=True, emboss=True)

            row = row_main.row()
            row.scale_x = 0.80
            row.prop(view_layer_lightgroup, "saturation", text="", slider=True, emboss=True)
        else:
            row_main = row.row(align=True)
            row_main.scale_x = 0.55
            row_main.prop(view_layer_lightgroup, "power", text="", slider=True, emboss=True)
            col = row_main.column(align=True)
            col.scale_x = 1.3
            col.scale_y = 0.5
            exp_step_up = col.operator("kcycles.light_exposure_step",text="",icon="TRIA_UP", emboss=False)
            exp_step_up.typ = "LIGHTGROUP"
            exp_step_up.name = item.name
            exp_step_up.step_up = True
            exp_step_down = col.operator("kcycles.light_exposure_step",text="",icon="TRIA_DOWN", emboss=False)
            exp_step_down.typ = "LIGHTGROUP"
            exp_step_down.name = item.name
            exp_step_down.step_up = False

            row_color = row_main.row()
            row_color.scale_x = .40
            row_color.prop(view_layer_lightgroup, "color_tint", text="")

            row_wb = row_main.row()
            row_wb.scale_x = 0.77
            row_wb.prop(view_layer_lightgroup, "white_balance",text="", slider=True, emboss=True)

            row = row_main.row()
            row.scale_x = 1.00
            if (item.cast_shadow):
                row.prop(item, "cast_shadow", text="", icon="HOLDOUT_ON", emboss=True)
            else:
                row.prop(item, "cast_shadow", text="", icon="HOLDOUT_OFF", emboss=True)

class CYCLES_RENDER_OT_kcycles_collapse_light_collections(bpy.types.Operator):
    bl_idname = "kcycles.collapse_light_collections"
    bl_label = "折叠/展开灯光集合"
    bl_description = "切换折叠或展开灯光集合。\nShift : 展开所有集合。\nCtrl : 折叠所有集合"
    bl_options = {"UNDO"}

    def invoke(self, context, event):
        cscene = context.scene.cycles
        if (len(context.scene.kcycles_lights)):
            auto_collapse = not context.scene.kcycles_lights[0].collapse
            for item in context.scene.kcycles_lights:
                if (item.typ == 'C'):
                    if not event.shift and not event.ctrl:
                        item.collapse = auto_collapse
                    elif event.shift:
                        item.collapse = False
                    elif event.ctrl:
                        item.collapse = True
        return{'FINISHED'}
    def execute(self,context):
        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_refresh_lights(bpy.types.Operator):
    bl_idname = "kcycles.refresh_lights"
    bl_label = "刷新灯光"
    bl_description = "刷新灯光、网格灯光和世界列表。\nShift : 重置灯光集合值"
    bl_options = {"UNDO"}

    def invoke(self, context, event):
        if event.shift:
            refresh_kcycles_lights(True)
        else:
            refresh_kcycles_lights(False)
        return{'FINISHED'}
    def execute(self, context):
        return{'FINISHED'}

class CYCLES_RENDER_PT_kcycles_lightgroups_and_linking(CyclesButtonsPanel, Panel):
    bl_label = "超级灯光"
    bl_parent_id = "RENDER_PT_kcycles"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        cscene = context.scene.cycles

    def draw(self, context):
        layout = self.layout

class CYCLES_RENDER_OT_kcycles_lightgroups_add_collections(bpy.types.Operator):
    bl_idname = "kcycles.lightgroups_add_collections"
    bl_label = "添加所有集合"
    bl_description = "将所有集合和世界添加到新的灯光组"

    def execute(self, context):
        view_layer = context.view_layer
        cscene = context.scene.cycles

        bpy.ops.kcycles.lightgroups_remove_all()        
        collections_in_scene = [c for c in bpy.data.collections if bpy.context.scene.user_of_id(c)]
        for collection in collections_in_scene:
            lightgroup_name = collection.name.replace(".", "_")
            if (lightgroup_name not in view_layer.lightgroups):
                cscene.kcycles_lightgroup = lightgroup_name
                lightgroup = view_layer.lightgroups.add()
                lightgroup.name = lightgroup_name
                lights_added = add_lightgroup_lights(self, collection.objects)
                if (lights_added == False):
                    bpy.ops.scene.view_layer_remove_lightgroup('EXEC_DEFAULT')
                else:
                    add_lighgroup_cameras(self, lightgroup)

        bpy.ops.kcycles.lightgroups_add_world()
        cscene.kcycles_lightgroup = cscene.kcycles_lightgroup
        cscene.kcycles_lightgroup_change += 1

        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_lightgroups_add_world(bpy.types.Operator):
    bl_idname = "kcycles.lightgroups_add_world"
    bl_label = "添加世界"
    bl_description = "将世界添加到新的灯光组"

    def execute(self, context):
        view_layer = context.view_layer
        cscene = context.scene.cycles

        if (bpy.context.scene.world != None):
            lightgroup_name = bpy.context.scene.world.name.replace(".", "_")
            if (lightgroup_name not in view_layer.lightgroups):
                cscene.kcycles_lightgroup = lightgroup_name
                lightgroup = view_layer.lightgroups.add()
                lightgroup.name = lightgroup_name
                bpy.context.scene.world.cycles.lightgroup = lightgroup.name
                add_lighgroup_cameras(self, lightgroup)
                refresh_lightgroup_lights()

        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_lightgroups_add_objects(bpy.types.Operator):
    bl_idname = "kcycles.lightgroups_add_objects"
    bl_label = "添加选中对象"
    bl_description = "将选中的对象或集合添加到新的灯光组"

    def execute(self, context):
        view_layer = context.view_layer
        cscene = context.scene.cycles

        lightgroup_name = "lightgroup"
        objects_add = bpy.context.selected_objects
        if (len(bpy.context.selected_objects) == 0 and len(bpy.context.collection.name) > 0):
            if (bpy.context.collection.name in bpy.data.collections):
                lightgroup_name = bpy.context.collection.name.replace(".", "_")
                objects_add = bpy.data.collections[bpy.context.collection.name].objects
        elif (len(bpy.context.selected_objects)):
            lightgroup_name = bpy.context.view_layer.objects.active.name.replace(".", "_")

        if (lightgroup_name not in view_layer.lightgroups):
            cscene.kcycles_lightgroup = lightgroup_name
            lightgroup = view_layer.lightgroups.add()
            lightgroup.name = lightgroup_name

        add_lightgroup_lights(self, objects_add)
        add_lighgroup_cameras(self, lightgroup)
        refresh_lightgroup_lights()

        cscene.kcycles_lightgroup_change += 1

        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_lightgroup_remove(bpy.types.Operator):
    bl_idname = "kcycles.lightgroup_remove"
    bl_label = "移除"
    bl_description = "移除灯光组"

    def execute(self, context):
        scene = bpy.context.scene
        cscene = scene.cycles
        view_layer = bpy.context.view_layer

        if (cscene.kcycles_lightgroup in view_layer.lightgroups):
            light_shadow_linking_unlink_remove(context)
            bpy.ops.scene.view_layer_remove_lightgroup('EXEC_DEFAULT')
            bpy.context.scene.world.cycles.lightgroup = bpy.context.scene.world.lightgroup

        return{'FINISHED'}

class CYCLES_RENDER_OT_kcycles_lightgroups_remove_all(bpy.types.Operator):
    bl_idname = "kcycles.lightgroups_remove_all"
    bl_label = "移除所有灯光组"
    bl_description = "移除所有灯光组"

    def execute(self, context):
        view_layer = context.view_layer

        view_layer.active_lightgroup_index = 0
        for lightgroup in view_layer.lightgroups:
            bpy.ops.scene.view_layer_remove_lightgroup('EXEC_DEFAULT')
        for lightgroup in view_layer.lightgroups:
            bpy.ops.scene.view_layer_remove_lightgroup('EXEC_DEFAULT')
        for lightgroup in view_layer.lightgroups:
            bpy.ops.scene.view_layer_remove_lightgroup('EXEC_DEFAULT')

        return{'FINISHED'}

class CYCLES_RENDER_PT_kcycles_lightgroups(CyclesButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "CYCLES_RENDER_PT_kcycles_lightgroups_and_linking"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header_preset(self, context):
        CYCLES_PT_kcycles_lightgroups_presets.draw_panel_header(self.layout)

    def draw_header(self, context):
        layout = self.layout

        cscene = context.scene.cycles

        row = layout.row()
        row.scale_x = 0.95
        row.prop(cscene, "use_kcycles_lightgroups_compositing", text="")
        if (len(context.view_layer.lightgroups) > 0):
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            row.prop(cscene, "kcycles_lightgroup_camera_mode", icon="OUTLINER_DATA_CAMERA", text="")
            row.label(text="灯光组 • " + context.view_layer.active_lightgroup.name)
        else:
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            row.prop(cscene, "kcycles_lightgroup_camera_mode", icon="OUTLINER_DATA_CAMERA", text="")
            row.label(text="灯光组混合 • 无")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        cscene = context.scene.cycles
        view_layer = context.view_layer

        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.scale_x = 1.2
        row.scale_y = 0.9
        row.prop(cscene, "kcycles_lightgroup_advanced_tonemapping", text = "", icon="NODE_TEXTURE", icon_only=True)
        row.prop(cscene, "kcycles_lightgroup_solo", text = "", icon="EVENT_S", icon_only=True)
        row.prop(cscene, "kcycles_lightgroup_remainder", text = "", icon="EVENT_R", icon_only=True)
        row.prop(cscene, "kcycles_lightgroup_compositor", text = "", icon="NODE_COMPOSITING", icon_only=True)
        row.label(text=" ")
        row.operator("kcycles.lightgroups_add_objects", icon='OUTLINER_DATA_LIGHT', text="")
        row.operator("kcycles.lightgroups_add_world", icon='WORLD', text="")
        row.operator("kcycles.lightgroups_add_collections", icon='OUTLINER_OB_GROUP_INSTANCE', text="")
        row.operator("kcycles.lightgroup_apply_changes_to_lights", icon='UV_SYNC_SELECT', text="")
        row.operator("kcycles.lightgroups_remove_all", icon='TRASH', text="")

        row = layout.row(align=True)
        row.template_list("CYCLES_RENDER_UL_lightgroups", "lightgroups", view_layer,
                          "lightgroups", view_layer, "active_lightgroup_index", rows=3, maxrows=5)
        if not cscene.kcycles_lightgroup_advanced_tonemapping:
            col = row.column()
            sub = col.column(align=True)
            sub.operator("scene.view_layer_add_lightgroup", icon='ADD', text="")
            sub.operator("kcycles.lightgroup_remove", icon='REMOVE', text="")
            sub.operator("scene.view_layer_move_lightgroup", icon='TRIA_UP', text="").direction = 'UP'
            sub.operator("scene.view_layer_move_lightgroup", icon='TRIA_DOWN', text="").direction = 'DOWN'

class CYCLES_RENDER_PT_filter_menu_lights(Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "HEADER"
    bl_label = "筛选灯光列表"
    bl_context = "none"

    def draw(self, context):
        layout = self.layout
        cscene = context.scene.cycles

        layout.label(text = "筛选灯光")
        layout.separator(factor=1)
        layout.prop(cscene, "kcycles_lights_filter_use_collections")
        layout.prop(cscene, "kcycles_lights_filter_use_lights")
        layout.prop(cscene, "kcycles_lights_filter_use_mesh_lights")
        layout.prop(cscene, "kcycles_lights_filter_use_world")
        layout.separator(factor=1)

class CYCLES_RENDER_PT_kcycles_lights(CyclesButtonsPanel, Panel):
    bl_label = ""
    bl_parent_id = "CYCLES_RENDER_PT_kcycles_lightgroups_and_linking"

    def draw_header(self, context):
        layout = self.layout
        cscene = context.scene.cycles

        # if (cscene.kcycles_lightgroup in context.view_layer.lightgroups):
            # view_layer_lightgroup = context.view_layer.lightgroups[cscene.kcycles_lightgroup]

        row = layout.row()
        row.label(text="灯光混合")
        row.prop(cscene,"kcycles_lights_mode", text="", expand=True)
        if (cscene.kcycles_lights_mode == "LIGHT"):
            row = layout.row(align=True)
            row.operator("kcycles.refresh_lights", icon="FILE_REFRESH", text = "")
            row.prop(cscene, "kcycles_lights_solo", text = "", icon="EVENT_S", icon_only=True)
            row.operator("kcycles.collapse_light_collections", icon="COLLAPSEMENU", text="")
            row.menu("VIEW3D_MT_light_add",text="",icon="PLUS")
            row.popover(panel="CYCLES_RENDER_PT_filter_menu_lights", text="", icon='FILTER',)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles
        view_layer = context.view_layer
        
        if (cscene.kcycles_lights_mode == "LIGHTGROUP"):
            if (cscene.kcycles_lightgroup in view_layer.lightgroups and cscene.kcycles_lightgroup != "Lightgroup_remainder"):
                row = layout.row(align=True)
                row.template_list("CYCLES_RENDER_UL_lightgroup_lights", "LinkedObjects",  bpy.context.scene, "lightgroup_lights",
                    view_layer.lightgroups[cscene.kcycles_lightgroup], "active_light_index", rows=2, maxrows=5)
                col = row.column()
                sub = col.column(align=True)
                sub.operator("kcycles.lightgroup_lights_add", icon='ADD', text="")
                sub.operator("kcycles.lightgroup_lights_remove", icon='REMOVE', text="")
                sub.operator("kcycles.lightgroup_lights_select", icon='RESTRICT_SELECT_ON', text="")
        else:
            if (bpy.context.scene.kcycles_lights.keys() == []):
                row = layout.row(align=True)
                row.alert = True
                row.label(text="灯光列表为空，请点击刷新按钮。")
            row = layout.row(align=True)
            row.template_list("CYCLES_RENDER_UL_lights", "Light List", bpy.context.scene, "kcycles_lights",
            cscene, "kcycles_lights_list_index", rows=2, maxrows=8)

class CYCLES_RENDER_PT_kcycles_lightgroups_linking(CyclesButtonsPanel, Panel):
    bl_label = "灯光与阴影链接"
    bl_parent_id = "CYCLES_RENDER_PT_kcycles_lightgroups_and_linking"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        cscene = context.scene.cycles

        if (cscene.kcycles_lightgroup in context.view_layer.lightgroups):
            view_layer_lightgroup = context.view_layer.lightgroups[cscene.kcycles_lightgroup]

            row = layout.row()
            row.scale_x = 0.95
            row.prop(view_layer_lightgroup, "use_light_linking", text="")
            row.active = not is_kcycles_lightgroup_world_lightgroup() and (view_layer_lightgroup.use_light_linking or view_layer_lightgroup.use_shadow_linking)
            row.prop(view_layer_lightgroup, "use_shadow_linking", icon="HOLDOUT_ON", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        scene = context.scene
        cscene = scene.cycles
        view_layer = context.view_layer

        # # Test code for calling light linking operator must be inside operator function
        # context_override = {'object': bpy.context.selected_objects}
        # with bpy.context.temp_override(**context_override):
            # print(context_override)
            # print(context_override['object'])
            # for obj in context_override['object']:
                # print(obj.name)
                # print(obj.light_linking)
            # print(*context_override)
            # print(*context_override['object'])
            # print(str(**context_override))
            # bpy.ops.object.light_linking_receivers_link()

        if (cscene.kcycles_lightgroup in view_layer.lightgroups):
            row = layout.row(align=True)
            row.template_list("CYCLES_RENDER_UL_lightgroup_linking", "LinkedObjects", view_layer.lightgroups[cscene.kcycles_lightgroup],
                "linked_objects", view_layer.lightgroups[cscene.kcycles_lightgroup], "active_linking_index", rows=2,  maxrows=5)
            if (not is_kcycles_lightgroup_world_lightgroup()):
                col = row.column()
                sub = col.column(align=True)
                sub.operator("kcycles.linked_objects_add", icon='ADD', text="")
                sub.operator("kcycles.linked_objects_remove", icon='REMOVE', text="")

classes = (
    CYCLES_RENDER_PT_kcycles_lightgroups,
    CYCLES_RENDER_PT_kcycles_lights,
    CYCLES_RENDER_PT_kcycles_lightgroups_linking,
    CYCLES_RENDER_OT_kcycles_lightgroup_lights_add,
    CYCLES_RENDER_OT_kcycles_lightgroup_lights_remove,
    CYCLES_RENDER_OT_kcycles_lightgroup_lights_select,
    CYCLES_RENDER_OT_kcycles_linked_objects_add,
    CYCLES_RENDER_OT_kcycles_linked_objects_remove,
    CYCLES_RENDER_OT_kcycles_lightgroups_camera_sync,
    CYCLES_RENDER_OT_kcycles_lightgroups_add_world,
    CYCLES_RENDER_OT_kcycles_lightgroups_add_collections,
    CYCLES_RENDER_OT_kcycles_lightgroups_add_objects,
    CYCLES_RENDER_OT_kcycles_lightgroups_remove_all,
    CYCLES_RENDER_OT_kcycles_lightgroup_apply_changes_to_lights,
    CYCLES_RENDER_OT_kcycles_lightgroup_remove,
    CYCLES_RENDER_UL_lightgroups,
    CYCLES_RENDER_UL_lightgroup_lights,
    CYCLES_RENDER_UL_lightgroup_linking,
    KCYCLES_OT_light_exposure_step,
    CYCLES_PT_kcycles_lightgroups_presets,
    CYCLES_RENDER_UL_lights,
    CYCLES_RENDER_OT_kcycles_light_select,
    CYCLES_RENDER_OT_kcycles_light_show,
    CYCLES_RENDER_PT_filter_menu_lights,
    CYCLES_RENDER_OT_kcycles_collapse_light_collections,
    CYCLES_RENDER_OT_kcycles_refresh_lights,
    KCYCLES_OT_light_delete,
)

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)