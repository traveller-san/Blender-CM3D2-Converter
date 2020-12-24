# 「プロパティ」エリア → 「オブジェクト」タブ
import re
import bpy
from . import common
from . import compat


# メニュー等に項目追加
def menu_func(self, context):
    ob = context.active_object
    if not ob or ob.type != 'MESH':
        return

    bone_data_count = 0
    if 'BoneData:0' in ob and 'LocalBoneData:0' in ob:
        for key in ob.keys():
            if re.search(r'^(Local)?BoneData:\d+$', key):
                bone_data_count += 1
    enabled_clipboard = False
    clipboard = context.window_manager.clipboard
    if 'BoneData:' in clipboard and 'LocalBoneData:' in clipboard:
        enabled_clipboard = True

    if bone_data_count or enabled_clipboard:
        col = self.layout.column(align=True)
        row = col.row(align=True)
        row.label(text="CM3D2 Bone Data", icon_value=common.kiss_icon())
        sub_row = row.row()
        sub_row.alignment = 'RIGHT'
        if 'BoneData:0' in ob and 'LocalBoneData:0' in ob:
            bone_data_count = 0
            for key in ob.keys():
                if re.search(r'^(Local)?BoneData:\d+$', key):
                    bone_data_count += 1
            sub_row.label(text=str(bone_data_count), icon='CHECKBOX_HLT')
        else:
            sub_row.label(text="0", icon='CHECKBOX_DEHLT')
        row = col.row(align=True)
        row.operator('object.copy_object_bone_data_property', icon='COPYDOWN', text="Copy")
        row.operator('object.paste_object_bone_data_property', icon='PASTEDOWN', text="Paste")
        row.operator('object.remove_object_bone_data_property', icon='X', text="")

@compat.BlRegister()
class CNV_OT_copy_object_bone_data_property(bpy.types.Operator):
    bl_idname = 'object.copy_object_bone_data_property'
    bl_label = "Copy the Bone Data from the object's custom properties"
    bl_description = "Copies the bone Data in the object's custom properties to the clipboard."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if ob:
            if 'BoneData:0' in ob and 'LocalBoneData:0' in ob:
                return True
        return False

    def execute(self, context):
        output_text = ""
        ob = context.active_object
        pass_count = 0
        if 'BaseBone' in ob:
            output_text += "BaseBone:" + ob['BaseBone'] + "\n"
        for i in range(99999):
            name = "BoneData:" + str(i)
            if name in ob:
                output_text += "BoneData:" + ob[name] + "\n"
            else:
                pass_count += 1
            if 10 < pass_count:
                break
        pass_count = 0
        for i in range(99999):
            name = "LocalBoneData:" + str(i)
            if name in ob:
                output_text += "LocalBoneData:" + ob[name] + "\n"
            else:
                pass_count += 1
            if 10 < pass_count:
                break
        context.window_manager.clipboard = output_text
        self.report(type={'INFO'}, message="Bone Data was copied to the clipboard.")
        return {'FINISHED'}


@compat.BlRegister()
class CNV_OT_paste_object_bone_data_property(bpy.types.Operator):
    bl_idname = 'object.paste_object_bone_data_property'
    bl_label = "Paste Bone Data"
    bl_description = "Paste Bone Data from the clipboard into the object's custom properties. NOTE:Any data in custom properties will be replaced."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if ob:
            clipboard = context.window_manager.clipboard
            if 'BoneData:' in clipboard and 'LocalBoneData:' in clipboard:
                return True
        return False

    def execute(self, context):
        ob = context.active_object
        pass_count = 0
        for i in range(99999):
            name = "BoneData:" + str(i)
            if name in ob:
                del ob[name]
            else:
                pass_count += 1
            if 10 < pass_count:
                break
        pass_count = 0
        for i in range(99999):
            name = "LocalBoneData:" + str(i)
            if name in ob:
                del ob[name]
            else:
                pass_count += 1
            if 10 < pass_count:
                break
        bone_data_count = 0
        local_bone_data_count = 0
        for line in context.window_manager.clipboard.split("\n"):
            if line.startswith('BaseBone:'):
                ob['BaseBone'] = line[9:]  # len('BaseData:') == 9
                continue

            if line.startswith('BoneData:'):
                if line.count(',') >= 4:
                    name = "BoneData:" + str(bone_data_count)
                    ob[name] = line[9:]  # len('BoneData:') == 9
                    bone_data_count += 1
                continue

            if line.startswith('LocalBoneData:'):
                if line.count(',') == 1:
                    name = "LocalBoneData:" + str(local_bone_data_count)
                    ob[name] = line[14:]  # len('LocalBoneData:') == 14
                    local_bone_data_count += 1
        self.report(type={'INFO'}, message="Data was pasted, mission accomplished")
        return {'FINISHED'}


@compat.BlRegister()
class CNV_OT_remove_object_bone_data_property(bpy.types.Operator):
    bl_idname = 'object.remove_object_bone_data_property'
    bl_label = "Remove the bone Data"
    bl_description = "Remove all bone Data for the custom properties"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        if ob:
            if 'BoneData:0' in ob and 'LocalBoneData:0' in ob:
                return True
        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(text="Remove all bone Data form the custom properties?", icon='CANCEL')

    def execute(self, context):
        ob = context.active_object
        pass_count = 0
        if 'BaseBone' in ob:
            del ob['BaseBone']
        for i in range(99999):
            name = "BoneData:" + str(i)
            if name in ob:
                del ob[name]
            else:
                pass_count += 1
            if 10 < pass_count:
                break
        pass_count = 0
        for i in range(99999):
            name = "LocalBoneData:" + str(i)
            if name in ob:
                del ob[name]
            else:
                pass_count += 1
            if 10 < pass_count:
                break
        self.report(type={'INFO'}, message="Bone Data was removed. Mission Accomplished.")
        return {'FINISHED'}




