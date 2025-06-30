bl_info = {
    "name": "One Click Splitting",
    "author": "tht master",
    "version": (1, 7, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > OneClickSplit",
    "description": "Split object in half or by a custom cutting plane (Guide)",
    "category": "Object"
}

import bpy
from mathutils import Vector

def create_cutting_plane(location, rotation):
    bpy.ops.mesh.primitive_plane_add(size=10, enter_editmode=False, location=location)
    plane = bpy.context.active_object
    plane.name = "CuttingPlane"
    plane.scale = (100, 100, 100)
    plane.rotation_euler = rotation
    return plane

class OBJECT_OT_create_cut_guide(bpy.types.Operator):
    bl_idname = "object.create_cut_guide"
    bl_label = "Create Guide Plane"
    bl_description = "Create a plane to use as a cutting guide (can move/rotate)"

    def execute(self, context):
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, location=context.scene.cursor.location)
        guide = bpy.context.active_object
        guide.name = "CutGuide"
        guide.display_type = 'SOLID'
        guide.show_in_front = True
        return {'FINISHED'}

class OBJECT_OT_split_custom_plane(bpy.types.Operator):
    bl_idname = "object.split_custom_plane"
    bl_label = "Split by Guide"
    bl_description = "Split selected mesh using 'CutGuide' plane"

    def execute(self, context):
        obj = context.active_object
        guide = bpy.data.objects.get("CutGuide")

        if not guide:
            self.report({'ERROR'}, "No object named 'CutGuide' found")
            return {'CANCELLED'}

        if not obj or obj.type != 'MESH' or obj == guide:
            self.report({'ERROR'}, "Please select the object to cut (not the CutGuide)")
            return {'CANCELLED'}

        obj1 = obj.copy(); obj1.data = obj.data.copy()
        obj2 = obj.copy(); obj2.data = obj.data.copy()
        context.collection.objects.link(obj1)
        context.collection.objects.link(obj2)

        plane = guide.copy(); plane.data = guide.data.copy()
        plane.name = "CuttingPlane"
        context.collection.objects.link(plane)
        plane.scale = (100, 100, 100)

        for o, op in [(obj1, 'INTERSECT'), (obj2, 'DIFFERENCE')]:
            mod = o.modifiers.new(name="CutMod", type='BOOLEAN')
            mod.operation = op
            mod.object = plane
            mod.solver = 'EXACT'
            context.view_layer.objects.active = o
            bpy.ops.object.modifier_apply(modifier=mod.name)

        bpy.data.objects.remove(plane, do_unlink=True)
        if guide.name in bpy.context.scene.objects:
            bpy.data.objects.remove(guide, do_unlink=True)

        obj.hide_set(True)
        return {'FINISHED'}

class OBJECT_OT_split_in_half(bpy.types.Operator):
    bl_idname = "object.split_in_half"
    bl_label = "Split in Half"
    bl_description = "Split selected object in half along X, Y, or Z axis"

    axis: bpy.props.EnumProperty(
        name="Axis",
        items=[('X', 'X', ''), ('Y', 'Y', ''), ('Z', 'Z', '')],
        default='Z'
    )

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object first")
            return {'CANCELLED'}

        obj1 = obj.copy(); obj1.data = obj.data.copy()
        obj2 = obj.copy(); obj2.data = obj.data.copy()
        context.collection.objects.link(obj1)
        context.collection.objects.link(obj2)

        loc = obj.location
        plane = create_cutting_plane(loc, (0, 0, 0))

        if self.axis == 'X':
            plane.rotation_euler[1] = 1.5708
        elif self.axis == 'Y':
            plane.rotation_euler[0] = 1.5708
        elif self.axis == 'Z':
            plane.rotation_euler[0] = 0

        for o, op in [(obj1, 'INTERSECT'), (obj2, 'DIFFERENCE')]:
            mod = o.modifiers.new(name="CutMod", type='BOOLEAN')
            mod.operation = op
            mod.object = plane
            mod.solver = 'EXACT'
            context.view_layer.objects.active = o
            bpy.ops.object.modifier_apply(modifier=mod.name)

        bpy.data.objects.remove(plane, do_unlink=True)
        obj.hide_set(True)
        return {'FINISHED'}

class VIEW3D_PT_oneclick_split(bpy.types.Panel):
    bl_label = "One Click Splitting"
    bl_idname = "VIEW3D_PT_oneclick_split"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "OneClickSplit"

    def draw(self, context):
        layout = self.layout
        layout.label(text="✂ Split in Half:")
        layout.operator("object.split_in_half", text="Split Z").axis = 'Z'
        layout.operator("object.split_in_half", text="Split X").axis = 'X'
        layout.operator("object.split_in_half", text="Split Y").axis = 'Y'

        layout.separator()
        layout.label(text="🧭 Custom Guide Cut:")
        layout.operator("object.create_cut_guide", text="Create Guide Plane")
        layout.operator("object.split_custom_plane", text="Split by Guide")

classes = [
    OBJECT_OT_create_cut_guide,
    OBJECT_OT_split_custom_plane,
    OBJECT_OT_split_in_half,
    VIEW3D_PT_oneclick_split
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
