bl_info = {
    "name": "2D_Canvas",
    "author": "Arjo Nagelhout",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "description": "Quick canvas creation",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper, object_data_add

def view3d_find( return_area = False ):
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    if return_area: return region, rv3d, v3d, area
                    return region, rv3d, v3d
    return None, None


def add_canvas(self, context):
    # CREATE A CANVAS TO DRAW ON
    width = self.width
    height = self.height
    name = self.name
    align_view = self.align_view
    only_z = self.only_z
    
    # CREATE THE MESH
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=context.scene.cursor.location)
    obj = bpy.context.object
    obj.name = name
    obj.show_wire = True

    bpy.ops.transform.rotate(value=1.5708, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    #bpy.ops.transform.resize(value=(1, width/500, 1), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.resize(value=(1, 1, height/width), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

    if (align_view):
        r3d, rv3d, v3d = view3d_find()
        eulerangles = rv3d.view_rotation.to_euler()
        
        bpy.context.object.rotation_euler = eulerangles
        
        
        
        bpy.ops.transform.rotate(value=-1.5708, orient_axis='Y', orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.transform.rotate(value=-1.5708, orient_axis='X', orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        
        if (only_z):
            
            bpy.context.object.rotation_euler[0] = 0
            bpy.context.object.rotation_euler[1] = 0
        
    
    


    # CREATE THE TEXTURE

    texture = bpy.data.images.new(name=name, width=width, height=height, alpha=True)
    texture.pixels[:] = (0.0, 0.0, 0.0, 0.0) * width * height


    # CREATE THE MATERIAL

    mat = bpy.data.materials.new(name=name)
    obj.data.materials.append(mat)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes

    node_image = nodes.new(type="ShaderNodeTexImage")
    node_image.location = -400, 300
    node_image.image = texture

    principled_bsdf = nodes.get("Principled BSDF")

    links = mat.node_tree.links
    links.new(node_image.outputs["Color"], principled_bsdf.inputs["Base Color"])
    links.new(node_image.outputs["Alpha"], principled_bsdf.inputs["Alpha"])

    # SET BLEND MODE
    bpy.context.object.active_material.blend_method = 'CLIP'
    bpy.context.object.active_material.shadow_method = 'CLIP'
    bpy.context.object.active_material.alpha_threshold = 0
    

    # SWITCH TO DRAWING

    bpy.ops.paint.texture_paint_toggle()

class OBJECT_OT_add_canvas(Operator):
    """Create a new 2D Canvas"""
    bl_idname = "mesh.add_canvas"
    bl_label = "Add Canvas"
    
    width = bpy.props.IntProperty(name="width", default=1024)
    height = bpy.props.IntProperty(name="height", default=1024)
    name = bpy.props.StringProperty(name="name", default="Canvas")
    align_view = bpy.props.BoolProperty(name="align view", default=True)
    only_z = bpy.props.BoolProperty(name="only Z", default=False)
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):

        add_canvas(self, context)

        return {'FINISHED'}


# Registration

def add_canvas_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_canvas.bl_idname,
        text="Canvas",
        icon='MESH_PLANE')


def register():
    bpy.utils.register_class(OBJECT_OT_add_canvas)
    bpy.types.VIEW3D_MT_add.append(add_canvas_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_canvas)
    bpy.types.VIEW3D_MT_add.remove(add_canvas_button)


if __name__ == "__main__":
    register()