"""
- - - - - - For Bone Sliders - - - - - - 
"""
@compat.BlRegister()
class CNV_PG_cm3d2_bone_morph(bpy.types.PropertyGroup):
    bl_idname = 'CNV_PG_cm3d2_bone_morph'

    def __calcMeasurements(self, context):                                               
        num    =  1340                         +                   self.sintyou * 4    +      self.DouPer * (1 + self.sintyou * 0.005) + self.KubiScl * 0.5 + self.HeadY * 0.5
        num2   =    55 * self.RegFat           + 50              * self.sintyou * 0.5  + 50 * self.DouPer * 0.4
        num3   =    55 * self.RegMeet          + 50              * self.sintyou * 0.5  + 50 * self.DouPer * 0.4
        num4   =    10 * self.UdeScl   * 0.1                                                             
        num5   =     5 * self.ArmL             +  5              * self.sintyou * 1    +  5 * self.UdeScl * 0.5
        num6   =    70 * self.Hara             + 50              * self.sintyou * 0.7  + 50 * self.Hara   * self.west * 0.005
        num7   =    10 * self.MuneL    * 2                                                                           
        num8   =  num7 * self.MuneTare * 0.005                                                                       
        num9   =    20 * self.west     * 0.5   + 15 * self.west  * self.sintyou * 0.02 + 15 * self.DouPer * self.west * 0.01
        num10  =    10 * self.koshi            +  7 * self.koshi * self.sintyou * 0.04
        num11  =     4 * self.kata                        
        num13  =    70                         +      self.MuneL                * 0.31 +                    self.west * 0.02      
        
        num13 -=     5 * (self.MuneS / 100)                
        num12  = 38000 + num2 + num3 + num4 + num5 + num6 + num7 + num8 + num9 + num10 + num11
        
        self.private_height = num   /   10
        self.private_weight = num12 / 1000
        self.private_bust   = num13
        self.private_waist  = 40 + self.west  * 0.25 + self.Hara   * 0.35
        self.private_hip    = 65 + self.koshi * 0.3  + self.RegFat * 0.025 + self.RegMeet * 0.025
             
        if   num13 <   80:
            self.private_cup = "A"
        elif num13 >= 110:
            self.private_cup = "N"
        else:
            cup_sizes = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
            self.private_cup = cup_sizes[int((num13 - 80) / 2.5)]

        self.private_height = int(self.private_height) * 0.01 / context.scene.unit_settings.scale_length
        self.private_weight = int(self.private_weight)        / context.scene.unit_settings.scale_length ** 3
        self.private_bust   = int(self.private_bust  ) * 0.01 / context.scene.unit_settings.scale_length
        self.private_waist  = int(self.private_waist ) * 0.01 / context.scene.unit_settings.scale_length
        self.private_hip    = int(self.private_hip   ) * 0.01 / context.scene.unit_settings.scale_length
        self.private_cup = "'" + self.private_cup + "'"

        return None

    def __calcMune(self, context):
        if self.BreastSize >= 0:
            self.MuneL = self.BreastSize
            self.MuneS = 0
        else:
            self.MuneL = 0
            self.MuneS = (self.BreastSize / -30) * 100
        self.__calcMuneTare(context)
        return None

    def __calcMuneTare(self, context):
        if self.MuneTare > self.MuneL:
            self.MuneTare = self.MuneL
        else:
            self.__calcMeasurements(context)

    HeadX     : bpy.props.FloatProperty(name="HeadX"     , description="Size of face (left to right)", default=  50, min=   0, max= 100, step=100, precision=0)
    HeadY     : bpy.props.FloatProperty(name="HeadY"     , description="Size of face (up and down)"  , default=  50, min=   0, max= 100, step=100, precision=0, update=__calcMeasurements)
    DouPer    : bpy.props.FloatProperty(name="DouPer"    , description="Leg length"                  , default=  50, min=-100, max= 500, step=100, precision=0, update=__calcMeasurements)
    sintyou   : bpy.props.FloatProperty(name="sintyou"   , description="Height"                      , default=  50, min=-300, max= 100, step=100, precision=0, update=__calcMeasurements)
    BreastSize: bpy.props.FloatProperty(name="BreastSize", description="Breast size"                 , default=  50, min= -30, max= 195, step=100, precision=0, update=__calcMune        )
    MuneTare  : bpy.props.FloatProperty(name="MuneTare"  , description="Breast sagging level"        , default=  50, min=   0, max= 195, step=100, precision=0, update=__calcMuneTare    )
    MuneUpDown: bpy.props.FloatProperty(name="MuneUpDown", description="Position of the nipple"      , default=  10, min= -50, max= 300, step=100, precision=0)
    MuneYori  : bpy.props.FloatProperty(name="MuneYori"  , description="Direction of breast"         , default=  40, min= -50, max= 200, step=100, precision=0)
    west      : bpy.props.FloatProperty(name="west"      , description="Waist"                       , default=  50, min= -30, max= 100, step=100, precision=0, update=__calcMeasurements)
    Hara      : bpy.props.FloatProperty(name="Hara"      , description="Belly"                       , default=  20, min=   0, max= 200, step=100, precision=0, update=__calcMeasurements)
    kata      : bpy.props.FloatProperty(name="kata"      , description="Shoulder width"              , default=  50, min=-400, max= 100, step=100, precision=0, update=__calcMeasurements)
    ArmL      : bpy.props.FloatProperty(name="ArmL"      , description="Size of arms"                , default=  20, min=   0, max= 100, step=100, precision=0, update=__calcMeasurements)
    UdeScl    : bpy.props.FloatProperty(name="UdeScl"    , description="Length of arms"              , default=  50, min=   0, max= 100, step=100, precision=0, update=__calcMeasurements)
    KubiScl   : bpy.props.FloatProperty(name="KubiScl"   , description="Length of neck"              , default=  50, min=   0, max= 200, step=100, precision=0, update=__calcMeasurements)
    koshi     : bpy.props.FloatProperty(name="koshi"     , description="Hip"                         , default=  50, min=-160, max= 200, step=100, precision=0, update=__calcMeasurements)
    RegFat    : bpy.props.FloatProperty(name="RegFat"    , description="Leg thickness"               , default=  40, min=   0, max= 100, step=100, precision=0, update=__calcMeasurements)
    RegMeet   : bpy.props.FloatProperty(name="RegMeet"   , description="Leg definition"              , default=  40, min=   0, max= 100, step=100, precision=0, update=__calcMeasurements)
    MuneL     : bpy.props.FloatProperty(name="MuneL"     , description="munel shapekey value"        , default=  50, min=   0)
    MuneS     : bpy.props.FloatProperty(name="MuneS"     , description="munes shapekey value"        , default=   0, min=   0)

    def __measurementSetter(self, value):
        self.__calcMeasurements(bpy.context)
        return None
    
    def __newGetter(attr, recalc=False):
        def __getter(self):
            if recalc:
                self.__calcMeasurements(bpy.context)
            return getattr(self, attr)
        return __getter

    private_height : bpy.props.FloatProperty (name="private_height", options={'HIDDEN'})
    private_weight : bpy.props.FloatProperty (name="private_weight", options={'HIDDEN'})
    private_bust   : bpy.props.FloatProperty (name="private_bust"  , options={'HIDDEN'})
    private_waist  : bpy.props.FloatProperty (name="private_waist" , options={'HIDDEN'})
    private_hip    : bpy.props.FloatProperty (name="private_hip"   , options={'HIDDEN'})
    private_cup    : bpy.props.StringProperty(name="private_cup"   , options={'HIDDEN'})
                                                     
    height  : bpy.props.FloatProperty (name="height", precision=3, unit='LENGTH', set=__measurementSetter, get=__newGetter('private_height', recalc=True))
    weight  : bpy.props.FloatProperty (name="weight", precision=3, unit='MASS'  , set=__measurementSetter, get=__newGetter('private_weight'))
    bust    : bpy.props.FloatProperty (name="bust"  , precision=3, unit='LENGTH', set=__measurementSetter, get=__newGetter('private_bust'  ))
    waist   : bpy.props.FloatProperty (name="waist" , precision=3, unit='LENGTH', set=__measurementSetter, get=__newGetter('private_waist' ))
    hip     : bpy.props.FloatProperty (name="hip"   , precision=3, unit='LENGTH', set=__measurementSetter, get=__newGetter('private_hip'   ))
    cup     : bpy.props.StringProperty(name="cup"   ,                             set=__measurementSetter, get=__newGetter('private_cup'   ))
                                                     
    def GetArmature(self, override=None):
        override = override or bpy.context.copy()
        ob = self.id_data
        override.update({
            'selected_objects'         : {ob},
            'selected_editable_objects': {ob},
            'editable_bones'           : {}  ,
            'selected_bones'           : {}  ,
            'selected_editable_bones'  : {}  ,
            'active_object'            : ob  ,
            'edit_object'              : ob  ,
        })
        return self.id_data, override

        #armature = override['object']
        #if not armature or armature.type != 'ARMATURE':
        #    print("ERROR: Active object is not an armature")
        #    return None, None
        #
        #for area in bpy.context.screen.areas:
        #    #print(area,area.type)
        #    if area.type == 'OUTLINER':
        #        override.update({
        #            'blend_data': None,
        #            'area': area,
        #            'scene': bpy.context.scene,
        #            'screen': None,
        #            'space_data': area.spaces[0],
        #            'window': None,
        #            'window_manager': None,
        #            'object': armature,
        #            'active_object': armature,
        #            'edit_object': armature,
        #        })
        #        break
        #
        #if override['area'].type != 'OUTLINER':
        #    print("ERROR: There is no 3D View Present in the current workspace")
        #    return None, None
        #
        #if False:
        #    print("\n")
        #    for k,v in override.items():
        #        print(k)
        #    print("\n")
        #return armature, override

    def GetPoseBone(self, boneName, flip=False, override=None):
        context = bpy.context
        
        side = "R" if flip else "L"
        armature, override = self.GetArmature()
        if not armature:
            return
        
        poseBoneList = armature.pose.bones
        poseBone = poseBoneList.get(boneName.replace("?",side)) or poseBoneList.get(boneName.replace("?","*")+"."+side)

        # check if _SCL_ bone needs to be created
        if not poseBone and "_SCL_" in boneName:
            boneList = armature.data.edit_bones
            bpy.ops.object.mode_set(mode='EDIT')
            print("Make Scale Bone: "+boneName)
            copyBone = boneList.get(boneName.replace("_SCL_","").replace("?",side)) or boneList.get(boneName.replace("_SCL_","").replace("?","*")+"."+side)
            if copyBone:
                #bpy.ops.armature.select_all(override, action='DESELECT')
                #for v in context.selected_bones:
                #    v.select = False
                #    v.select_head = False
                #    v.select_tail = False
                #copyBone.select = True
                #copyBone.select_head = True
                #copyBone.select_tail = True
                #boneList.active = copyBone
                #bpy.ops.armature.duplicate(override)
                new_name = copyBone.basename+"_SCL_" + ("."+side if ("."+side) in copyBone.name else "")
                bone = armature.data.edit_bones.new(new_name)
                bone.parent = copyBone
                bone.head = copyBone.head
                bone.tail = copyBone.tail
                bone.roll = copyBone.roll
                bone.show_wire = True
                bone.use_deform = True
                copyBone["UnknownFlag"] = False
                bone["UnknownFlag"] = False
                
                # rename vertex groups
                for child in armature.children:
                    if child.type == 'MESH':
                        vertexGroup = child.vertex_groups.get(copyBone.name)
                        if vertexGroup:
                            vertexGroup.name = bone.name
        
        bpy.ops.object.mode_set(mode='POSE')
        poseBone = poseBone or poseBoneList.get(boneName.replace("?", side)) or poseBoneList.get(boneName.replace("?","*")+"."+side)
        
        if not poseBone:
            print("WARNING: Could not find bone \""+boneName+"\"")
            return

        return poseBone

    def GetDrivers(self, data_path, prop):
        id_data = self.id_data
        drivers = [None, None, None]
        if id_data and id_data.animation_data:
            for f in id_data.animation_data.drivers:
                fName = f.data_path
                #print("check",fName, "for", '["%s"].%s' % (data_path, prop))
                if '["{path}"].{attr}'.format(path=data_path, attr=prop) in fName:
                    #print("VALID!")
                    drivers[f.array_index] = f.driver
        return drivers


    def AddPositionDriver(self, prop, bone, drivers, axis, value, default=50):
        value = value-1
        if value == 0:
            return
        
        driver = drivers[axis] or bone.driver_add("location", axis).driver
        prefix = " + "
        
        # if just created
        if not driver.use_self:
            driver.type = 'SCRIPTED'
            driver.use_self = True
            if axis == 1: # if y axis, include parent bone's length, because head coords are based on parent's tail
                driver.expression = "(self.parent.bone.length+self.bone.head[%d])_" % axis
            else:
                driver.expression = "self.bone.head[%d]_" % axis
            prefix = " * ("
        
        # if prop isn't already a factor
        if not prop in driver.expression:
            driver.expression = driver.expression[:-1] + prefix + ("(self.id_data.cm3d2_bone_morph.%s-%g)*%g)" % (prop, default, value/(100-default) ))
            
        return

    def AddScaleDriver(self, prop, bone, drivers, axis, value, default=50):
        value = value-1
        if value == 0:
            return
        
        driver = drivers[axis] or bone.driver_add("scale", axis).driver
        
        # if just created
        if not driver.use_self:
            driver.type = 'SCRIPTED'
            driver.use_self = True
            driver.expression = "(1)"
        
        # if prop isn't already a factor
        if not prop in driver.expression:
            driver.expression = driver.expression[:-1] + (" + (self.id_data.cm3d2_bone_morph.%s-%g)*%g)" % (prop, default, value/(100-default) ))
                
        return

    def SetPosition(self, prop, boneName, x, y, z, default=50):
        # Check if object has this property
        #if not bpy.context.object.get(prop) or ONLY_FIX_SETTINGS:
        #    if ONLY_FIX_SETTINGS:
        #        return
        #x = (1-x)+1
        #y = (1-y)+1
        #z = (1-z)+1

        #loc.x, loc.y, loc.z = loc.z, -loc.x, loc.y
        x, y, z = z, x, y
            
        bone = self.GetPoseBone(boneName)
        if bone:
            bone.bone.use_local_location = False
            drivers = self.GetDrivers(bone.name,'location')
            
            self.AddPositionDriver(prop, bone, drivers, 0, x, default=default)
            self.AddPositionDriver(prop, bone, drivers, 1, y, default=default)
            self.AddPositionDriver(prop, bone, drivers, 2, z, default=default)
        
        # repeat for left side
        if '?' in boneName:
            bone = self.GetPoseBone(boneName, flip=True)
            if bone:
                bone.bone.use_local_location = False
                drivers = self.GetDrivers(bone.name,'location')
                
                self.AddPositionDriver(prop, bone, drivers, 0, x, default=default)
                self.AddPositionDriver(prop, bone, drivers, 1, y, default=default)
                self.AddPositionDriver(prop, bone, drivers, 2, (1-z)+1, default=default) # mirror z axis
        
        return

    def SetScale(self, prop, boneName, x, y, z, default=50):
        # Check if object has this property
        #if not bpy.context.object.get(prop) or ONLY_FIX_SETTINGS:
        #    if ONLY_FIX_SETTINGS:
        #        return

        x, y, z = z, abs(-x), y
        
        bone = self.GetPoseBone(boneName)
        if bone:
            drivers = self.GetDrivers(bone.name,'scale')
            
            self.AddScaleDriver(prop, bone, drivers, 0, x, default=default)
            self.AddScaleDriver(prop, bone, drivers, 1, y, default=default)
            self.AddScaleDriver(prop, bone, drivers, 2, z, default=default)
        
        # repeat for left side
        if '?' in boneName:
            bone = self.GetPoseBone(boneName, flip=True)
            if bone:
                drivers = self.GetDrivers(bone.name,'scale')
                
                self.AddScaleDriver(prop, bone, drivers, 0, x, default=default)
                self.AddScaleDriver(prop, bone, drivers, 1, y, default=default)
                self.AddScaleDriver(prop, bone, drivers, 2, z, default=default)
        
        return


