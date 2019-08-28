import os
import re
import struct
import shutil
import bpy
from . import common
from . import compat
from . import cm3d2_data


@compat.BlRegister()
class CNV_OT_import_cm3d2_mate(bpy.types.Operator):
    bl_idname = 'material.import_cm3d2_mate'
    bl_label = "mateを開く"
    bl_description = "mateファイルをマテリアルとして開きます"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH')
    filename_ext = ".mate"
    filter_glob = bpy.props.StringProperty(default="*.mate", options={'HIDDEN'})

    is_decorate = bpy.props.BoolProperty(name="種類に合わせてマテリアルを装飾", default=True)
    is_replace_cm3d2_tex = bpy.props.BoolProperty(name="テクスチャを探す", default=True, description="CM3D2本体のインストールフォルダからtexファイルを探して開きます")

    @classmethod
    def poll(cls, context):
        if hasattr(context, 'material_slot'):
            if hasattr(context, 'material'):
                return True
        return False

    def invoke(self, context, event):
        prefs = common.preferences()
        if prefs.mate_default_path:
            self.filepath = common.default_cm3d2_dir(prefs.mate_default_path, "", "mate")
        else:
            self.filepath = common.default_cm3d2_dir(prefs.mate_import_path, "", "mate")
        self.is_replace_cm3d2_tex = prefs.is_replace_cm3d2_tex
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        self.layout.prop(self, 'is_decorate', icon='TEXTURE_SHADED')
        self.layout.prop(self, 'is_replace_cm3d2_tex', icon='BORDERMOVE')

    def execute(self, context):
        prefs = common.preferences()
        prefs.mate_import_path = self.filepath

        try:
            file = open(self.filepath, 'rb')
        except:
            self.report(type={'ERROR'}, message="ファイルを開くのに失敗しました、アクセス不可かファイルが存在しません。file=%s" % self.filepath)
            return {'CANCELLED'}

        if common.read_str(file) != 'CM3D2_MATERIAL':
            self.report(type={'ERROR'}, message="これはmateファイルではありません、中止します")
            return {'CANCELLED'}
        struct.unpack('<i', file.read(4))[0]
        common.read_str(file)
        mate_name = common.read_str(file)

        if not context.material_slot:
            bpy.ops.object.material_slot_add()
        root, ext = os.path.splitext(os.path.basename(self.filepath))
        mate = context.blend_data.materials.new(mate_name)
        context.material_slot.material = mate

        mate['shader1'] = common.read_str(file)
        mate['shader2'] = common.read_str(file)

        slot_index = 0
        already_texs = []
        for i in range(99999):
            type = common.read_str(file)
            if type == 'tex':
                slot = mate.texture_slots.create(slot_index)
                tex_name = common.read_str(file)
                tex = context.blend_data.textures.new(tex_name, 'IMAGE')
                slot.texture = tex
                sub_type = common.read_str(file)
                if sub_type == 'tex2d':
                    img = context.blend_data.images.new(common.read_str(file), 128, 128)
                    img['cm3d2_path'] = common.read_str(file)
                    img.filepath = img['cm3d2_path']
                    img.source = 'FILE'
                    tex.image = img
                    slot.color = struct.unpack('<3f', file.read(4*3))
                    slot.diffuse_color_factor = struct.unpack('<f', file.read(4))[0]

                    # tex探し
                    if self.is_replace_cm3d2_tex:
                        if common.replace_cm3d2_tex(img) and tex_name=='_MainTex':
                            for face in me.polygons:
                                if face.material_index == ob.active_material_index:
                                    me.uv_textures.active.data[face.index].image = img

            elif type == 'col':
                slot = mate.texture_slots.create(slot_index)
                tex_name = common.read_str(file)
                tex = context.blend_data.textures.new(tex_name, 'BLEND')
                mate.use_textures[slot_index] = False
                slot.use_rgb_to_intensity = True
                slot.color = struct.unpack('<3f', file.read(4*3))
                slot.diffuse_color_factor = struct.unpack('<f', file.read(4))[0]
                slot.texture = tex

            elif type == 'f':
                slot = mate.texture_slots.create(slot_index)
                tex_name = common.read_str(file)
                tex = context.blend_data.textures.new(tex_name, 'BLEND')
                mate.use_textures[slot_index] = False
                slot.diffuse_color_factor = struct.unpack('<f', file.read(4))[0]
                slot.texture = tex

            elif type == 'end':
                break
            else:
                self.report(type={'ERROR'}, message="未知の設定値タイプが見つかりました、中止します")
                return {'CANCELLED'}

            if common.preferences().mate_unread_same_value:
                if tex_name in already_texs:
                    mate.texture_slots.clear(slot_index)
                    slot_index -= 1
                already_texs.append(tex_name)

            slot_index += 1

        file.close()
        common.decorate_material(mate, self.is_decorate, me, ob.active_material_index)
        return {'FINISHED'}


