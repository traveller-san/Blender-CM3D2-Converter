# 「3Dビュー」エリア → ポーズモード → Ctrl+A (ポーズ → 適用)
import bpy
from . import common
from . import compat


# メニュー等に項目追加
def menu_func(self, context):
    self.layout.separator()
    self.layout.operator('pose.apply_prime_field', icon_value=common.kiss_icon())


@compat.BlRegister()
class CNV_OT_apply_prime_field(bpy.types.Operator):
    bl_idname = 'pose.apply_prime_field'
    bl_label = "Apply Prime Field"
    bl_description = "A body will be created that makes custom modeling easy with the current pose."
    bl_options = {'REGISTER', 'UNDO'}

    is_apply_armature_modifier = bpy.props.BoolProperty(name="Apply Armature Modifier", default=True )
    is_deform_preserve_volume  = bpy.props.BoolProperty(name="Preserve Volume"        , default=True )
    is_keep_original           = bpy.props.BoolProperty(name="Keep Original"          , default=True )
    is_swap_prime_field        = bpy.props.BoolProperty(name="Swap Prime Field"       , default=False)


    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if ob and ob.type == 'ARMATURE':
            return True
        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, 'is_apply_armature_modifier')
        self.layout.prop(self, 'is_deform_preserve_volume' )
        if context.active_object.data.get('is T Stance'):
            self.layout.prop(self, 'is_keep_original')

    def execute(self, context):
        ob = context.active_object
        arm = ob.data
        pose = ob.pose

        pre_selected_objects = context.selected_objects
        pre_selected_pose_bones = context.selected_pose_bones
        pre_mode = ob.mode
        pre_frame = context.scene.frame_current

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        compat.set_select(ob, True)

        if self.is_swap_prime_field:
            context.scene.frame_set(1)

        if self.is_apply_armature_modifier:
            override = context.copy()
            for o in ob.children:
                override['object'], override['active_object'] = o, o
                if o.type == 'MESH' and len(o.modifiers) and bpy.ops.object.forced_modifier_apply.poll(override):
                    for mod in o.modifiers:
                        if mod.type == 'ARMATURE':
                            mod.use_deform_preserve_volume = self.is_deform_preserve_volume
                            if not mod.object == ob:
                                had_armature = False
                            else:
                                had_armature = True
                                old_name                = mod.name                      
                                old_show_expanded       = mod.show_expanded             
                                old_show_in_editmode    = mod.show_in_editmode          
                                old_show_on_cage        = mod.show_on_cage              
                                old_show_render         = mod.show_render               
                                old_show_viewport       = mod.show_viewport             
                                old_use_apply_on_spline = mod.use_apply_on_spline       
                                old_invert_vertex_group = mod.invert_vertex_group       
                                old_use_bone_envelopes  = mod.use_bone_envelopes        
                                #old_use_multi_modifier  = mod.use_multi_modifier        
                                old_use_vertex_groups   = mod.use_vertex_groups         
                                old_vertex_group        = mod.vertex_group        
                    apply_results = bpy.ops.object.forced_modifier_apply(override, apply_viewport_visible=True)
                    if ('FINISHED' in apply_results) and had_armature:
                        new_mod = o.modifiers.new(name=old_name, type='ARMATURE')
                        new_mod.use_deform_preserve_volume = self.is_deform_preserve_volume
                        new_mod.show_expanded       = old_show_expanded      
                        new_mod.show_in_editmode    = old_show_in_editmode   
                        new_mod.show_on_cage        = old_show_on_cage       
                        new_mod.show_render         = old_show_render        
                        new_mod.show_viewport       = old_show_viewport      
                        new_mod.use_apply_on_spline = old_use_apply_on_spline
                        new_mod.invert_vertex_group = old_invert_vertex_group
                        new_mod.use_bone_envelopes  = old_use_bone_envelopes 
                        #new_mod.use_multi_modifier  = old_use_multi_modifier 
                        new_mod.use_vertex_groups   = old_use_vertex_groups  
                        new_mod.vertex_group        = old_vertex_group       

        temp_ob = ob.copy()
        temp_arm = arm.copy()
        temp_ob.data = temp_arm
        compat.link(context.scene, temp_ob)
        
        compat.set_active(context, ob)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply()
        bpy.ops.pose.constraints_clear()
        ob.animation_data_clear()
        
        if arm.get("is T Stance") and self.is_keep_original and not self.is_swap_prime_field:
            context.scene.frame_set(1)
        else:
            compat.set_active(context, temp_ob)
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            temp_ob.animation_data_clear()
            bpy.ops.pose.transforms_clear()
            bpy.ops.object.mode_set(mode='OBJECT')
            compat.set_select(temp_ob, False)

        compat.set_active(context, ob)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')

        consts = []
        for bone in pose.bones:
            const = bone.constraints.new('COPY_TRANSFORMS')
            const.target = temp_ob
            const.subtarget = bone.name
            consts.append(const)

        for i in range(10):
            for const in consts:
                const.mute = not bool(i % 2)

            if i % 2:
                bpy.ops.pose.visual_transform_apply()
            else:
                bpy.ops.pose.transforms_clear()

            for bone in pose.bones:
                bone.keyframe_insert(data_path='location'           , frame=i, group=bone.name)
                bone.keyframe_insert(data_path='rotation_euler'     , frame=i, group=bone.name)
                bone.keyframe_insert(data_path='rotation_quaternion', frame=i, group=bone.name)
                bone.keyframe_insert(data_path='scale'              , frame=i, group=bone.name)
        
        bpy.ops.pose.constraints_clear()
        common.remove_data(temp_arm)
        try:
            common.remove_data(temp_ob)
        except:
            pass

        bpy.ops.pose.select_all(action='DESELECT')
        if pre_selected_pose_bones:
            for bone in pre_selected_pose_bones:
                arm.bones[bone.name].select = True

        if self.is_swap_prime_field and arm.get('is T Stance'):
            arm['is T Stance'] = False
        else:
            arm['is T Stance'] = True

        if pre_selected_objects:
            for o in pre_selected_objects:
                compat.set_select(o, True)
        compat.set_active(context, ob)
        bpy.ops.object.mode_set(mode=pre_mode)

        context.scene.frame_set(pre_frame)
        return {'FINISHED'}