@compat.BlRegister()
class CNV_PG_cm3d2_wide_slider(bpy.types.PropertyGroup):
    bl_idname = 'CNV_PG_cm3d2_wide_slider'

    HIPPOS    : bpy.props.FloatVectorProperty(name="HIPPOS"    , description="Hips Position"         , default=(0,0,0), min=-100, max= 200, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    THIPOS    : bpy.props.FloatVectorProperty(name="THIPOS"    , description="Legs Position"         , default=(0,0,0), min=-100, max= 200, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    MTWPOS    : bpy.props.FloatVectorProperty(name="MTWPOS"    , description="Thigh Position"        , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    MMNPOS    : bpy.props.FloatVectorProperty(name="MMNPOS"    , description="Rear Thigh Position"   , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    THI2POS   : bpy.props.FloatVectorProperty(name="THI2POS"   , description="Knee Position"         , default=(0,0,0), min=-100, max= 200, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    SKTPOS    : bpy.props.FloatVectorProperty(name="SKTPOS"    , description="Skirt Position"        , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    SPIPOS    : bpy.props.FloatVectorProperty(name="SPIPOS"    , description="Lower Abdomen Position", default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    S0APOS    : bpy.props.FloatVectorProperty(name="S0APOS"    , description="Upper Abdomen Position", default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    S1POS     : bpy.props.FloatVectorProperty(name="S1POS"     , description="Lower Chest Position"  , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    S1APOS    : bpy.props.FloatVectorProperty(name="S1APOS"    , description="Upper Chest Position"  , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    MUNEPOS   : bpy.props.FloatVectorProperty(name="MUNEPOS"   , description="Breasts Position"      , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    MUNESUBPOS: bpy.props.FloatVectorProperty(name="MUNESUBPOS", description="Breasts Sub-Position"  , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    NECKPOS   : bpy.props.FloatVectorProperty(name="NECKPOS"   , description="Neck Position"         , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
    CLVPOS    : bpy.props.FloatVectorProperty(name="CLVPOS"    , description="Clavicle Position"     , default=(0,0,0), min=-1.0, max= 1.0, precision=2, subtype=compat.subtype('XYZ'        ), unit='NONE')
                                                                                                
    PELSCL    : bpy.props.FloatVectorProperty(name="PELSCL"    , description="Pelvis Scale"          , default=(1,1,1), min= 0.1, max= 2.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    HIPSCL    : bpy.props.FloatVectorProperty(name="HIPSCL"    , description="Hips Scale"            , default=(1,1,1), min= 0.1, max= 2.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    THISCL    : bpy.props.FloatVectorProperty(name="THISCL"    , description="Legs Scale"            , default=(1,1,1), min= 0.1, max= 2.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    MTWSCL    : bpy.props.FloatVectorProperty(name="MTWSCL"    , description="Thigh Scale"           , default=(1,1,1), min= 0.1, max= 2.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    MMNSCL    : bpy.props.FloatVectorProperty(name="MMNSCL"    , description="Rear Thigh Scale"      , default=(1,1,1), min= 0.1, max= 2.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    THISCL2   : bpy.props.FloatVectorProperty(name="THISCL2"   , description="Knee Scale"            , default=(1,1,1), min= 0.1, max= 2.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    CALFSCL   : bpy.props.FloatVectorProperty(name="CALFSCL"   , description="Calf Scale"            , default=(1,1,1), min= 0.1, max= 2.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    FOOTSCL   : bpy.props.FloatVectorProperty(name="FOOTSCL"   , description="Foot Scale"            , default=(1,1,1), min= 0.1, max= 2.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    SKTSCL    : bpy.props.FloatVectorProperty(name="SKTSCL"    , description="Skirt Scale"           , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    SPISCL    : bpy.props.FloatVectorProperty(name="SPISCL"    , description="Lower Abdomen Scale"   , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    S0ASCL    : bpy.props.FloatVectorProperty(name="S0ASCL"    , description="Upper Abdomen Scale"   , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    S1_SCL    : bpy.props.FloatVectorProperty(name="S1_SCL"    , description="Lower Chest Scale"     , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    S1ASCL    : bpy.props.FloatVectorProperty(name="S1ASCL"    , description="Upper Chest Scale"     , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    S1ABASESCL: bpy.props.FloatVectorProperty(name="S1ABASESCL", description="Upper Torso Scale"     , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    MUNESCL   : bpy.props.FloatVectorProperty(name="MUNESCL"   , description="Breasts Scale"         , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    MUNESUBSCL: bpy.props.FloatVectorProperty(name="MUNESUBSCL", description="Breasts Sub-Scale"     , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    NECKSCL   : bpy.props.FloatVectorProperty(name="NECKSCL"   , description="Neck Scale"            , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    CLVSCL    : bpy.props.FloatVectorProperty(name="CLVSCL"    , description="Clavicle Scale"        , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    KATASCL   : bpy.props.FloatVectorProperty(name="KATASCL"   , description="Shoulders Scale"       , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    UPARMSCL  : bpy.props.FloatVectorProperty(name="UPARMSCL"  , description="Upper Arm Scale"       , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    FARMSCL   : bpy.props.FloatVectorProperty(name="FARMSCL"   , description="Forearm Scale"         , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
    HANDSCL   : bpy.props.FloatVectorProperty(name="HANDSCL"   , description="Hand Scale"            , default=(1,1,1), min= 0.1, max= 3.0, precision=2, subtype=compat.subtype('XYZ_LENGTH' ), unit='NONE')
                                                                                                                                        
                                                                                                                                        
    def GetArmature(self, override=None):
        return CNV_PG_cm3d2_bone_morph.GetArmature(self, override=override)
    
    def GetPoseBone(self, boneName, flip=False, override=None):
        return CNV_PG_cm3d2_bone_morph.GetPoseBone(self, boneName, flip=flip, override=override)

    def GetDrivers(self, data_path, prop):
        return CNV_PG_cm3d2_bone_morph.GetDrivers(self, data_path, prop)


    def AddPositionDriver(self, prop, index, bone, drivers, axis, value):
        if value == 0:
            return
              
        driver = drivers[axis] or bone.driver_add("location",axis).driver
              
        # if just created
        if not driver.use_self:
            driver.type = 'SCRIPTED'
            driver.use_self = True
            driver.expression = "0"
              
        # if prop isn't already a factor
        if not prop in driver.expression:
            driver.expression = driver.expression + (" + self.id_data.cm3d2_wide_slider.%s[%d]*%g" % (prop,index,value))
                
        return
              
              
    def AddScaleDriver(self, prop, index, bone, drivers, axis):
        if index < 0:
            return
              
        driver = drivers[axis] or bone.driver_add("scale",axis).driver
              
        # if just created
        if not driver.use_self:
            driver.type = 'SCRIPTED'
            driver.use_self = True
            driver.expression = "1"
              
        # if prop isn't already a factor
        if not prop in driver.expression:
            driver.expression = driver.expression + (" * self.id_data.cm3d2_wide_slider.%s[%d]" % (prop,index))
                
        return
              
                      
    def AddVectorProperty(self, object, prop, value=None, default=0.0, min=-100, max=200):
        #value = value or [default, default, default]
        #object[prop] = not RESET_SETTINGS and object.get(prop) or value
        #object['_RNA_UI'][prop] = {
        #    "description": "",
        #    "default": default,
        #    "min": min,
        #    "max": max,
        #    "soft_min": min,
        #    "soft_max": max,
        #}     
        return
    
              
    def SetPosition(self, prop, boneName, ux, uy, uz, axisOrder=[0,1,2], axisFlip=None):
        # Check if object has this property
        #if not bpy.context.object.get(prop) or ONLY_FIX_SETTINGS:
        #    self.AddVectorProperty(bpy.context.object, prop)
        #    if ONLY_FIX_SETTINGS:
        #        return

        ux, uy, uz = uz*5, ux*5, -uy*5
        #axisFlip = axisOrder[axisFlip] if axisFlip else None
        axisFlip = 2 if axisFlip == 0 else  0 if axisFlip == 1 else  1 if axisFlip == 2 else  None
        #axisFlip = axisOrder[axisFlip] if axisFlip else None
        axisOrder[0], axisOrder[1], axisOrder[2] = axisOrder[2], axisOrder[0], axisOrder[1]
        axisFlip = axisOrder[axisFlip] if axisFlip != None else None
        
        bone = self.GetPoseBone(boneName)
        if bone:
            bone.bone.use_local_location = False
            drivers = self.GetDrivers(bone.name,'location')
        
            self.AddPositionDriver(prop, axisOrder[0], bone, drivers, 0, -ux)
            self.AddPositionDriver(prop, axisOrder[1], bone, drivers, 1, -uy)
            self.AddPositionDriver(prop, axisOrder[2], bone, drivers, 2, -uz)
        
        # repeat for left side
        if '?' in boneName:
            bone = self.GetPoseBone(boneName, flip=True)
            if bone:
                bone.bone.use_local_location = False
                drivers = self.GetDrivers(bone.name,'location')
                
                if   axisFlip == 0:
                    ux = -ux
                elif axisFlip == 1:
                    uy = -uy
                elif axisFlip == 2:
                    uz = -uz
                
                self.AddPositionDriver(prop, axisOrder[0], bone, drivers, 0, -ux)
                self.AddPositionDriver(prop, axisOrder[1], bone, drivers, 1, -uy)
                self.AddPositionDriver(prop, axisOrder[2], bone, drivers, 2, -uz)
        
        return


    def SetScale(self, prop, boneName, axisOrder=[0,1,2]):
        # Check if object has this property
        #if not bpy.context.object.get(prop) or ONLY_FIX_SETTINGS:
        #    self.AddVectorProperty(bpy.context.object, prop, default=1.0, min=0.1, max=3.0)
        #    if ONLY_FIX_SETTINGS:
        #        return

        # x, y, z = x, z, y
        axisOrder[0], axisOrder[1], axisOrder[2] = axisOrder[0], axisOrder[2], axisOrder[1]
        
        bone = self.GetPoseBone(boneName)
        if bone:
            drivers = self.GetDrivers(bone.name,'scale')
            
            self.AddScaleDriver(prop, axisOrder[0], bone, drivers, 0)
            self.AddScaleDriver(prop, axisOrder[1], bone, drivers, 1)
            self.AddScaleDriver(prop, axisOrder[2], bone, drivers, 2)
        
        # repeat for left side
        if '?' in boneName:
            bone = self.GetPoseBone(boneName, True)
            if bone:
                drivers = self.GetDrivers(bone.name,'scale')

                self.AddScaleDriver(prop, axisOrder[0], bone, drivers, 0)
                self.AddScaleDriver(prop, axisOrder[1], bone, drivers, 1)
                self.AddScaleDriver(prop, axisOrder[2], bone, drivers, 2)
        
        return


@compat.BlRegister()
class CNV_OT_add_cm3d2_body_sliders(bpy.types.Operator):
    bl_idname      = 'object.add_cm3d2_body_sliders'
    bl_label       = "Add CM3D2 Body Sliders"
    bl_description = "Adds drivers to armature to enable body sliders."
    bl_options     = {'REGISTER', 'UNDO'}

    is_fix_thigh       : bpy.props.BoolProperty(name="Fix Thigh"       , default=True, description="Fix twist bone values for the thighs in motor-cycle pose")
    is_drive_shape_keys: bpy.props.BoolProperty(name="Drive Shape Keys", default=True, description="Connect sliders to mesh children's shape keys"           )
    

    @classmethod
    def poll(cls, context):
        if context.area.type == 'PROPERTIES':
            ob = context.object
            arm = ob.data
        else:
            ob = context.active_object
            arm = ob.data
        has_arm  = arm and isinstance(arm, bpy.types.Armature) and ("Bip01" in arm.bones)
        can_edit = (ob and ob.data == arm) or (arm and arm.is_editmode)
        return has_arm and can_edit

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, 'is_fix_thigh'       )
        self.layout.prop(self, 'is_drive_shape_keys')

    def driveShapeKey(self, shapekey, data, prop, expression, set_min=None, set_max=None):
        if not shapekey:
            return
        driver = shapekey.driver_add('value').driver
        driver.type = 'SCRIPTED'

        driver_var = driver.variables.new() if len(driver.variables) < 1 else driver.variables[0]
        driver_var.type = 'SINGLE_PROP'
        driver_var.name = prop

        driver_target = driver_var.targets[0]
        driver_target.id_type = 'OBJECT'
        driver_target.id = data.id_data
        driver_target.data_path = data.path_from_id(prop)

        driver.expression = expression

        if set_min:
            shapekey.slider_min = set_min
        if set_max:
            shapekey.slider_max = set_max

    def driveTwistBone(self, bone, prop='rotation_euler', axis=0, expression=""):
        if not bone:
            return
        driver = bone.driver_add(prop, axis).driver
        driver.type = 'SCRIPTED'
        driver.use_self = True

        driver.expression = expression

    def execute(self, context):
        try:
            ob = context.object
        except:
            try:
                ob = context.active_object
            except:
                pass
        arm = ob.data
        pre_mode = ob.mode
        #if pre_mode != 'EDIT':
        #    override = context.copy()
        #    override['active_object'] = ob
        #    bpy.ops.object.mode_set(override, mode='EDIT')

        morph   = ob.cm3d2_bone_morph
        sliders = ob.cm3d2_wide_slider



        #BoneMorph.SetPosition("KubiScl", "Bip01 Neck"        , 0.95, 1   , 1   , 1.05, 1   , 1   )
        #BoneMorph.SetPosition("KubiScl", "Bip01 Head"        , 0.8 , 1   , 1   , 1.2 , 1   , 1   )
        #BoneMorph.SetScale   ("UdeScl" , "Bip01 ? UpperArm"  , 0.85, 1   , 1   , 1.15, 1   , 1   )
        #BoneMorph.SetScale   ("EyeSclX", "Eyepos_L"          , 1   , 1   , 0.92, 1   , 1   , 1.08)
        #BoneMorph.SetScale   ("EyeSclX", "Eyepos_R"          , 1   , 1   , 0.92, 1   , 1   , 1.08)
        #BoneMorph.SetScale   ("EyeSclY", "Eyepos_L"          , 1   , 0.92, 1   , 1   , 1.08, 1   )
        #BoneMorph.SetScale   ("EyeSclY", "Eyepos_R"          , 1   , 0.92, 1   , 1   , 1.08, 1   )
        #BoneMorph.SetPosition("EyePosX", "Eyepos_R"          , 1   , 1   , 0.9 , 1   , 1   , 1.1 )
        #BoneMorph.SetPosition("EyePosX", "Eyepos_L"          , 1   , 1   , 0.9 , 1   , 1   , 1.1 )
        #BoneMorph.SetPosition("EyePosY", "Eyepos_R"          , 1   , 0.93, 1   , 1   , 1.07, 1   )
        #BoneMorph.SetPosition("EyePosY", "Eyepos_L"          , 1   , 0.93, 1   , 1   , 1.07, 1   )
        #BoneMorph.SetScale   ("HeadX"  , "Bip01 Head"        , 1   , 0.9 , 0.8 , 1   , 1.1 , 1.2 )
        #BoneMorph.SetScale   ("HeadY"  , "Bip01 Head"        , 0.8 , 0.9 , 1   , 1.2 , 1.1 , 1   )
        #BoneMorph.SetPosition("DouPer" , "Bip01 Spine"       , 1   , 1   , 0.94, 1   , 1   , 1.06)
        #BoneMorph.SetPosition("DouPer" , "Bip01 Spine0a"     , 0.88, 1   , 1   , 1.12, 1   , 1   )
        #BoneMorph.SetPosition("DouPer" , "Bip01 Spine1"      , 0.88, 1   , 1   , 1.12, 1   , 1   )
        #BoneMorph.SetPosition("DouPer" , "Bip01 Spine1a"     , 0.88, 1   , 1   , 1.12, 1   , 1   )
        #BoneMorph.SetPosition("DouPer" , "Bip01 Neck"        , 1.03, 1   , 1   , 0.97, 1   , 1   )
        #BoneMorph.SetPosition("DouPer" , "Bip01 ? Calf"      , 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetPosition("DouPer" , "Bip01 ? Foot"      , 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetScale   ("DouPer" , "Bip01 ? Thigh_SCL_", 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetScale   ("DouPer" , "momotwist_?"       , 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetScale   ("DouPer" , "Bip01 ? Calf_SCL_" , 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetScale   ("DouPer" , "Bip01 ? UpperArm"  , 0.98, 1   , 1   , 1.02, 1   , 1   )
        #BoneMorph.SetPosition("sintyou", "Bip01 Spine"       , 1   , 1   , 0.85, 1   , 1   , 1.15)
        #BoneMorph.SetPosition("sintyou", "Bip01 Spine0a"     , 0.88, 1   , 1   , 1.12, 1   , 1   )
        #BoneMorph.SetPosition("sintyou", "Bip01 Spine1"      , 0.88, 1   , 1   , 1.12, 1   , 1   )
        #BoneMorph.SetPosition("sintyou", "Bip01 Spine1a"     , 0.88, 1   , 1   , 1.12, 1   , 1   )
        #BoneMorph.SetPosition("sintyou", "Bip01 Neck"        , 0.97, 1   , 1   , 1.03, 1   , 1   )
        #BoneMorph.SetPosition("sintyou", "Bip01 Head"        , 0.9 , 1   , 1   , 1.1 , 1   , 1   )
        #BoneMorph.SetPosition("sintyou", "Bip01 ? Calf"      , 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetPosition("sintyou", "Bip01 ? Foot"      , 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetScale   ("sintyou", "Bip01 ? UpperArm"  , 0.9 , 1   , 1   , 1.1 , 1   , 1   )
        #BoneMorph.SetScale   ("sintyou", "Bip01 ? Thigh_SCL_", 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetScale   ("sintyou", "momotwist_?"       , 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetScale   ("sintyou", "Bip01 ? Calf_SCL_" , 0.87, 1   , 1   , 1.13, 1   , 1   )
        #BoneMorph.SetScale   ("koshi"  , "Bip01 Pelvis_SCL_" , 1   , 0.8 , 0.92, 1   , 1.2 , 1.08)
        #BoneMorph.SetScale   ("koshi"  , "Bip01 Spine_SCL_"  , 1   , 1   , 1   , 1   , 1   , 1   )
        #BoneMorph.SetScale   ("koshi"  , "Hip_?"             , 1   , 0.96, 0.9 , 1   , 1.04, 1.1 )
        #BoneMorph.SetScale   ("koshi"  , "Skirt"             , 1   , 0.85, 0.88, 1   , 1.2 , 1.12)
        #BoneMorph.SetPosition("kata"   , "Bip01 ? Clavicle"  , 0.98, 1   , 0.5 , 1.02, 1   , 1.5 )
        #BoneMorph.SetScale   ("kata"   , "Bip01 Spine1a_SCL_", 1   , 1   , 0.95, 1   , 1   , 1.05)
        #BoneMorph.SetScale   ("west"   , "Bip01 Spine_SCL_"  , 1   , 0.95, 0.9 , 1   , 1.05, 1.1 )
        #BoneMorph.SetScale   ("west"   , "Bip01 Spine0a_SCL_", 1   , 0.85, 0.7 , 1   , 1.15, 1.3 )
        #BoneMorph.SetScale   ("west"   , "Bip01 Spine1_SCL_" , 1   , 0.9 , 0.85, 1   , 1.1 , 1.15)
        #BoneMorph.SetScale   ("west"   , "Bip01 Spine1a_SCL_", 1   , 0.95, 0.95, 1   , 1.05, 1.05)
        #BoneMorph.SetScale   ("west"   , "Skirt"             , 1   , 0.92, 0.88, 1   , 1.08, 1.12)



        morph.SetPosition("KubiScl", "Bip01 Neck"         , 1.05, 1   , 1   )
        morph.SetPosition("KubiScl", "Bip01 Head"         , 1.2 , 1   , 1   )
                                                                      
        morph.SetScale   ("UdeScl" , "Bip01 ? UpperArm"   , 1.15, 1   , 1   )
                                                                      
        morph.SetScale   ("HeadX"  , "Bip01 Head"         , 1   , 1.1 , 1.2 )
        morph.SetScale   ("HeadY"  , "Bip01 Head"         , 1.2 , 1.1 , 1   )
        
        morph.SetPosition("sintyou", "Bip01 Spine"        , 1   , 1   , 1.15)
        morph.SetPosition("sintyou", "Bip01 Spine0a"      , 1.12, 1   , 1   )
        morph.SetPosition("sintyou", "Bip01 Spine1"       , 1.12, 1   , 1   )
        morph.SetPosition("sintyou", "Bip01 Spine1a"      , 1.12, 1   , 1   )
        morph.SetPosition("sintyou", "Bip01 Neck"         , 1.03, 1   , 1   )
        morph.SetPosition("sintyou", "Bip01 Head"         , 1.1 , 1   , 1   )
        morph.SetPosition("sintyou", "Bip01 ? Calf"       , 1.13, 1   , 1   )
        morph.SetPosition("sintyou", "Bip01 ? Foot"       , 1.13, 1   , 1   )
        morph.SetScale   ("sintyou", "Bip01 ? UpperArm"   , 1.1 , 1   , 1   )
        morph.SetScale   ("sintyou", "Bip01 ? Thigh_SCL_" , 1.13, 1   , 1   )
        morph.SetScale   ("sintyou", "momotwist_?"        , 1.13, 1   , 1   )
        morph.SetScale   ("sintyou", "Bip01 ? Calf_SCL_"  , 1.13, 1   , 1   )
                                                                            
        # for DouPer, any bone not a thigh or a decendant of one, it's values are inverted
        morph.SetPosition("DouPer" , "Bip01 Spine"        , 1, 1, (1-1.06)+1)
        morph.SetPosition("DouPer" , "Bip01 Spine0a"      , (1-1.12)+1, 1, 1)
        morph.SetPosition("DouPer" , "Bip01 Spine1"       , (1-1.12)+1, 1, 1)
        morph.SetPosition("DouPer" , "Bip01 Spine1a"      , (1-1.12)+1, 1, 1)
        morph.SetPosition("DouPer" , "Bip01 Neck"         , (1-0.97)+1, 1, 1)
        morph.SetScale   ("DouPer" , "Bip01 ? UpperArm"   , (1-1.02)+1, 1, 1)
        morph.SetPosition("DouPer" , "Bip01 ? Calf"       ,       1.13, 1, 1)
        morph.SetPosition("DouPer" , "Bip01 ? Foot"       ,       1.13, 1, 1)
        morph.SetScale   ("DouPer" , "Bip01 ? Thigh_SCL_" ,       1.13, 1, 1)
        morph.SetScale   ("DouPer" , "momotwist_?"        ,       1.13, 1, 1)
        morph.SetScale   ("DouPer" , "Bip01 ? Calf_SCL_"  ,       1.13, 1, 1)

        # This has some issues            
        morph.SetScale   ("koshi"  , "Bip01 Pelvis_SCL_"  , 1   , 1.2 , 1.08)
        morph.SetScale   ("koshi"  , "Bip01 Spine_SCL_"   , 1   , 1   , 1   )
        morph.SetScale   ("koshi"  , "Hip_?"              , 1   , 1.04, 1.1 )
        morph.SetScale   ("koshi"  , "Skirt"              , 1   , 1.2 , 1.12)
                                     
        #morph.SetPosition("kata"   , "Bip01 ? Clavicle"   , 1.02, 1   , 1.5, default=0)
        morph.SetPosition("kata"   , "Bip01 ? Clavicle"   , 1.02, 1   , 1.5 , default=50)
        morph.SetScale   ("kata"   , "Bip01 Spine1a_SCL_" , 1   , 1   , 1.05, default=50)
                                        
        morph.SetScale   ("west"   , "Bip01 Spine_SCL_"   , 1   , 1.05, 1.1 )
        morph.SetScale   ("west"   , "Bip01 Spine0a_SCL_" , 1   , 1.15, 1.3 )
        morph.SetScale   ("west"   , "Bip01 Spine1_SCL_"  , 1   , 1.1 , 1.15)
        morph.SetScale   ("west"   , "Bip01 Spine1a_SCL_" , 1   , 1.05, 1.05)
        morph.SetScale   ("west"   , "Skirt"              , 1   , 1.08, 1.12)
        
        # WideSlider functions MUST be called AFTER all BoneMorph calls
        sliders.SetPosition("THIPOS"    , "Bip01 ? Thigh"     ,  0    ,  0.001,  0.001, axisFlip=0, axisOrder=[1, 2, 0]) #axisFlip=2 #axisFlip=0
        sliders.SetPosition("THI2POS"   , "Bip01 ? Thigh_SCL_",  0.001,  0.001,  0.001, axisFlip=0, axisOrder=[1, 2, 0]) #axisFlip=2 #axisFlip=0
        sliders.SetPosition("HIPPOS"    , "Hip_?"             ,  0.001,  0.001,  0.001, axisFlip=0, axisOrder=[1, 2, 0]) #axisFlip=2 #axisFlip=0
        sliders.SetPosition("MTWPOS"    , "momotwist_?"       ,  0.1  ,  0.1  , -0.1  , axisFlip=2                     ) #axisFlip=2 #axisFlip=2
        sliders.SetPosition("MMNPOS"    , "momoniku_?"        ,  0.1  , -0.1  ,  0.1  , axisFlip=1                     ) #axisFlip=1 #axisFlip=1
        sliders.SetPosition("SKTPOS"    , "Skirt"             , -0.1  , -0.1  ,  0.1  ,             axisOrder=[2, 1, 0]) #           #          
        sliders.SetPosition("SPIPOS"    , "Bip01 Spine"       , -0.1  ,  0.1  ,  0.1                                   ) #           #          
        sliders.SetPosition("S0APOS"    , "Bip01 Spine0a"     , -0.1  ,  0.1  ,  0.1                                   ) #           #          
        sliders.SetPosition("S1POS"     , "Bip01 Spine1"      , -0.1  ,  0.1  ,  0.1                                   ) #           #          
        sliders.SetPosition("S1APOS"    , "Bip01 Spine1a"     , -0.1  ,  0.1  ,  0.1                                   ) #           #          
        sliders.SetPosition("NECKPOS"   , "Bip01 Neck"        , -0.1  ,  0.1  ,  0.1                                   ) #           #          
        sliders.SetPosition("CLVPOS"    , "Bip01 ? Clavicle"  , -0.1  ,  0.1  , -0.1  , axisFlip=2                     ) #axisFlip=2 #axisFlip=2
        sliders.SetPosition("MUNESUBPOS", "Mune_?_sub"        , -0.1  , -0.1  , -0.1  , axisFlip=2, axisOrder=[1, 2, 0]) #axisFlip=1 #axisFlip=2
        sliders.SetPosition("MUNEPOS"   , "Mune_?"            ,  0.1  , -0.1  , -0.1  , axisFlip=0, axisOrder=[2, 1, 0]) #axisFlip=2 #axisFlip=0
                                                                                                                                     
        sliders.SetScale   ("THISCL",     "Bip01 ? Thigh"     , axisOrder=[0, 1, -1])
        sliders.SetScale   ("MTWSCL",     "momotwist_?"       )
        sliders.SetScale   ("MMNSCL",     "momoniku_?"        )
        sliders.SetScale   ("PELSCL",     "Bip01 Pelvis_SCL_" )
        sliders.SetScale   ("THISCL2",    "Bip01 ? Thigh_SCL_")
        sliders.SetScale   ("CALFSCL",    "Bip01 ? Calf"      )
        sliders.SetScale   ("FOOTSCL",    "Bip01 ? Foot"      )
        sliders.SetScale   ("SKTSCL",     "Skirt"             )
        sliders.SetScale   ("SPISCL",     "Bip01 Spine_SCL_"  )
        sliders.SetScale   ("S0ASCL",     "Bip01 Spine0a_SCL_")
        sliders.SetScale   ("S1_SCL",     "Bip01 Spine1_SCL_" )
        sliders.SetScale   ("S1ASCL",     "Bip01 Spine1a_SCL_")
        sliders.SetScale   ("S1ABASESCL", "Bip01 Spine1a"     )
        sliders.SetScale   ("KATASCL",    "Kata_?"            )
        sliders.SetScale   ("UPARMSCL",   "Bip01 ? UpperArm"  )
        sliders.SetScale   ("FARMSCL",    "Bip01 ? Forearm"   )
        sliders.SetScale   ("HANDSCL",    "Bip01 ? Hand"      )
        sliders.SetScale   ("CLVSCL",     "Bip01 ? Clavicle"  )
        sliders.SetScale   ("MUNESCL",    "Mune_?"            )
        sliders.SetScale   ("MUNESUBSCL", "Mune_?_sub"        )
        sliders.SetScale   ("NECKSCL",    "Bip01 Neck_SCL_"   )
        sliders.SetScale   ("HIPSCL",     "Hip_?"             )
        sliders.SetScale   ("PELSCL",     "Hip_?"             ) # hips are also scaled with pelvis
        
        if self.is_fix_thigh:
            bone = morph.GetPoseBone("momoniku_?")
            bone.rotation_quaternion[0] = 0.997714
            bone.rotation_quaternion[3] = -0.06758
            bone = morph.GetPoseBone("momoniku_?", flip=True)
            bone.rotation_quaternion[0] = 0.997714
            bone.rotation_quaternion[3] = 0.06758
            
        if self.is_drive_shape_keys:
            for child in ob.children:
                if child.type == 'MESH':
                    sks = child.data.shape_keys.key_blocks
                    self.driveShapeKey(sks.get('arml'    ), morph, 'ArmL'    , "ArmL     * 0.01")
                    self.driveShapeKey(sks.get('hara'    ), morph, 'Hara'    , "Hara     * 0.01")
                    self.driveShapeKey(sks.get('munel'   ), morph, 'MuneL'   , "MuneL    * 0.01", set_max=2)
                    self.driveShapeKey(sks.get('munes'   ), morph, 'MuneS'   , "MuneS    * 0.01")
                    self.driveShapeKey(sks.get('munetare'), morph, 'MuneTare', "MuneTare * 0.01", set_max=2)
                    self.driveShapeKey(sks.get('regfat'  ), morph, 'RegFat'  , "RegFat   * 0.01")
                    self.driveShapeKey(sks.get('regmeet' ), morph, 'RegMeet' , "RegMeet  * 0.01")

        if True:
            bones = ob.pose.bones
            Mune_L = bones.get('Mune_L') or bones.get('Mune_*.L')
            Mune_R = bones.get('Mune_R') or bones.get('Mune_*.R')
            if Mune_L:
                Mune_L.rotation_mode = 'XYZ'
            if Mune_R:                  
                Mune_R.rotation_mode = 'XYZ'
            
            self.driveTwistBone(Mune_R, axis=0, expression="-(self.id_data.cm3d2_bone_morph.MuneUpDown-50) * self.id_data.cm3d2_bone_morph.MuneL * (pi/180) * 0.00060")
            self.driveTwistBone(Mune_L, axis=0, expression="+(self.id_data.cm3d2_bone_morph.MuneUpDown-50) * self.id_data.cm3d2_bone_morph.MuneL * (pi/180) * 0.00060")
            self.driveTwistBone(Mune_R, axis=2, expression="-(self.id_data.cm3d2_bone_morph.MuneYori  -50) * self.id_data.cm3d2_bone_morph.MuneL * (pi/180) * 0.00025")
            self.driveTwistBone(Mune_L, axis=2, expression="-(self.id_data.cm3d2_bone_morph.MuneYori  -50) * self.id_data.cm3d2_bone_morph.MuneL * (pi/180) * 0.00025")



        

        bpy.ops.object.mode_set(mode=pre_mode)
        
        return {'FINISHED'}



@compat.BlRegister()
class OBJECT_PT_cm3d2_sliders(bpy.types.Panel):
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = 'object'
    bl_label       = 'CM3D2 Sliders'
    bl_idname      = 'OBJECT_PT_cm3d2_sliders'

    @classmethod
    def poll(cls, context):
        if context.area.type == 'PROPERTIES':
            ob = context.object
            arm = ob.data
        else:
            ob = context.active_object
            arm = ob.data
        return arm and isinstance(arm, bpy.types.Armature) and ("Bip01" in arm.bones)

    def draw(self, context):
        if context.area.type == 'PROPERTIES':
            ob = context.object
            arm = ob.data
        else:
            ob = context.active_object
            arm = ob.data

        morph = ob.cm3d2_bone_morph
        flow = self.layout.grid_flow(row_major=True, columns=2, even_columns=False, even_rows=False, align=True)
        flow.use_property_split    = True
        flow.use_property_decorate = False
        flow.prop(morph, 'height', text="Height", emboss=False)
        flow.prop(morph, 'weight', text="Weight", emboss=False)
        flow.prop(morph, 'bust'  , text="Bust"  , emboss=False)
        flow.prop(morph, 'cup'   , text="Cup"   , emboss=False)
        flow.prop(morph, 'waist' , text="Waist" , emboss=False)
        flow.prop(morph, 'hip'   , text="Hip"   , emboss=False)
                                
        row = self.layout.row()
        row.enabled = bpy.ops.object.add_cm3d2_body_sliders.poll(context.copy())
        op = row.operator("object.add_cm3d2_body_sliders", text="Connect Sliders", icon=compat.icon('CONSTRAINT_BONE'))


@compat.BlRegister()
class OBJECT_PT_cm3d2_body_sliders(bpy.types.Panel):
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = 'object'
    bl_label       = 'Body Sliders'
    bl_idname      = 'OBJECT_PT_cm3d2_body_sliders'
    bl_parent_id   = 'OBJECT_PT_cm3d2_sliders'
    bl_options     = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and True

    def draw(self, context):
        morph = context.object.cm3d2_bone_morph

        self.layout.use_property_split = True

        flow = self.layout.grid_flow(row_major=False, columns=0, even_columns=False, even_rows=False, align=False)
        col = flow.column(align=True); col.prop(morph, 'HeadX'     , text="Face Width"  , slider=True)
        pass;                          col.prop(morph, 'HeadY'     , text="Face Height" , slider=True)
        col = flow.column(align=True); col.prop(morph, 'DouPer'    , text="Leg Length"  , slider=True)
        pass;                          col.prop(morph, 'sintyou'   , text="Height"      , slider=True)
        col = flow.column(align=True); col.prop(morph, 'BreastSize', text="Breast Size" , slider=True)
        pass;                          col.prop(morph, 'MuneTare'  , text="Breast Sag"  , slider=True)
        pass;                          col.prop(morph, 'MuneUpDown', text="Breast Pitch", slider=True)
        pass;                          col.prop(morph, 'MuneYori'  , text="Breast Yaw"  , slider=True)
        col = flow.column(align=True); col.prop(morph, 'west'      , text="Waist"       , slider=True)
        pass;                          col.prop(morph, 'Hara'      , text="Belly"       , slider=True)
        pass;                          col.prop(morph, 'kata'      , text="Shoulders"   , slider=True)
        pass;                          col.prop(morph, 'ArmL'      , text="Arm Size"    , slider=True)
        pass;                          col.prop(morph, 'UdeScl'    , text="Arm Length"  , slider=True)
        pass;                          col.prop(morph, 'KubiScl'   , text="Neck Length" , slider=True)
        col = flow.column(align=True); col.prop(morph, 'koshi'     , text="Hip"         , slider=True)
        pass;                          col.prop(morph, 'RegFat'    , text="Leg Fat"     , slider=True)
        pass;                          col.prop(morph, 'RegMeet'   , text="Leg Meat"    , slider=True)
                                       

@compat.BlRegister()
class OBJECT_PT_cm3d2_wide_sliders(bpy.types.Panel):
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = 'object'
    bl_label       = 'Wide Sliders'
    bl_idname      = 'OBJECT_PT_cm3d2_wide_sliders'
    bl_parent_id   = 'OBJECT_PT_cm3d2_sliders'
    bl_options     = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and True

    def draw(self, context):
        sliders = context.object.cm3d2_wide_slider
        
        self.layout.use_property_split = True

        flow = self.layout.grid_flow(row_major=False, columns=0, even_columns=False, even_rows=False, align=False)
        #col = flow
        col = flow.column();           col.prop(sliders, "PELSCL"    , text="Pelvis Scale"            , slider=True)
        col = flow.column(align=True); col.prop(sliders, "HIPPOS"    , text="Hips Position"           , slider=True)
        pass;                          col.prop(sliders, "HIPSCL"    , text="Hips Scale"              , slider=True)
        col = flow.column(align=True); col.prop(sliders, "THIPOS"    , text="Legs Position"           , slider=True)
        pass;                          col.prop(sliders, "THISCL"    , text="Legs Scale"              , slider=True)
        col = flow.column(align=True); col.prop(sliders, "MTWPOS"    , text="Thigh Position"          , slider=True)
        pass;                          col.prop(sliders, "MTWSCL"    , text="Thigh Scale"             , slider=True)
        col = flow.column(align=True); col.prop(sliders, "MMNPOS"    , text="Rear Thigh Position"     , slider=True)
        pass;                          col.prop(sliders, "MMNSCL"    , text="Rear Thigh Scale"        , slider=True)
        col = flow.column(align=True); col.prop(sliders, "THI2POS"   , text="Knee Position"           , slider=True)
        pass;                          col.prop(sliders, "THISCL2"   , text="Knee Scale"              , slider=True)
        col = flow.column();           col.prop(sliders, "CALFSCL"   , text="Calf Scale"              , slider=True)
        col = flow.column();           col.prop(sliders, "FOOTSCL"   , text="Foot Scale"              , slider=True)
        col = flow.column(align=True); col.prop(sliders, "SKTPOS"    , text="Skirt Position"          , slider=True)
        pass;                          col.prop(sliders, "SKTSCL"    , text="Skirt Scale"             , slider=True)
        col = flow.column(align=True); col.prop(sliders, "SPIPOS"    , text="Lower Abdomen Position"  , slider=True)
        pass;                          col.prop(sliders, "SPISCL"    , text="Lower Abdomen Scale"     , slider=True)
        col = flow.column(align=True); col.prop(sliders, "S0APOS"    , text="Upper Abdomen Position"  , slider=True)
        pass;                          col.prop(sliders, "S0ASCL"    , text="Upper Abdomen Scale"     , slider=True)
        col = flow.column(align=True); col.prop(sliders, "S1POS"     , text="Lower Chest Position"    , slider=True)
        pass;                          col.prop(sliders, "S1_SCL"    , text="Lower Chest Scale"       , slider=True)
        col = flow.column(align=True); col.prop(sliders, "S1APOS"    , text="Upper Chest Position"    , slider=True)
        pass;                          col.prop(sliders, "S1ASCL"    , text="Upper Chest Scale"       , slider=True)
        col = flow.column();           col.prop(sliders, "S1ABASESCL", text="Upper Torso Scale"       , slider=True)
        col = flow.column(align=True); col.prop(sliders, "MUNEPOS"   , text="Breasts Position"        , slider=True)
        pass;                          col.prop(sliders, "MUNESCL"   , text="Breasts Scale"           , slider=True)
        col = flow.column(align=True); col.prop(sliders, "MUNESUBPOS", text="Breasts Sub-Position"    , slider=True)
        pass;                          col.prop(sliders, "MUNESUBSCL", text="Breasts Sub-Scale"       , slider=True)
        col = flow.column(align=True); col.prop(sliders, "NECKPOS"   , text="Neck Position"           , slider=True)
        pass;                          col.prop(sliders, "NECKSCL"   , text="Neck Scale"              , slider=True)
        col = flow.column(align=True); col.prop(sliders, "CLVPOS"    , text="Clavicle Position"       , slider=True)
        pass;                          col.prop(sliders, "CLVSCL"    , text="Clavicle Scale"          , slider=True)
        col = flow.column();           col.prop(sliders, "KATASCL"   , text="Shoulders Scale"         , slider=True)
        col = flow.column();           col.prop(sliders, "UPARMSCL"  , text="Upper Arm Scale"         , slider=True)
        col = flow.column();           col.prop(sliders, "FARMSCL"   , text="Forearm Scale"           , slider=True)
        col = flow.column();           col.prop(sliders, "HANDSCL"   , text="Hand Scale"              , slider=True)
                                                           
                                                           
                                                
                                               
                                               
                                               