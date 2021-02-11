import bpy
from . import common
from . import compat

def menu_func(self, context):
    icon_id = common.kiss_icon()
    self.layout.separator()
    self.layout.operator('script.hide_cm3d2_bones', icon_value=icon_id)
    self.layout.operator('script.show_cm3d2_bones', icon_value=icon_id)

@compat.BlRegister()
class CNV_OT_hide_cm3d2_bones(bpy.types.Operator):
    bl_idname = 'script.hide_cm3d2_bones'
    bl_label = "Hide SCL, IK, and momo bones"
    bl_description = "Hides bones in the current pose containing 'SCL', 'IK', and 'momo' in their names"
    bl_options = {'REGISTER'}

    def execute(self, context):
        for obj in context.selected_objects:
            pose = obj.pose
            for pose_bone in pose.bones:
                bone = pose_bone.bone
                if '_IK_' in bone.name or '_SCL_' in bone.name or 'momo' in bone.name:
                    bone.hide = True
        return {'FINISHED'}

@compat.BlRegister()
class CNV_OT_show_cm3d2_bones(bpy.types.Operator):
    bl_idname = 'script.show_cm3d2_bones'
    bl_label = "Show SCL, IK, and momo bones"
    bl_description = "Shows bones in the current pose containing 'SCL', 'IK', and 'momo' in their names"
    bl_options = {'REGISTER'}

    def execute(self, context):
        for obj in context.selected_objects:
            pose = obj.pose
            for pose_bone in pose.bones:
                bone = pose_bone.bone
                if '_IK_' in bone.name or '_SCL_' in bone.name or 'momo' in bone.name:
                    bone.hide = False
        return {'FINISHED'}