@compat.BlRegister()
class CNV_OT_import_cm3d2_mate_text(bpy.types.Operator):
    bl_idname = 'text.import_cm3d2_mate_text'
    bl_label = "mateを開く"
    bl_description = "mateファイルをテキストとして開きます"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype='FILE_PATH')
    filename_ext = ".mate"
    filter_glob = bpy.props.StringProperty(default="*.mate", options={'HIDDEN'})

    is_overwrite = bpy.props.BoolProperty(name="現在のテキストに上書き", default=False)

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        prefs = common.preferences()
        if prefs.mate_default_path:
            self.filepath = common.default_cm3d2_dir(prefs.mate_default_path, "", "mate")
        else:
            self.filepath = common.default_cm3d2_dir(prefs.mate_import_path, "", "mate")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        self.layout.prop(self, 'is_overwrite', icon='SAVE_COPY')

    def execute(self, context):
        common.preferences().mate_import_path = self.filepath

        edit_text = None
        if self.is_overwrite:
            edit_text = getattr(context, 'edit_text')
            if not edit_text:
                self.report(type={'ERROR'}, message="上書きする為のテキストデータが見つかりません")
                return {'CANCELLED'}
            edit_text.clear()

        try:
            file = open(self.filepath, 'rb')
        except:
            self.report(type={'ERROR'}, message="ファイルを開くのに失敗しました、アクセス不可かファイルが存在しません")
            return {'CANCELLED'}
        if common.read_str(file) != 'CM3D2_MATERIAL':
            self.report(type={'ERROR'}, message="これはmateファイルではありません、中止します")
            return {'CANCELLED'}

        version = str(struct.unpack('<i', file.read(4))[0])
        name1 = common.read_str(file)
        name2 = common.read_str(file)
        if not edit_text:
            edit_text = context.blend_data.texts.new(os.path.basename(name2))
            context.area.type = 'TEXT_EDITOR'
            context.space_data.text = edit_text
        edit_text.write( version + "\n" )
        edit_text.write( name1 + "\n" )
        edit_text.write( name2 + "\n" )
        edit_text.write( common.read_str(file) + "\n" )
        edit_text.write( common.read_str(file) + "\n" )
        edit_text.write("\n")

        for i in range(99999):
            type = common.read_str(file)
            if type == 'tex':
                edit_text.write( type + "\n" )
                edit_text.write( "\t" + common.read_str(file) + "\n" )
                tex_type = common.read_str(file)
                edit_text.write( "\t" + tex_type + "\n" )
                if tex_type == 'tex2d':
                    edit_text.write( "\t" + common.read_str(file) + "\n" )
                    edit_text.write( "\t" + common.read_str(file) + "\n" )
                    fs = struct.unpack('<4f', file.read(4*4))
                    edit_text.write( "\t" + " ".join([str(fs[0]), str(fs[1]), str(fs[2]), str(fs[3])]) + "\n" )
            elif type == 'col':
                edit_text.write( type + "\n" )
                edit_text.write( "\t" + common.read_str(file) + "\n" )
                fs = struct.unpack('<4f', file.read(4*4))
                edit_text.write( "\t" + " ".join([str(fs[0]), str(fs[1]), str(fs[2]), str(fs[3])]) + "\n" )
            elif type == 'f':
                edit_text.write( type + "\n" )
                edit_text.write( "\t" + common.read_str(file) + "\n" )
                edit_text.write( "\t" + str(struct.unpack('<f', file.read(4))[0]) + "\n" )
            elif type == 'end':
                break
            else:
                self.report(type={'ERROR'}, message="未知の設定値タイプが見つかりました、中止します")
                return {'CANCELLED'}

        file.close()
        edit_text.current_line_index = 0
        return {'FINISHED'}


# テキストメニューに項目を登録
def TEXT_MT_text(self, context):
    self.layout.separator()
    self.layout.operator(import_cm3d2_mate_text.bl_idname, icon_value=common.preview_collections['main']['KISS'].icon_id)
