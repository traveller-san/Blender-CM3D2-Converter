# 「3Dビュー」エリア → ポーズモード → Ctrl+A (ポーズ → 適用)
import bpy
from . import common
from . import compat


# メニュー等に項目追加
def menu_func(self, context):
    self.layout.separator()
    self.layout.operator('pose.apply_prime_field', icon_value=common.kiss_icon())
    self.layout.operator('pose.copy_prime_field' , icon_value=common.kiss_icon())

@compat.BlRegister()
class CNV_OT_copy_prime_field(bpy.types.Operator):
    bl_idname = 'pose.copy_prime_field'
    bl_label = "Copy Prime Field"
    bl_description = "Copies the visual pose of the selected object to the prime field of the active object"
    bl_options = {'REGISTER', 'UNDO'}

    #is_apply_armature_modifier = bpy.props.BoolProperty(name="Apply Armature Modifier", default=True )
    #is_deform_preserve_volume  = bpy.props.BoolProperty(name="Preserve Volume"        , default=True )
    #is_keep_original           = bpy.props.BoolProperty(name="Keep Original"          , default=True )
    #is_swap_prime_field        = bpy.props.BoolProperty(name="Swap Prime Field"       , default=False)
    #is_bake_drivers            = bpy.props.BoolProperty(name="Bake Drivers"           , default=False, description="Enable keyframing of driven properties, locking sliders and twist bones for final apply")
    
    is_only_selected = bpy.props.BoolProperty(name="Only Selected", default=True )
    is_key_location  = bpy.props.BoolProperty(name="Key Location" , default=True )
    is_key_rotation  = bpy.props.BoolProperty(name="Key Rotation" , default=True )
    is_key_scale     = bpy.props.BoolProperty(name="Key Scale"    , default=True )
    is_apply_prime   = bpy.props.BoolProperty(name="Apply Prime"  , default=False, options={'HIDDEN'})
    


    @classmethod
    def poll(cls, context):
        target_ob, source_ob = common.get_target_and_source_ob(context)
        if target_ob and source_ob:
            return True
        else:
            return False

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, 'is_only_selected')
        self.layout.prop(self, 'is_key_location' )
        self.layout.prop(self, 'is_key_rotation' )
        self.layout.prop(self, 'is_key_scale'    )

    def execute(self, context):
        ob, temp_ob = common.get_target_and_source_ob(context)
        pose = ob.pose
        arm = ob.data

        pre_selected_pose_bones = context.selected_pose_bones
        pre_mode = ob.mode
        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.constraints_clear()

        consts = []
        bones = pre_selected_pose_bones if self.is_only_selected else pose.bones
        for bone in bones:
            if bone.name in temp_ob.data.bones:
                const = bone.constraints.new('COPY_TRANSFORMS')
                const.target = temp_ob
                const.subtarget = bone.name
                consts.append(const)

        for i in range(10):
            is_prime_frame = not bool(i % 2) if arm.get("is T Stance") else bool(i % 2)
            if self.is_apply_prime:
                is_prime_frame = not is_prime_frame
            for const in consts:
                const.mute = not is_prime_frame

            if is_prime_frame:
                bpy.ops.pose.visual_transform_apply()
            else:
                bpy.ops.pose.transforms_clear()

            for bone in pose.bones:
                if self.is_key_location:
                    bone.keyframe_insert(data_path='location'           , frame=i, group=bone.name)
                if self.is_key_rotation:
                    bone.keyframe_insert(data_path='rotation_euler'     , frame=i, group=bone.name)
                    bone.keyframe_insert(data_path='rotation_quaternion', frame=i, group=bone.name)
                if self.is_key_scale   :
                    bone.keyframe_insert(data_path='scale'              , frame=i, group=bone.name)
        
        bpy.ops.pose.constraints_clear()

        bpy.ops.pose.select_all(action='DESELECT')
        if pre_selected_pose_bones:
            for bone in pre_selected_pose_bones:
                arm.bones[bone.name].select = True

        if pre_mode: 
            bpy.ops.object.mode_set(mode=pre_mode)
        
        return {'FINISHED'}


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
    is_bake_drivers            = bpy.props.BoolProperty(name="Bake Drivers"           , default=False, description="Enable keyframing of driven properties, locking sliders and twist bones for final apply")
    
    was_t_stance = False

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
        self.layout.prop(self, 'is_bake_drivers'           )
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
            anim_data = temp_ob.animation_data
            drivers = anim_data.drivers
            for driver in drivers.values():
                drivers.remove(driver)
            context.scene.frame_set(1)
            bpy.ops.pose.transforms_clear()
        else:
            compat.set_active(context, temp_ob)
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            temp_ob.animation_data_clear()
            bpy.ops.pose.transforms_clear()
            bpy.ops.object.mode_set(mode='OBJECT')
            compat.set_select(temp_ob, False)
        
        if self.is_swap_prime_field and arm.get('is T Stance'):
            arm['is T Stance'] = False
        else:
            arm['is T Stance'] = True

        # CNV_OT_copy_prime_field.execute()
        compat.set_select(temp_ob, True)
        compat.set_active(context, ob)
        response = bpy.ops.pose.copy_prime_field(is_only_selected=False, is_key_location=self.is_bake_drivers, is_key_scale=self.is_bake_drivers, is_apply_prime=True)

        if not 'FINISHED' in response:
            return response

        common.remove_data(temp_arm)
        try:
            common.remove_data(temp_ob)
        except:
            pass
        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        if pre_selected_pose_bones:
            for bone in pre_selected_pose_bones:
                arm.bones[bone.name].select = True

        if pre_selected_objects:
            for o in pre_selected_objects:
                compat.set_select(o, True)
        compat.set_active(context, ob)
        bpy.ops.object.mode_set(mode=pre_mode)

        context.scene.frame_set(pre_frame)
        return {'FINISHED'}
