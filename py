# Converts 3D mesh models to Pro Evolution Soccer stadiums game file format.
# version info : version 1.8a
# blender version : 2.71
# PES version: PES2015_PC

# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "PES 2015 Stadium Exporter",
    "author": "Suat CAGDAS  'sxsxsx'",
    "version": (1,8),
    "blender": (2, 7, 1),
    "api": 35853,
    "location": "Properties space > Scene tab > Exporter panel",
    "description": "Converts 3D mesh models and textures then creates game *.bin file , it supports DDS, PNG and TGA texture formats..",
    "warning": "",
    "wiki_url": "http://forums.evo-web.co.uk/showthread.php?t=63622",
    "tracker_url": "http://forums.evo-web.co.uk/showthread.php?t=63622",
    "category": "System"}

import bpy,zlib,os
from bpy.props import *
from math import *
from mathutils import *
from struct import *

part_list=["DOWN_TRI_1","DOWN_TRI_2","DOWN_TRI_3","LEFT_TRI_1","LEFT_TRI_2","LEFT_TRI_3","CENTER_2",\
           "BASE","ROOF","RIGHT_TRI_1","RIGHT_TRI_2","RIGHT_TRI_3","UP_TRI_1","UP_TRI_2","UP_TRI_3","PITCH"]
obname=['st_front1','st_front2','st_front3','st_left1','st_left2','st_left3','st_center2','st_center1',\
            'st_center3','st_right1','st_right2','st_right3','st_back1','st_back2','st_back3','pitch','None','None','None']
partname=['bg_front_lower','bg_front_middle','bg_front_upper','bg_left_lower','bg_left_middle','bg_left_upper','bg_center_middle',\
'bg_center_lower','bg_center_upper','bg_right_lower','bg_right_middle','bg_right_upper','bg_back_lower','bg_back_middle','bg_back_upper']

main_list=["DOWN_TRI_1","DOWN_TRI_2","DOWN_TRI_3","LEFT_TRI_1","LEFT_TRI_2","LEFT_TRI_3","CENTER_2","BASE",\
           "ROOF","RIGHT_TRI_1","RIGHT_TRI_2","RIGHT_TRI_3","UP_TRI_1","UP_TRI_2","UP_TRI_3","PITCH","CROWD","LIGHTS","L_DOWN","L_RIGHT","L_LEFT","L_UP"]

part_info=["1st floor for down_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "2nd floor for down_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "3rd floor for down_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "1st floor for left_tribune objects, it supports", "transparent textures, 'visible playing game'...",
           "2nd floor for left_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "3rd floor for left_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "2nd floor objects for all sides (wall_adbs etc.), it supports", "transparent textures, auto 'invisible playing game'...",
           "Base objects around the pitch (Olimpic track,field etc.)", "supports transparent textures, visible playing game...",
           "Roof object for all sides of stadium, supports", "transparent textures, 'invisible playing game'...",
           "1st floor for right_tribune objects, it supports", "transparent textures, 'visible playing game'...",
           "2nd floor for right_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "3rd floor for right_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "1st floor for up_tribune objects, it supports", "transparent textures, 'visible playing game'...",
           "2nd floor for up_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "3rd floor for up_tribune objects, it supports", "transparent textures, auto 'invisible playing game'...",
           "Pitch object for stadium , does not need ", "assign material/textures, visible playing game...",
           "Main Part for Crowd parts and Stadium Scoreboards", "Use XXXX_2 Parts for 2nd and 3rd Floor Crowd...",
           "Main Part for Stadium Light Effects", "Select Lamp Objects and Assign Property from menu..."]

cr_list=['DOWN','DOWN_2','UP','UP_2','LEFT','LEFT_2','RIGHT','RIGHT_2']
vl_list=[0x00010000,0x00010200,0x00010001,0x00010201,0x00010002,0x00010202,0x00010003,0x00010203]
stad_id_list=[1,7,11,13,14,15,16,17,20,22,23,27,28,29,30,31,38,39,2,3,4,5,6,8,9,10,12,18,19,21,24,25,26,32,33,34,35,36,37,40]

TEMPPATH = bpy.app[4].split('blender.exe')[0]+'pes_temp\\'
DDSPATH = bpy.app[4].split('blender.exe')[0]+'pes_temp\\nvidia_dds.exe'
DDSPATH = '"'+DDSPATH+'"'
REMPATH = bpy.app[4].split('blender.exe')[0]+'pes_temp\\remove_dds_files.bat'
REMPATH = '"'+REMPATH+'"'
parentlist = [("","","")]
e_texlist,k=[],112
ob_id = 'None'

def uv_key(uv):
    return round(uv[0], 6), round(uv[1], 6)

class tri_wrapper(object):

    __slots__ = 'vertex_index', 'faceuv', 'offset'
    def __init__(self, vindex=(0,0,0), faceuv=None):
        self.vertex_index= vindex
        self.faceuv=faceuv
        self.offset= [0, 0, 0]

def triangles(mesh):

    tris_list=[]
    mesh.uv_textures[0].name = 'base'
    mesh.uv_textures[1].name = 'lightmap'
    uvcount=len(mesh.uv_textures)
    mesh.update(calc_tessface=1)

    for i, f in enumerate(mesh.tessfaces):
        fv=f.vertices
        for p in range(2):
            if len(fv) == 3:
                if p == 0:
                    new_tri = tri_wrapper((fv[0], fv[1], fv[2]))
                    uvface=mesh.tessface_uv_textures['base'].data[i] if uvcount else None
                    f_uv=uvface.uv
                    t1_uv1=uv_key(f_uv[0]), uv_key(f_uv[1]), uv_key(f_uv[2])
                else:
                    uvface=mesh.tessface_uv_textures['lightmap'].data[i] if uvcount else None
                    f_uv=uvface.uv
                    t1_uv2=(uv_key(f_uv[0]), uv_key(f_uv[1]), uv_key(f_uv[2]))
                    uv1=t1_uv1+t1_uv2
                    new_tri.faceuv=uv1
                    tris_list.append(new_tri)
            else:
                if p == 0:
                    new_tri = tri_wrapper((fv[0], fv[1], fv[2]))
                    new_tri2 = tri_wrapper((fv[0], fv[2], fv[3]))
                    uvface=mesh.tessface_uv_textures['base'].data[i] if uvcount else None
                    f_uv=uvface.uv
                    t1_uv1=uv_key(f_uv[0]), uv_key(f_uv[1]), uv_key(f_uv[2])
                    t2_uv1=uv_key(f_uv[0]), uv_key(f_uv[2]), uv_key(f_uv[3])
                else:
                    uvface=mesh.tessface_uv_textures['lightmap'].data[i] if uvcount else None
                    f_uv=uvface.uv
                    t1_uv2=(uv_key(f_uv[0]), uv_key(f_uv[1]), uv_key(f_uv[2]))
                    t2_uv2=(uv_key(f_uv[0]), uv_key(f_uv[2]), uv_key(f_uv[3]))
                    uv1=t1_uv1+t1_uv2
                    uv2=t2_uv1+t2_uv2
                    new_tri.faceuv=uv1
                    new_tri2.faceuv=uv2
                    tris_list.append(new_tri)
                    tris_list.append(new_tri2)

    return tris_list

def remove_face_uv(verts, tris_list):

        unique_uvs= [{} for i in range(len(verts))]

        for tri in tris_list:
            for i in range(3):
                context_uv_vert= unique_uvs[tri.vertex_index[i]]
                uvkey=tri.faceuv[i],tri.faceuv[i+3]
                try:
                    offset_index, uv_3ds=context_uv_vert[uvkey]
                except:
                    offset_index=len(context_uv_vert)
                    context_uv_vert[tri.faceuv[i],tri.faceuv[i+3]]= offset_index, uvkey
                tri.offset[i]=offset_index

        vert_index = 0
        vert_array = []
        normal_array = []
        uv_array = []
        index_list = []

        for i,vert in enumerate(verts):
            index_list.append(vert_index)
            x,y,z=vert.co
            nx,ny,nz=vert.normal
            uvmap = [None] * len(unique_uvs[i])
            for ii, uv_3ds in unique_uvs[i].values():
                vert_array.append((x,y,z))
                normal_array.append((nx,ny,nz))
                uvmap[ii] = uv_3ds
            for uv_3ds in uvmap:
                uv_array.append(uv_3ds)
            vert_index += len(unique_uvs[i])
        for tri in tris_list:
            for i in range(3):
                tri.offset[i]+=index_list[tri.vertex_index[i]]
            tri.vertex_index= tri.offset

        return vert_array, normal_array, uv_array, tris_list

def zlib_comp(path):

    str_o1 = open(TEMPPATH+"unzlib_data", 'rb').read()
    str_o2 = zlib.compress(str_o1, 9)
    s1,s2=len(str_o1),len(str_o2)
    f = open(path, 'wb')
    f.write(pack("4I",0x570110FF,0x53595345,s2,s1))
    f.write(str_o2),f.flush(),f.close()

def load_objs():

    global e_texlist
    part_data,objlist,texlist=[],[],[]
    scn=bpy.context.scene
    tm=scn.time_mode
    mtl,xml='st_%s.mtl' %tm,'st_%s.xml'%tm
    outpath = bpy.context.scene.export_path

    if bpy.ops.object.mode_set():
    	bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.data.objects:
        if ob.parent and ob.parent.name in main_list:
            if ob.hide == 0:
                ob.select = 1

    bpy.ops.object.transform_apply(location=1,rotation=1,scale=1)
    bpy.ops.object.select_all(action='DESELECT')

    print("\nStarting 3D Model Exporting...")

    def model_header(parent):  # MODEL DATA HEADER

        s_hdr=open(TEMPPATH+"unzlib_data","wb")
        hdr_file=open(TEMPPATH+"extras14.dll","rb")
        data1,data2,data3=hdr_file.read(112),hdr_file.read(80),hdr_file.read(132)
        data4,data5,data6=hdr_file.read(40),hdr_file.read(24),hdr_file.read(28)
        data7,data8,data9=hdr_file.read(60),hdr_file.read(28),hdr_file.read(68)
        dat10,dat11=hdr_file.read(172),hdr_file.read(192)

        s_hdr.write(data1)
        sublist=[ch_ob for ch_ob in parent.children if ch_ob.hide == 0]
        spc=len(sublist)
        hdr_offs,hdr_offs2=[],[]
        s_hdr.write(pack("3I",12,spc,20))
        for i in range(spc):
            s_hdr.write(pack("5I",1,255,255,0,255))
        s_hdr.write(pack("2I",0,0))
        hdr_offs.append(s_hdr.tell())
        for i in range(spc):
            s_hdr.write(data2)
            if i == 0:
                s_hdr.write(pack("I",0))
        hdr_offs.append(s_hdr.tell())
        for i in range(spc):
            if sublist[i].shader == "lmap":
                hdr_offs2.append(s_hdr.tell())
                s_hdr.write(data3)
            elif sublist[i].shader in ["fld1","fld2"]:
                hdr_offs2.append(s_hdr.tell())
                s_hdr.write(dat10)
            elif sublist[i].shader in ["ref1","ref2"]:
                hdr_offs2.append(s_hdr.tell())
                s_hdr.write(dat11)

        s_hdr.seek(124,0)
        off1,off2=hdr_offs[0]-k,hdr_offs[1]-k

        for i in range(spc):
            o1=off1+(80*i)
            o2=off2
            kkk=96

            if sublist[i].shader in ["fld1","fld2"]:
                kkk=136
            if sublist[i].shader in ["ref1","ref2"]:
                kkk=156

            if i != 0:
                o1=o1+4
                o3=hdr_offs2[i]-k
                s_hdr.write(pack("5I",1,o3,o3+kkk,0,o1))
            else:
                s_hdr.write(pack("5I",1,o2,o2+kkk,0,o1))

        s_hdr.seek(hdr_offs[0],0)
        bsize1_x,bsize1_y,bsize1_z,bsize2_x,bsize2_y,bsize2_z=[],[],[],[],[],[]
        for i in range(spc):
            s_hdr.seek(28,1)
            bsize1,bsize2=part_data[i][5][0],part_data[i][5][1]
            x1,y1,z1,w1=bsize1[0],bsize1[2],bsize1[1]*-1,0
            s_hdr.write(pack("4f",x1,y1,z1,w1)) # bound box size1
            x2,y2,z2,w2=bsize2[0],bsize2[2],bsize2[1]*-1,0
            s_hdr.write(pack("4f",x2,y2,z2,w2)) # bound box size2
            bsize1_x.append(x1),bsize1_y.append(y1),bsize1_z.append(z1),bsize2_x.append(x2),bsize2_y.append(y2),bsize2_z.append(z2)
            if i == 0:
                s_hdr.seek(24,1)
            else:
                s_hdr.seek(20,1)

        offset=s_hdr.tell()
        s_hdr.flush()
        s_hdr.seek(0,2)
        filesize=s_hdr.tell()
        p1_off=filesize-k
        s_hdr.seek(offset,0)

        for i in range(spc):
            s_hdr.seek(12,1)
            s_hdr.write(pack("I",s_hdr.tell()-k+4))
            s_hdr.seek(20,1)
            s_hdr.write(pack("5I",p1_off+part_data[i][0],2,5,part_data[i][6],0))
            if sublist[i].shader != "lmap":
                s_hdr.write(pack("5I",p1_off+part_data[i][9],3,5,part_data[i][6],0))
                s_hdr.write(pack("5I",p1_off+part_data[i][10],16,5,part_data[i][6],0))
                s_hdr.write(pack("5I",p1_off+part_data[i][11],15,5,part_data[i][6],0))
            s_hdr.write(pack("5I",p1_off+part_data[i][1],7,4,part_data[i][6],0))
            if sublist[i].shader not in ["fld1","fld2"]:
                s_hdr.write(pack("5I",p1_off+part_data[i][2],8,4,part_data[i][6],0))
            s_hdr.seek(12,1)
            s_hdr.write(pack("6I",p1_off+part_data[i][3],1,1,part_data[i][7]*3,0,p1_off+part_data[i][4]))

        model_data=open(TEMPPATH+'model_data.bin',"rb").read()
        s_hdr.write(model_data)
        s_hdr.flush()
        h1off=s_hdr.tell()-24
        s_hdr.write(data4)
        h2off=s_hdr.tell()-24
        s_hdr.write(pack("3I",12,spc,28))
        for i in range(spc):
            s_hdr.write(pack("7I",0,0,0,2,2,2,0))
        m1_off=s_hdr.tell()
        s_hdr.write(pack("3I",12,spc,24))
        for i in range(spc):
            s_hdr.write(data5)
        m2_off=s_hdr.tell()
        for i in range(spc):
            s_hdr.write(pack("3I",12,0,4))
        m222_off=s_hdr.tell()
        for i in range(spc):
            s_hdr.write(data6)
        m2222_off=s_hdr.tell()
        for i in range(spc):
            s_hdr.write(data7)
        m33_off=s_hdr.tell()
        s_hdr.write(pack("6I",12,0,4,12,spc,4))
        m22_off=s_hdr.tell()
        m3_off = 12+(spc*4)
        for i in range(spc):
            if i == 0:
                s_hdr.write(pack("I",m3_off))
            else:
                m3_off += part_data[i-1][12]
                s_hdr.write(pack("I",m3_off))
        for i in range(spc):
            nsize=str(len(part_data[i][8]))+'sB'
            s_hdr.write(pack(nsize,part_data[i][8].encode(),0))
        s_hdr.write(pack("H",0))
        m44_off=s_hdr.tell()
        s_hdr.write(pack("3I",0,0,4))
        m4_off=s_hdr.tell()
        s_hdr.write(data8)
        m5_off=s_hdr.tell()
        s_hdr.write(data9)
        s_hdr.seek(-48,2)
        s_hdr.write(pack("8f",min(bsize1_x),min(bsize1_y),min(bsize1_z),0,max(bsize2_x),max(bsize2_y),max(bsize2_z),0))

        s_hdr.seek(m1_off+12,0)
        a1=0xFFFFFFFF-(m1_off-125)
        for i in range(spc):
            a2=a1+(i*20)
            a3=(m2_off-m1_off)+(i*12)
            a4=(m22_off-m1_off)+(i*4)
            a5=(m222_off-m1_off)+(i*28)
            a6=(m2222_off-m1_off)+(i*60)
            s_hdr.write(pack("6I",a2,a3,a5,a4,0,a6))

        s_hdr.seek(44,0)
        s_hdr.write(pack("9I",h1off,h2off,m1_off-24,m33_off-24,m33_off-12,m5_off-24,m44_off-24,m4_off-24,m44_off))

        s_hdr.close()
        hdr_file.close()

        if parent.name != 'PITCH':
            pname1 = obname[part_list.index(parent.name)]
            pname2 = partname[part_list.index(parent.name)]
            txt1.write('\n\t<model material="./st_%s.mtl" path="./model/%s.model" type="%s"/>' %(tm,pname1,pname2))


    def main(obj):

        vlist,uvlist,normlist,flist,binorlist,tanlist=[],[],[],[],[],[]

        bsize=obj.bound_box[3][:],obj.bound_box[5][:]
        mesh=obj.data
        mesh.update(calc_tessface=1)

        tri_list=triangles(mesh)

        if len(mesh.uv_textures):
            vlist, normlist, uvlist, tri_list = remove_face_uv(mesh.vertices, tri_list)

        for tri in tri_list:
            flist.append((tri.vertex_index))

        print("")
        print("*"*60),print("\nCurrent Active Object is: %s" %ob.parent.name+' -> '+ob.name)
        #print(obj.parent.name,'->',obj.name,"is Exporting...")

        nor_off,binor_off,tan_off,uv2off = 0,0,0,0

        voff=file.tell()

        for v in range(len(vlist)):
            x,y,z=vlist[v][0],vlist[v][1],vlist[v][2]
            file.write(pack("3f",x,z,-y))

        if obj.shader != "lmap":

            nor_off=file.tell()

            for n in range(len(normlist)):
                nx,ny,nz=normlist[n][0],normlist[n][1]*-1,normlist[n][2]
                file.write(pack("3f",nx,nz,ny))
                normal=Vector((nx,ny*-1,nz))
                v_tangent=Vector.cross(normal,Vector((-1,0,0)))
                tanlist.append(v_tangent)
                binorlist.append(Vector.cross(v_tangent,normal))

            binor_off=file.tell()

            for b in range(len(binorlist)):
                bx,by,bz=binorlist[b][0],binorlist[b][1]*-1,binorlist[b][2]
                file.write(pack("3f",bx,bz,by))

            tan_off=file.tell()

            for t in range(len(tanlist)):
                tx,ty,tz=tanlist[t][0],tanlist[t][1]*-1,tanlist[t][2]
                file.write(pack("3f",tx,tz,ty))

        uv1off=file.tell()

        for w in range(len(vlist)):
            u1,v1=uvlist[w][0][0],uvlist[w][0][1]
            file.write(pack("2f",u1,1-v1))

        if obj.shader not in ["fld1","fld2"]:
            uv2off=file.tell()

            for q in range(len(vlist)):
                u2,v2=uvlist[q][1][0],uvlist[q][1][1]
                file.write(pack("2f",u2,1-v2))

        toff=file.tell()

        for idx in range(len(flist)):
            file.write(pack("3H",*flist[idx]))

        off1=file.tell()

        if obj.parent.name != 'PITCH':
            
            obname=obj.name
            
            if scn.uvtex:
                tex1 = bpy.path.abspath(ob.data.uv_textures[0].data[0].image.filepath)
                tex2 = bpy.path.abspath(ob.data.uv_textures[1].data[0].image.filepath)  
            else:
                tex1 = bpy.path.abspath(ob.active_material.texture_slots[0].texture.image.filepath)
                tex2 = bpy.path.abspath(ob.active_material.texture_slots[1].texture.image.filepath)
                
            for tt in e_texlist:
                if tex1 == tt[0]:
                    bm=tt[1]
                elif tex2 == tt[0]:
                    lm=tt[1]
        else:
            obname='pitch_mat'

        part_data.append((voff,uv1off,uv2off,toff,off1,bsize,len(vlist),len(flist),obname,nor_off,binor_off,tan_off,len(obj.name)+1)) #last index [12]

        trans='1' if obj.tra else '0'
        tside='1' if obj.ts else '0'
        
        if obj.shader == "fld2":
            shdr,x = 'Field_Day_G3','1'
        elif obj.shader == "ref1":
            shdr,x = 'LightMapReflectG3','0'
        else:
            shdr,x = 'LightMapG3','1'
        
        if obj.parent.name != 'PITCH':
            txt.write('\n\t<material name="%s" shader="%s">' %(obj.name,shdr))
            txt.write('\n\t\t<vector name="EnvParam" x="%s" y="0" z="0" w="0" />' %x)
            txt.write('\n\t\t<sampler name="DiffuseMap" path="./texture/common/%s" srgb="1" minfilter="anisotropic" magfilter="linear" mipfilter="linear" uaddr="wrap" vaddr="wrap" waddr="wrap" maxaniso="2" />' %bm)
            txt.write('\n\t\t<sampler name="MaskMap" path="./texture/common/weather_lbm_lm.dds" srgb="0" minfilter="anisotropic" magfilter="linear" mipfilter="linear" uaddr="wrap" vaddr="wrap" waddr="wrap" maxaniso="2" />')
            if shdr != 'Field_Day_G3':
                txt.write('\n\t\t<sampler name="LightMap" path="./texture/%s/%s" srgb="0" minfilter="anisotropic" magfilter="linear" mipfilter="linear" uaddr="wrap" vaddr="wrap" waddr="wrap" maxaniso="2" />' %(tm,lm))
                if shdr == 'LightMapReflectG3':
                    txt.write('\n\t\t<sampler name="EnvironmentMap" path="./texture/%s/st_cube_r.dds" srgb="0" minfilter="linear" magfilter="linear" mipfilter="linear" uaddr="wrap" vaddr="wrap" waddr="wrap" maxaniso="2" />' %tm)
            else:
                txt.write('\n\t\t<sampler name="AmbientMap" path="./texture/%s/st_ambient.dds" srgb="0" minfilter="linear" magfilter="linear" mipfilter="linear" uaddr="wrap" vaddr="wrap" waddr="wrap" maxaniso="2" />' %tm)
                txt.write('\n\t\t<sampler name="ShadeMap" path="./texture/%s/st_shade.dds" srgb="0" minfilter="linear" magfilter="linear" mipfilter="linear" uaddr="wrap" vaddr="wrap" waddr="wrap" maxaniso="2" />' %tm)
                txt.write('\n\t\t<sampler name="GroundColorMap" path="./texture/common/ground_c.dds" srgb="0" minfilter="anisotropic" magfilter="linear" mipfilter="linear" uaddr="wrap" vaddr="wrap" waddr="wrap" maxaniso="2" />')
            txt.write('\n\t\t<state name="alpharef" value="0" />')
            txt.write('\n\t\t<state name="blendmode" value="0" />')
            txt.write('\n\t\t<state name="alphablend" value="%s" />' %trans)
            txt.write('\n\t\t<state name="alphatest" value="0" />')
            txt.write('\n\t\t<state name="twosided" value="%s" />' %tside)
            txt.write('\n\t\t<state name="ztest" value="1" />')
            txt.write('\n\t\t<state name="zwrite" value="1" />')
            txt.write('\n\t</material>')

        return 1

    for ob in bpy.context.scene.objects:
        if ob.type == 'EMPTY' and ob.name in part_list:
            if len(ob.children) != 0:
                objlist.append(ob)

    txt=open(outpath+mtl,"wt")
    txt.write('<materialset>')
    txt1=open(outpath+xml,"wt")
    txt1.write('<?xml version="1.0" encoding="UTF-8"?>')
    txt1.write('\n<stadium>')

    for object in objlist:

        s=0
        file=open(TEMPPATH+'model_data.bin',"wb")

        for ob in object.children:  # script starts here
            if ob.hide == 0:
                if main(ob):
                    s=1

        file.flush(),file.close()
        if s:
            dat12=model_header(object) # add header
            part_data=[]
            pname1 = obname[part_list.index(object.name)]
            outpath2 = outpath+'model\\'+pname1+'.model'
            if object.name == 'PITCH':
                outpath2 = outpath[:-14]+'pitch\\'+scn.stadid+'\\model\\pitch.model'
            zlib_comp(outpath2)

    os.remove(TEMPPATH+'unzlib_data')
    os.remove(TEMPPATH+'model_data.bin')
    txt.write('\n</materialset>')
    txt.flush(),txt.close()

    txt1.write('\n\t<luminance path="./etc/stad_%s.lmn"/>' %tm)
    txt1.write('\n\t<texture path="./texture/%s/st_shade.dds" type="shadow_plane"/>' %tm)
    txt1.write('\n\t<texture path="./etc/cg_%s.dds" type="color_grading_game"/>' %tm)
    txt1.write('\n\t<texture path="./etc/cg_%s_demo.dds" type="color_grading_demo"/>' %tm)
    txt1.write('\n\t<texture path="./etc/env_%s.dds" type="envmap"/>' %tm)
    txt1.write('\n\t<irv path="./etc/stad_%s.irv"/>' %tm)
    txt1.write('\n</stadium>')
    txt1.flush(),txt1.close()

    if tm == "df":
        dat12=open(TEMPPATH+"Temp\\sun_cfg.xml","rt").read()
        sun_x,sun_y,sun_z=bpy.data.objects['PES_Sun'].location
        sun_x,sun_y,sun_z=round(sun_x*-1,3),round(sun_y,3),round(sun_z*-1,3)
        dat12=dat12.replace('%x',str(sun_x))
        dat12=dat12.replace('%y',str(sun_z))
        dat12=dat12.replace('%z',str(sun_y))
        light_cfg=open(outpath+'etc\\light_config_df.xml','wt')
        light_cfg.write(dat12),light_cfg.flush(),light_cfg.close()
        print(""),print("Info: Exported Sun Light Position Successfully...")

    if bpy.ops.object.mode_set():
    	bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.data.objects:
        if ob.parent and ob.parent.name in main_list:
            if ob.hide == 0:
                ob.select = 1
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')

def ddsconvert():

    global e_texlist
    dxt5=" -fast -alpha -bc3 " if bpy.context.scene.cuda else " -alpha -nocuda -bc3 "
    ac_obj=bpy.context.active_object
    texlist,e_texlist=[],[]
    scn = bpy.context.scene
    tm = scn.time_mode
    
    def convert(tex,obj,s,x):
        if s:
            ext='lm_'+str(x)+'.dds' if x > 9 else 'lm_0'+str(x)+'.dds'
            f='texture\\%s\\tex_' %tm
        else:
            ext='bm_'+str(x)+'.dds' if x > 9 else 'bm_0'+str(x)+'.dds'
            f='texture\\common\\tex_'

        e_texlist.append((tex,'tex_'+ext))
        if os.access(tex,0) == 0:
            print("\nDDS Convertion Failed !! (File Not Found or Unsupported Type)"), print("\nCheck out Object ==> %s" %obj.parent.name+' -> '+obj.name)
        if tex[-4:] in ['.png','.tga']:  ##  Convert TGA,PNG
            output=TEMPPATH+"unzlib_data"
            output2='"'+output+'"'
            input2='"'+tex+'"'
            print("")
            os.system('"'+DDSPATH+dxt5+" "+input2+" "+output2+'"')  # Convert to DXT 5 (with alpha)
            if os.access(output,0) == 1:
                print("\nDDS Convertion OK... ")
                path=scn.export_path+f+ext
                zlib_comp(path)
            else:
                print("\nDDS Convertion Failed !! (File Not Found or Unsupported Type)"), print("\nCheck out Object ==> %s" %obj.parent.name+' -> '+obj.name)
                return 1

        elif tex[-4:] == '.dds': ##  Export DDS
            ddsdata=open(tex,'rb').read()
            out=open(TEMPPATH+"unzlib_data","wb")
            out.write(ddsdata)
            out.flush(),out.close()
            path=scn.export_path+f+ext
            zlib_comp(path)
        else:
            print("\nERROR - Invalid Texture Format!! (Supported only PNG,TGA,DDS)"), print("\nCheck out Object ==> %s" %obj.parent.name+' -> '+obj.name)
            return 1

    bx=lx=0
    for pob in bpy.context.scene.objects:
        if pob.type == 'EMPTY' and pob.name in part_list:
            if len(pob.children) != 0:
                for ob in pob.children:   
                    if (ob.type == 'MESH') and (ob.parent.name != 'PITCH') and (ob.hide == 0):
                        print("\nCurrent Active Object is: %s" %ob.parent.name+' -> '+ob.name)
                        if scn.uvtex:
                            try:
                                tex1 = bpy.path.abspath(ob.data.uv_textures[0].data[0].image.filepath)
                                tex2 = bpy.path.abspath(ob.data.uv_textures[1].data[0].image.filepath)
                            except(AttributeError):
                                print("ERROR: Not Found UVmap Textures !!")
                                return 0 
                        else:
                            try:
                                tex1 = bpy.path.abspath(ob.active_material.texture_slots[0].texture.image.filepath)
                                tex2 = bpy.path.abspath(ob.active_material.texture_slots[1].texture.image.filepath)
                            except(AttributeError):
                                print("ERROR: Not Found Material Textures !!")
                                return 0 
                            
                        if tex1 not in texlist:
                            texlist.append(tex1)
                            bx+=1
                            if convert(tex1,ob,0,bx):
                                return 0
                        if tex2 not in texlist:
                            texlist.append(tex2)
                            lx+=1
                            if convert(tex2,ob,1,lx):
                                return 0

    stex1=stex2='notex'
    try:
        stex1 = bpy.path.abspath(bpy.data.objects['shadow_plane'].data.uv_textures[0].data[0].image.filepath)
    except:
        pass
    try:
        stex2 = bpy.path.abspath(bpy.data.objects['shadow_plane'].data.uv_textures[1].data[0].image.filepath)
    except:
        pass

    if (stex1 != 'notex') and (stex1[-4:] in ['.png','.tga']) and (os.access(stex1,0) == 1) and (scn.time_mode == 'df'):
        dxt,dxt5=" -fast -nomips -rgb "," -fast -nomips -alpha -bc3 "
        output4=TEMPPATH+"shadow_tex.dds"
        output5='"'+output4+'"'
        input2='"'+stex1+'"'
        print("")
        os.system('"'+DDSPATH+dxt+" "+input2+" "+output5+'"')
        m_stex1=open(output4,'r+b')
        m_stex1.seek(0,2)
        fsize=m_stex1.tell()
        m_stex1.seek(128,0)
        while (m_stex1.tell() != fsize):
            r,g,b = unpack('3B',m_stex1.read(3))
            a=int((r+g+b)/3)
            m_stex1.seek(-3,1)
            m_stex1.write(pack('4B',0,0,0,a))
        m_stex1.flush(),m_stex1.close()

        output4=TEMPPATH+"unzlib_data"
        output5='"'+output4+'"'
        input=TEMPPATH+"shadow_tex.dds"
        input2='"'+input+'"'
        print("")
        os.system('"'+DDSPATH+dxt5+" "+input2+" "+output5+'"')
        path=scn.export_path+'texture\\df\\st_shade.dds'
        zlib_comp(path)

    if (stex2 != 'notex') and (stex2[-4:] in ['.png','.tga']) and (os.access(stex2,0) == 1) and (scn.time_mode == 'df'):
        dxt1=" -fast -nomips -bc1 "
        output6=TEMPPATH+"unzlib_data"
        output7='"'+output6+'"'
        input4='"'+stex2+'"'
        print("")
        os.system('"'+DDSPATH+dxt1+" "+input4+" "+output7+'"')
        path=scn.export_path+'texture\\df\\st_ambient.dds'
        zlib_comp(path)

    if os.access(TEMPPATH+'unzlib_data',0) == 1:
        os.remove(TEMPPATH+'unzlib_data')
    if os.access(TEMPPATH+'shadow_tex.dds',0) == 1:
        os.remove(TEMPPATH+'shadow_tex.dds')

    return 1

def crowd_exp():

    scn = bpy.context.scene
    tm = scn.time_mode
    outpath = scn.export_path
    
    if bpy.ops.object.mode_set():
    	bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.data.objects:
        if ob.parent and ob.parent.name == 'CROWD':
            if ob.hide == 0:
                ob.select = 1

    bpy.ops.object.transform_apply(location=1,rotation=1,scale=1)
    bpy.ops.object.select_all(action='DESELECT')

    print("\nStarting Crowd Parts Exporting...")
    
    hdr_file=open(TEMPPATH+"extras14.dll","rb")
    hdr_file.seek(1274,0)
    dat17=hdr_file.read(380)
    dat18=hdr_file.read(328)
    hdr_file.flush(),hdr_file.close()
    dat19=open(TEMPPATH+"Temp\\tv_cfg.xml","rt").read()
    dat20=open(TEMPPATH+"Temp\\tv_cfg.mtl","rt").read()
    
    def sb_export(sb_obj,i):
        
        bsize=sb_obj.bound_box[3][:],sb_obj.bound_box[5][:]
        mesh=sb_obj.data
        mesh.update(calc_tessface=1)
        
        tvxml.seek(0,2)
        tvxml.write('\n\t<model material="./tv_%s.mtl" path="./model/tv_tv_0%i.model" ratio="1.806"/>' %(tm,i))
        
        sb_fileout=open(outpath+'model\\tv_tv_0'+str(i)+'.model',"wb")
        sb_fileout.write(dat17)
        sb_fileout.seek(176,0)
        sb_fileout.write(pack("8f",bsize[0][0],bsize[0][2],-bsize[0][1],0,bsize[1][0],bsize[1][2],-bsize[1][1],0))
        sb_fileout.seek(0,2)
        
        vlist,uvlist,normlist,flist=[],[],[],[]

        tri_list=triangles(mesh)

        if len(mesh.uv_textures):
            vlist, normlist, uvlist, tri_list = remove_face_uv(mesh.vertices, tri_list)

        for tri in tri_list:
            flist.append((tri.vertex_index))
        
        for v in range(len(vlist)):
            x,y,z=vlist[v][0],vlist[v][1],vlist[v][2]
            sb_fileout.write(pack("3f",x,z,-y))
        for n in range(len(normlist)):
            nx,ny,nz=normlist[n][0],normlist[n][1],normlist[n][2]
            sb_fileout.write(pack("3f",nx,nz,-ny))
            
        for w in range(len(vlist)):
            u1,v1=uvlist[w][0][0],uvlist[w][0][1]
            sb_fileout.write(pack("2f",u1,1-v1))
        for q in range(len(vlist)):
            u2,v2=uvlist[q][1][0],uvlist[q][1][1]
            sb_fileout.write(pack("2f",u2,1-v2))

        for idx in range(len(flist)):
            sb_fileout.write(pack("3H",*flist[idx]))
            
        sb_fileout.write(dat18)
        sb_fileout.seek(-48,2)
        
        sb_fileout.write(pack("8f",bsize[0][0],bsize[0][2],-bsize[0][1],0,bsize[1][0],bsize[1][2],-bsize[1][1],0))
        sb_fileout.flush(),sb_fileout.close()    
        
    def crowd14(obj):
        print("*"*20)
        print(obj.name)
        
        off1=cr_file.tell()
        off_list.append(off1)
        cr_file.write(pack("I",vl_list[cr_list.index(obj.name)]))
        cr_file.write(pack("I",off1+8))
        bsize=obj.bound_box[3][:],obj.bound_box[5][:]
        mesh=obj.data
        mesh.update(calc_tessface=1)

        ud=0
        if obj.name[:1] in ['L','R']:
            ud=1

        cr_file.write(pack("6f",bsize[0][0],bsize[0][2],bsize[0][1]*-1,bsize[1][0],bsize[1][2],bsize[1][1]*-1))
        cr_file.write(pack("I",len(mesh.tessfaces)))
        for f, face in enumerate(mesh.tessfaces):
            vec1,vec2,idx1,idx2,vlist=[],[],[],[],[]
            v1,v2,v3,v4=0,0,0,0
            for p, v in enumerate(face.vertices):
                uvface = mesh.tessface_uv_textures[0].data[face.index]
                fuv=uvface.uv
                if mesh.vertices[v].co.z > face.center.z:
                    u,w=fuv[p][0],fuv[p][1]
                    idx1.append((v,u,w))
                else:
                    u,w=fuv[p][0],fuv[p][1]
                    idx2.append((v,u,w))

            if len(idx1)==len(idx2):
                for t in range(0,len(idx1),2):
                    vec1.append((mesh.vertices[idx1[t][0]].co+mesh.vertices[idx1[t+1][0]].co)/2)
                    vec1.append((mesh.vertices[idx1[t][0]].co+mesh.vertices[idx1[t+1][0]].co)/2)
                    vec2.append((mesh.vertices[idx2[t][0]].co+mesh.vertices[idx2[t+1][0]].co)/2)
                    vec2.append((mesh.vertices[idx2[t][0]].co+mesh.vertices[idx2[t+1][0]].co)/2)

                for x in range(0,len(idx1),2):
                    if (mesh.vertices[idx1[x+0][0]].co[ud]) < (vec1[x][ud]):
                        v1=mesh.vertices[idx1[x+0][0]].co,idx1[x+0][1],idx1[x+0][2]
                    else:
                        v1=mesh.vertices[idx1[x+1][0]].co,idx1[x+1][1],idx1[x+1][2]
                    if (mesh.vertices[idx1[x+0][0]].co[ud]) > (vec1[x][ud]):
                        v2=mesh.vertices[idx1[x+0][0]].co,idx1[x+0][1],idx1[x+0][2]
                    else:
                        v2=mesh.vertices[idx1[x+1][0]].co,idx1[x+1][1],idx1[x+1][2]
                    if (mesh.vertices[idx2[x+0][0]].co[ud]) < (vec2[x][ud]):
                        v3=mesh.vertices[idx2[x+0][0]].co,idx2[x+0][1],idx2[x+0][2]
                    else:
                        v3=mesh.vertices[idx2[x+1][0]].co,idx2[x+1][1],idx2[x+1][2]
                    if (mesh.vertices[idx2[x+0][0]].co[ud]) > (vec2[x][ud]):
                        v4=mesh.vertices[idx2[x+0][0]].co,idx2[x+0][1],idx2[x+0][2]
                    else:
                        v4=mesh.vertices[idx2[x+1][0]].co,idx2[x+1][1],idx2[x+1][2]

                    vlist.append(v4),vlist.append(v2),vlist.append(v1),vlist.append(v3)
                    row=round((v1[0]-v3[0]).length,1)
            else:
                print("Bad Mesh Faces for %s Crowd Part, Fix it before export !!" %obj.name)

            ha=0.85
            try:
                if obj.material_slots[face.material_index].name == 'away':
                    ha=0.15
                if obj.material_slots[face.material_index].name == 'neutral':
                    ha=0.5
            except:
                pass
            row2=round((row/(5.0+scn.row_space)),1)
            cr_file.write(pack("I",f))
            cr_file.write(pack("3f",row2,ha,ha))
            for w in vlist:
                cr_file.write(pack("3f",w[0][0],w[0][2],w[0][1]*-1))
            for m in vlist:
                cr_file.write(pack("2f",m[1],m[2]))

    outpath_crowd_data = outpath[:-14]+'audi\\area\\'+scn.stadid+'\\data\\audiarea.bin'
    outpath_crowd_tex = outpath[:-14]+'audi\\area\\'+scn.stadid+'\\texture\\%s\\' %tm
    ### EXPORT CROWD LIGHTMAP TEXTURES ###
    ctex1=ctex2=ctex3='notex'
    dxt,dxt_m=" -fast -nomips -bc1 "," -fast -bc1 "
    
    try:
        for crw in bpy.data.objects['CROWD'].children:
            if not crw.name.startswith('SCOREBOARD'):
                crw_ob = crw
    except:
        pass
    
    try:
        ctex1=bpy.path.abspath(crw_ob.data.uv_textures[0].data[0].image.filepath)
    except:
        pass
    
    try:
        ctex2=bpy.path.abspath(crw_ob.data.uv_textures[1].data[0].image.filepath)
    except:
        pass
    
    if tm == 'df':
        try:
            ctex3=bpy.path.abspath(crw_ob.data.uv_textures[2].data[0].image.filepath)
        except:
            pass
    
    if (ctex1 != 'notex') and (ctex1[-4:] in ['.png','.tga']) and (os.access(ctex1,0) == 1):
        
        output2=outpath_crowd_tex[:-3]+'common\\au_seat.dds'
        output2='"'+output2+'"'
        input2='"'+ctex1+'"'
        print("")
        os.system('"'+DDSPATH+dxt_m+" "+input2+" "+output2+'"')
    if (ctex2 != 'notex') and (ctex2[-4:] in ['.png','.tga']) and (os.access(ctex2,0) == 1):
        
        output3=outpath_crowd_tex+'au_ambient.dds'
        output3='"'+output3+'"'
        input3='"'+ctex2+'"'
        print("")
        os.system('"'+DDSPATH+dxt+" "+input3+" "+output3+'"')
    if tm == 'df':
        if (ctex3 != 'notex') and (ctex3[-4:] in ['.png','.tga']) and (os.access(ctex3,0) == 1):
            
            output4=outpath_crowd_tex+'au_shade.dds'
            output4='"'+output4+'"'
            input4='"'+ctex3+'"'
            print("")
            os.system('"'+DDSPATH+dxt+" "+input4+" "+output4+'"')

    cr_file=open(outpath_crowd_data,"wb")
    cr_file.write(pack("2I48s",1,1,"".encode()))
    off_list,cr_list_temp,sb_list = [],[],[]
    
    for cr in bpy.data.objects['CROWD'].children:
        if cr.name.startswith('SCOREBOARD'):
            sb_list.append(cr.name)
        else:
            cr_list_temp.append(cr.name)
    
    if len(sb_list):
        fn1=outpath+'tv_%s.xml' %tm
        fn2=outpath+'tv_%s.mtl' %tm
        tvxml=open(fn1,"wt")
        tvxml.write(dat19)
        tv_mtl=open(fn2,"wt")
        dat20=dat20.replace('%b',tm)
        tv_mtl.write(dat20) 
        tv_mtl.flush(),tv_mtl.close()
        
        for sb in range(len(sb_list)):
            sb_export(bpy.data.objects[sb_list[sb]],sb)
            
        tvxml.write('\n</stadium>')
        tvxml.flush(),tvxml.close()
        
    for ob in cr_list:
        if ob in cr_list_temp:
            crowd14(bpy.data.objects[ob])
        else:
            off_list.append(0)

    cr_file.seek(8,0)
    for i, o in enumerate(off_list):
        cr_file.write(pack("I",o))
        if i in [0,2,4,6]:
            cr_file.write(pack("I",0))

    cr_file.flush(),cr_file.close()

    if bpy.ops.object.mode_set():
    	bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.data.objects:
        if ob.parent and ob.parent.name == 'CROWD':
            if ob.hide == 0:
                ob.select = 1
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    bpy.ops.object.select_all(action='DESELECT')

def id_changer():

    scn=bpy.context.scene
    id_o=scn.old_id
    id_n=scn.new_id
    out1=scn.id_path
    out=out1+'bg\\model\\bg'

    print("*"*50)
    os.rename(out+'\\ad\\texture\\ad_'+id_o[-3:]+'.dds',out+'\\ad\\texture\\ad_'+id_n[-3:]+'.dds')
    os.rename(out+'\\audi\\area\\'+id_o,out+'\\audi\\area\\'+id_n)

    for i in ['\\'+id_o+'_df.xml','\\'+id_o+'_dr.xml','\\'+id_o+'_nf.xml','\\'+id_o+'_nr.xml']:
        txt1=open(out+'\\bill\\'+id_o+i,'rt').read()
        txt1=txt1.replace(id_o,id_n)
        open(out+'\\bill\\'+id_o+i,'wt').write(txt1)
    txt1=open(out+'\\bill\\'+id_o+'\\bill_texlist.xml','rt').read()
    txt1=txt1.replace(id_o,id_n)
    open(out+'\\bill\\'+id_o+'\\bill_texlist.xml','wt').write(txt1)
    os.rename(out+'\\bill\\'+id_o+'\\'+id_o+'_df.xml',out+'\\bill\\'+id_o+'\\'+id_n+'_df.xml')
    os.rename(out+'\\bill\\'+id_o+'\\'+id_o+'_dr.xml',out+'\\bill\\'+id_o+'\\'+id_n+'_dr.xml')
    os.rename(out+'\\bill\\'+id_o+'\\'+id_o+'_nf.xml',out+'\\bill\\'+id_o+'\\'+id_n+'_nf.xml')
    os.rename(out+'\\bill\\'+id_o+'\\'+id_o+'_nr.xml',out+'\\bill\\'+id_o+'\\'+id_n+'_nr.xml')
    os.rename(out+'\\bill\\'+id_o,out+'\\bill\\'+id_n)
    os.rename(out+'\\bill\\billBody\\'+id_o,out+'\\bill\\billBody\\'+id_n)
    #os.rename(out+'\\bill\\90systemAd\\'+id_o,out+'\\bill\\90systemAd\\'+id_n)

    for i in ['\\cheer_df.mtl','\\cheer_nf.mtl','\\cheer_dr.mtl','\\cheer_nr.mtl']:
        txt1=open(out+'\\cheer\\'+id_o+i,'rt').read()
        txt1=txt1.replace(id_o,id_n)
        open(out+'\\cheer\\'+id_o+i,'wt').write(txt1)

    os.rename(out+'\\cheer\\'+id_o,out+'\\cheer\\'+id_n)
    os.rename(out+'\\effect\\locator\\'+id_o,out+'\\effect\\locator\\'+id_n)

    for i in ['\\pitch_s_df.mtl','\\pitch_s_nf.mtl','\\pitch_w_df.mtl','\\pitch_w_nf.mtl','\\pitch_s_dr.mtl','\\pitch_s_nr.mtl','\\pitch_w_dr.mtl','\\pitch_w_nr.mtl']:
        txt1=open(out+'\\pitch\\'+id_o+i,'rt').read()
        txt1=txt1.replace(id_o,id_n)
        open(out+'\\pitch\\'+id_o+i,'wt').write(txt1)

    os.rename(out+'\\pitch\\'+id_o,out+'\\pitch\\'+id_n)
    os.rename(out+'\\scarecrow\\'+id_o,out+'\\scarecrow\\'+id_n)
    os.rename(out+'\\sky\\'+id_o,out+'\\sky\\'+id_n)

    for i in ['\\ad_df.mtl','\\ad_nf.mtl','\\ad_dr.mtl','\\ad_nr.mtl']:
        txt1=open(out+'\\stadium\\'+id_o+i,'rt').read()
        x1='ad_'+id_o[-3:]+'.dds'; x2='ad_'+id_n[-3:]+'.dds'
        txt1=txt1.replace(x1,x2)
        open(out+'\\stadium\\'+id_o+i,'wt').write(txt1)

    os.rename(out+'\\stadium\\'+id_o,out+'\\stadium\\'+id_n)
    os.rename(out+'\\staff\\common\\texture\\staff_'+id_o+'.dds',out+'\\staff\\common\\texture\\staff_'+id_n+'.dds')
    os.rename(out+'\\staff\\'+id_o,out+'\\staff\\'+id_n)

    out2=out[:-11]
    os.rename(out2+'\\render\\model\\bg\\hit\\bill\\'+id_o,out2+'\\render\\model\\bg\\hit\\bill\\'+id_n)
    os.rename(out2+'\\render\\model\\bg\\hit\\stadium\\'+id_o,out2+'\\render\\model\\bg\\hit\\stadium\\'+id_n)
    os.rename(out2+'\\render\\thumbnail\\stadium\\'+id_o+'.dds',out2+'\\render\\thumbnail\\stadium\\'+id_n+'.dds')

def name_changer():
    scn=bpy.context.scene
    out3=scn.id_path+'\\etc\\pesdb\\Stadium.bin'
    sid=stad_id_list.index(int(scn.nameid[-2:],10))
    stadbin=open(out3,'r+b')
    stadbin.seek(129+(sid*272),0)
    stadbin.write(pack('80s',"".encode()))
    stadbin.seek(-80,1)
    stadbin.write(pack('80s',scn.stadname.encode()))
    stadbin.flush(),stadbin.close()

def light_fx():
    scn = bpy.context.scene
    hdr_file=open(TEMPPATH+"extras14.dll","rb")
    hdr_file.seek(942,0)
    dat13=hdr_file.read(236)
    dat14=hdr_file.read(28)
    dat15=hdr_file.read(68)
    hdr_file.flush(),hdr_file.close()
    
    cfg = 'effect_config_%s.xml' %scn.time_mode
    
    dat16=open(TEMPPATH+'Temp\\'+cfg,'rt').read()
    LT = scn.lfx_tex
    if LT in ['00','01','04']:
        LR = '30'
    else:
        LR = '45'
    dat16=dat16.replace('%LT',LT)
    dat16=dat16.replace('%LR',LR)
    dat16=dat16.replace('stxxx',scn.stadid)
    light_cfg=open(scn.export_path+'etc\\'+cfg,'wt')
    light_cfg.write(dat16)
    light_cfg.flush(),light_cfg.close()
    
    lamp_list=["L_DOWN","front3","L_LEFT","left3","L_RIGHT","right3","L_UP","back3"]
    
    def lamp_side(p_name,l_count):
        
        i=lamp_list.index(p_name)
        
        if scn.time_mode == 'df':
            outpath_lightfx = scn.export_path[:-14]+'effect\\locator\\'+scn.stadid+'\\locstar_%s_df.model' %lamp_list[i+1]    
        elif scn.time_mode == 'dr':
            outpath_lightfx = scn.export_path[:-14]+'effect\\locator\\'+scn.stadid+'\\locstar_%s_dr.model' %lamp_list[i+1] 
        else:
            outpath_lightfx = scn.export_path[:-14]+'effect\\locator\\'+scn.stadid+'\\locstar_%s_nf_nr.model' %lamp_list[i+1]
            
        lfx=open(outpath_lightfx,"wb")
        lfx.write(dat13)
        lfx.write(pack("4I",(48*l_count+40),l_count,0x72617473,0))
        return lfx

    for p_lamp in bpy.data.objects['LIGHTS'].children:
        if len(p_lamp.children) > 0:
            l_count=len(p_lamp.children)
            lfx=lamp_side(p_lamp.name,l_count)
            
            for lamp in p_lamp.children:
                l_energy=lamp.fx_e
                lfx.write(pack("12f",l_energy,0,0,lamp.location.x,0,1,0,lamp.location.z,0,1,0,(lamp.location.y*-1)))
            
            for i in range(l_count):
                if i == 0:
                    x=4*l_count
                else:
                    x+=28
                lfx.write(pack("I",x))
        
            for p in range(l_count):
                lfx.write(dat14)
            
            sz1=lfx.tell()
            lfx.write(dat15)
            lfx.seek(64,0)
            lfx.write(pack("I",sz1-24))
            lfx.close()

  ###### User Interface Panel & Operators & API Functions #######

class OBJECT_Exporter(bpy.types.Panel):
    bl_label = "PES 2015 BSE v1.8a [PC Game]"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):

        global ob_id
        obj = bpy.context.active_object
        scn = bpy.context.scene
        obj_co = len(scn.objects)
        layout = self.layout
        
        box=layout.box()
        box.alignment='CENTER'
        """
        if bpy.app[1][:4] != '2.67':
            box.alignment='CENTER'
            box.label(text=" This tool works with only Blender 2.67", icon='ERROR')
        """
        row=box.row(align=0)
        row.operator("wm.url_open",text="Visit Evo-Web Thread",icon="URL").url="http://www.evo-web.co.uk/forums/showthread.php?t=63622"
        row.operator("wm.url_open",text="Visit Blender Page",icon="BLENDER").url="www.blender.org"
        row=box.row()
        row.label(text=" BSE v1.8a - Blender v2.71",icon="INFO")
        row=box.row()
        row.label(text=" Made by Suat CAGDAS",icon="INFO")
        row.operator("bse14.operator", text="Create Main Parts", icon="EMPTY_DATA").opname='parents'
        row=box.row()

        if not obj:
            box=layout.box()
            box.alignment='CENTER'
            box.label(text=" No active object or there is no object in the scene,", icon="ERROR")
            box.label(text="Select any object or add new objects in to scene...")
            
        else:

            if obj.type == 'LAMP':
                    box = layout.box()
                    box.alignment='CENTER'
                    box.label(text="Active Light Object Info : ",icon="INFO")
                    row = box.row()
                    if obj.parent:
                        lp=obj.parent.name
                    else:
                        lp="Not Assigned"
                    row.label(text="Parent: " +lp)
                    row.label(text="Name: " +obj.name)
                    row.label(text="Energy: " +str(round(obj.fx_e,2))[:4])
                    row = box.row()
                    
                    row.prop(scn,"lit_side",text="")
                    row.prop(scn,"fxe")
                    row.operator("bse14.operator",text="Set Light FX",icon="FILE_TICK").opname='set_lfx_side'
                    row = box.row()

            elif obj.parent and obj.type != 'LAMP':

                box=layout.box()
                box.alignment='CENTER'
                row=box.row()
                row.label(text="Parent : " +obj.parent.name, icon="EMPTY_DATA")
                row.label(text="Object : " +obj.name, icon="OBJECT_DATA")

            elif bool(obj.parent)==0 and obj.type == 'EMPTY':
                if obj.name in main_list:
                    box=layout.box()
                    box.label(text="    Not selected a mesh object, select mesh",icon="INFO")
                    box.label(text="          object or add new mesh objects...")
                    row = layout.row(); row = layout.row(); box = layout.box()
                    box.alignment = 'LEFT'
                    box.label(text="Main Part Info : "+obj.name+"  ==  "+obname[main_list.index(obj.name)]+".model",icon='INFO')
                    info = main_list.index(obj.name)
                    info*=2
                    box.label(text=part_info[info])
                    box.label(text=part_info[info+1])
                    row=layout.row; row=layout.row; row=layout.row()

                    box=layout.box()
                    row=box.row(); row.label("Stadium ID Changer :",icon='INFO')
                    row=box.row(); row.prop(scn,'id_path',text="'common' "); row=box.row()
                    row.prop(scn,'old_id',text="Old"); row.prop(scn,'new_id',text="New")
                    row.operator("bse14.operator", text="Change ID").opname='set_id'
                    row=box.row(); row=row.split(0.17); row.prop(scn,'nameid',text="")
                    row=row.split(0.6); row.prop(scn,'stadname',text="")
                    row.operator("bse14.operator", text="Change Name").opname='set_name'
                    row=box.row(); row=layout.row(); row=layout.row(); row=layout.row()

                else:
                    box = layout.box()
                    box.alignment='CENTER'
                    box.label(text="  Active Object is not valid object, select another...", icon="ERROR")

            elif obj.type == 'CAMERA' or obj.type == 'CURVE' or obj.type == 'FONT':
                box=layout.box()
                box.label(text="   Active Object is not a valid Object Type,",icon="ERROR")
                box.label(text="        Select a Mesh or Empty Object...")
                row = layout.row()

            else:
                box = layout.box()
                box.alignment='CENTER'
                box.label(text="  No parent for active object, assign a parent...", icon="ERROR")
                row = layout.row()

            if obj.type == 'MESH':
                row = box.row()
                row.label(text="Vertex Count : " +str(len(obj.data.vertices)), icon="VERTEXSEL")
                row.label(text="Face Count : " +str(len(obj.data.polygons)), icon="FACESEL")
                row = box.row()
                row.alignment = 'EXPAND'
                split = row.split(percentage=1)
                split = split.split(percentage=0.6)
                row = split.row()
                row.prop(obj, "droplist", text="Parent")
                ob_id = obj.droplist
                split = split.split(percentage=1)
                row = split.row()
                row.operator("bse14.operator",text="",icon="FILE_REFRESH").opname='refresh'
                row.operator("bse14.operator",text="SET").opname='setparent'
                row.operator("bse14.operator",text="CLR").opname='clrparent'
                row = box.row()
                split = row.split(percentage=1)
                split = split.split(percentage=0.57)
                col = split.column()
                col.prop(obj,"name",text="Object ")
                row = col.row(); row = col.row(); ic1=ic2="ERROR"; a1=a2="None"

                if obj.parent and obj.parent.name == 'PITCH':
                        box.label(text=" No need Material/Textures for Pitch Object...",icon="INFO")
                
                if obj.parent and obj.name.startswith('SCOREBOARD') :
                        box.label(text=" No need Material/Textures for Scoreboard Object...",icon="INFO")
                
                if scn.uvtex:
                    col.label("Material :  (UVmap Mode)")
                else:    
                    if obj.active_material:
                        col.prop(obj.active_material,"name",text="Material")
                    else:
                        col.label("Material :  Not Assigned",icon='ERROR')    
                row = box.row()
                split = split.split(percentage=1)
                col = split.column()
                if obj.parent and obj.parent.name == "CROWD":
                    if obj.name not in cr_list:
                        if not obj.name.startswith('SCOREBOARD'): 
                            box.label(text=" Crowd Part Name is Wrong, Fix it before Export... ",icon="ERROR")

                else:
                    split=col.split(percentage=1)
                    row=split.row()
                    row.prop(obj,"tra",text="Trans")
                    row.prop(obj,"ts",text="Tside")
                    row=col.row(); row=col.row()
                    col.prop(obj,"shader",text="")
                    mtex1='notex'; mtex2='notex'
                    try:
                        if scn.uvtex:
                            mtex1 = bpy.path.abspath(obj.data.uv_textures[0].data[0].image.filepath)
                        else:
                            mtex1 = bpy.path.abspath(obj.active_material.texture_slots[0].texture.image.filepath) 
                    except:
                        pass
                    
                    if (mtex1 != 'notex') and (mtex1[-4:] in ['.png','.tga','.dds']) and (os.access(mtex1,0) == 1):
                        ic1="TEXTURE_DATA"
                        if scn.uvtex:
                            b_s1,b_s2=obj.data.uv_textures[0].data[0].image.name,mtex1
                        else:
                            b_s1,b_s2=obj.active_material.texture_slots[0].texture.image.name,mtex1
                        b_ic1="IMAGE_DATA";a1=mtex1[-3:].upper()+' Image';t1=1
                        if len(b_s2)>30:
                            b_s2="..."+b_s2[(len(b_s2)-24):]
                    else:
                        b_s1,b_s2,b_ic1,ic1,a1,t1="None","None","ERROR","ERROR","None",0
                        box.label(text=" Not Found Base Texture",icon="ERROR")

                    try:
                        if scn.uvtex:
                            mtex2 = bpy.path.abspath(obj.data.uv_textures[1].data[0].image.filepath)
                        else:
                            mtex2 = bpy.path.abspath(obj.active_material.texture_slots[1].texture.image.filepath) 
                    except:
                        pass
                    if (mtex2 != 'notex') and (mtex2[-4:] in ['.png','.tga','.dds']) and (os.access(mtex2,0) == 1):
                        ic2="TEXTURE_DATA"
                        if scn.uvtex:
                            l_s1,l_s2=obj.data.uv_textures[1].data[0].image.name,mtex2
                        else:
                            l_s1,l_s2=obj.active_material.texture_slots[1].texture.image.name,mtex2
                        
                        l_ic1="IMAGE_DATA";a2=mtex2[-3:].upper()+' Image';t2=1

                        if len(l_s2)>30:
                            l_s2="..."+l_s2[(len(l_s2)-24):]
                    else:
                        l_s1,l_s2,l_ic1,ic2,a2,t2="None","None","ERROR","ERROR","None",0
                        box.label(text=" Not Found Lightmap Texture",icon="ERROR")

                    if t1 and t2:
                        col=box.column()
                        col.label(text="Base : "+b_s1+"  -  "+b_s2,icon=b_ic1)
                        col.label(text="Lmap : "+l_s1+"  -  "+l_s2,icon=l_ic1)

                #elif not obj.active_material:
                        #if obj.parent and obj.parent.name != "PITCH" and not obj.name.startswith('SCOREBOARD'):
                            #box.label(text=" Not Found Active Material, add a new Material...",icon="ERROR")

                if obj.parent and obj.parent.name == "CROWD" and obj.name != "SCOREBOARD":
                    if len(obj.data.uv_textures) == 0:
                        box.label(text="  Add a new UV Layer for Crowd Lightmap...",icon="ERROR")

                else:
                    if len(obj.data.uv_textures) >= 2:
                        row = box.row(1)
                        row.alignment='LEFT'
                        row=row.split(0.26)
                        row.label(text="UVmap 1",icon="POTATO")
                        row=row.split(0.34)
                        row.prop(obj.data.uv_textures[0],"name",text="")
                        if obj.parent and obj.parent.name != "PITCH":
                            row.label(text="Base: "+a1,icon=ic1)
                        row = box.row(1)
                        row.alignment='LEFT'
                        row=row.split(0.26)
                        row.label(text="UVmap 2",icon="POTATO")
                        row=row.split(0.34)
                        row.prop(obj.data.uv_textures[1],"name",text="")
                        if obj.parent and obj.parent.name != "PITCH":
                            row.label(text="Lmap: "+a2,icon=ic2)
                        row = box.row()

                        if obj.data.uv_textures[0].name != 'base' or obj.data.uv_textures[1].name != 'lightmap':
                            col=box.split(0.75)
                            col.label(text=" Some UV Layer names is wrong, click --> ",icon="ERROR")
                            col.operator("bse14.operator",text="Set Names").opname='set_uv'
                    else:
                        col=box.split(0.75)
                        col.label(text=" Not Found 2 UV Layers, Add UVs  --> ",icon="ERROR")
                        col.operator("bse14.operator",text="Add UVs").opname='add_uv'
                
                
                box=layout.box()
                box.alignment='CENTER'
                row=box.row()
                row.label("DDS Convert - Export Textures :",icon="INFO")
                #row.prop(scn,"cuda",text="CUDA Accelaration")
                row=box.row()
                
                row.operator("bse14.operator", text="Export DDS Textures", icon="LIBRARY_DATA_DIRECT").opname='convertdds'
                #row.prop(scn,"ac_dds",text="Only Active Obj. Texs")
                row=row.split()
                row.enabled=0
                row.prop(scn,"uvtex",text="Export UV-map Texs")
                row=box.row()
                row.operator("bse14.operator", text="Clean DDS Temp", icon="X").opname='clean_temp'
                row.operator("bse14.operator", text="Clean DataBlock List", icon="X").opname='remove_image'
                row=box.row()
                
                
                box=layout.box()
                box.alignment='CENTER'
                row=box.row()
                row.label("Export Menu :",icon="INFO")
                row.prop(scn,"time_mode",text="Mode")
                #row.prop(scn,"sun",text="Export Sun")
                row=box.row()
                row.prop(scn,"export_path",text="")
                if os.access(scn.export_path,0) == 0:
                    row=box.row()
                    row.label(text=" Not Found Export Folder Path, Select Again...",icon="ERROR")
                row = box.row()
                row.prop(scn,"stadid",text="Stad ID", icon="FACESEL_HLT")
                row.operator("bse14.operator", text="Export Model Files", icon="COPYDOWN").opname='export'
                row = box.row()
                row.prop(scn,"row_space",text="Ver. Row Space")
                row.operator("bse14.operator",text="Export Crowd File",icon="COPYDOWN").opname='exportcrowd'
                row = box.row()
                #if scn.time_mode == 'df': 
                    #row.enabled = 0
                row.prop(scn,"lfx_tex",text="")
                row.operator("bse14.operator", text="Export Light FX ", icon="LAMP_DATA").opname='export_lfx'
                row = box.row()
                
                box=layout.box()
                row=box.row(align=0)
                if scn.cpk_path[-13:] != 'build_cpk.bat':
                    row.enabled = 0
                row.label("Build CPK File :",icon='INFO')
                row.operator("bse14.operator",text="Build CPK",icon="EXPORT").opname="build_cpk"
                row=box.row()
                row.prop(scn,"cpk_path",text="")
                row=box.row()


class MainOperator(bpy.types.Operator):

    bl_idname = "bse14.operator"
    bl_label = "BSE14 Operator"
    opname = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return (context.mode == "OBJECT") and (context.active_object and context.active_object.hide == 0)
    
    def execute(self, context):

        global parentlist

        if self.opname == "set_uv":
            bpy.context.active_object.data.uv_textures[0].name="base"
            bpy.context.active_object.data.uv_textures[1].name="lightmap"
            bpy.context.active_object.data.uv_textures.active_index = 0
            return {'FINISHED'}

        elif self.opname == "add_uv":
            uv_co=len(bpy.context.active_object.data.uv_textures)
            if uv_co == 0:
                bpy.ops.mesh.uv_texture_add('EXEC_SCREEN')
                bpy.ops.mesh.uv_texture_add('EXEC_SCREEN')
            else:
                bpy.ops.mesh.uv_texture_add('EXEC_SCREEN')
            bpy.ops.bse14.operator(opname="set_uv")
            return {'FINISHED'}

        elif self.opname == "switch_uv":
            for m_obj in bpy.context.selected_objects:
                if m_obj.data.uv_textures.active_index == 0:
                    m_obj.data.uv_textures.active_index = 1
                else:
                    m_obj.data.uv_textures.active_index = 0

            return {'FINISHED'}

        elif self.opname == "parents":
            inc_list=[]
            for i in context.scene.objects:
                if i.type == "EMPTY":
                    if i.name in main_list:
                        inc_list.append(i.name)
            for o in main_list:
                if o not in inc_list:
                    bpy.ops.object.add(type='EMPTY',location=(0,0,0))
                    ob = context.active_object
                    for i in range(3):
                        ob.lock_location[i]=1
                        ob.lock_rotation[i]=1
                        ob.lock_scale[i]=1
                    ob.name = o
                    if ob.name in ["L_DOWN","L_RIGHT","L_LEFT","L_UP"]:
                        ob.parent = bpy.data.objects['LIGHTS']

            parentlist = [(ob.name,ob.name,ob.name) for i, ob in enumerate(bpy.context.scene.objects) if ob.type == 'EMPTY' if ob.name in main_list if ob.name != 'LIGHTS']
            parentlist.sort(reverse=0)
            bpy.types.Object.droplist = EnumProperty(name="Parent List", items=parentlist)
            self.report({"INFO"},"Stadium main parts (Parents) has been created...")
            print("")
            return {'FINISHED'}

        elif self.opname == "refresh":
            parentlist = [(ob.name,ob.name,ob.name) for i, ob in enumerate(bpy.context.scene.objects) if ob.type == 'EMPTY' if ob.name in main_list if ob.name not in ['LIGHTS','L_DOWN','L_UP','L_RIGHT','L_LEFT']]
            parentlist.sort(reverse=0)
            bpy.types.Object.droplist = EnumProperty(name="Parent List", items=parentlist)
            for p_ob in bpy.data.objects:
                if p_ob.type == 'MESH' and p_ob.parent and p_ob.parent.name in main_list:
                    p_ob.droplist = p_ob.parent.name

            return {'FINISHED'}

        elif self.opname == "setparent":
            for ob_p in bpy.context.selected_objects:
                ob_p.parent = bpy.data.objects[ob_id]
                ob_p.droplist = bpy.data.objects[ob_id].name
            return {'FINISHED'}

        elif self.opname == "clrparent":
            bpy.ops.object.parent_clear(type='CLEAR')

            return {'FINISHED'}

        elif self.opname == "exportcrowd":
            if len(bpy.data.objects['CROWD'].children) > 0:
                crowd_exp()
                self.report( {"INFO"}, " Crowd Data File and Textures Exported Successfully..." )
                print("")
                return {'FINISHED'}
            else:
                self.report( {"WARNING"}, " No Crowd Objects under CROWD parent !" )
                print("")
                return {'FINISHED'}

        elif self.opname == "clean_temp":
            os.system(REMPATH)
            self.report( {"INFO"}, " Removed all temporary DDS Image Files..." )
            print("")
            return {'FINISHED'}

        elif self.opname == "remove_image":
            for img in bpy.data.images:
                if img.users == 0:
                    bpy.data.images.remove(img)
            for tex in bpy.data.textures:
                if tex.users == 0:
                    bpy.data.textures.remove(tex)

            self.report( {"INFO"}, " Removed Unused Images / Textures from datablock list..." )
            print("")
            return {'FINISHED'}

        elif self.opname == "convertdds":
            if ddsconvert():
                self.report( {"INFO"}, " All Textures Converted and Exported Successfully... " )
                print("")
                return {'FINISHED'}
            else:
                self.report( {"WARNING"}, " Problem when converting textures, check out console screen !!" )
                print("")
                return {'FINISHED'}

        elif self.opname == "export": #!!!!!
            if len(e_texlist) != 0:
                load_objs()
                self.report( {"INFO"}, " Model Files Converted and Exported Successfully... " )
                print("")
                return {'FINISHED'}
            else:
                self.report( {"WARNING"}, " Export All DDS Textures before Export Model Files !!" )
                print("")
                return {'FINISHED'}

        elif self.opname == "set_id": #!!!!!
            id_changer()
            self.report( {"INFO"}, " Changed Stadium ID has been Successfully... " )
            print("")
            return {'FINISHED'}

        elif self.opname == "set_name": #!!!!!
            name_changer()
            self.report( {"INFO"}, " Changed Stadium Name has been Successfully... " )
            print("")
            return {'FINISHED'}

        elif self.opname == "export_lfx": #!!!!!
            light_fx()
            self.report( {"INFO"}, " Light FX Exported has been Successfully... " )
            print("")
            return {'FINISHED'}

        elif self.opname == "set_lfx_side": #!!!!!
            for l_ob in bpy.context.selected_objects:
                if l_ob.type == 'LAMP':
                    l_ob.parent = bpy.data.objects[bpy.context.scene.lit_side]
                    l_ob.fx_e = bpy.context.scene.fxe

            return {'FINISHED'}
        
        elif self.opname == "build_cpk":
            if bpy.context.scene.cpk_path[-13:] == 'build_cpk.bat':
                cpk_folder=os.path.dirname(bpy.context.scene.cpk_path)+"\\"
                os.chdir(cpk_folder)
                os.system('"'+bpy.context.scene.cpk_path+'"') 
                print("")
                self.report( {"INFO"}, " Builded 'stad_test.cpk' File OK..." )
                return {'FINISHED'}
            else:
                print("")
                self.report( {"WARNING"}, " Not Found 'build_cpk.bat' File !!" )
                return {'FINISHED'}



lit_sidelist=[("L_DOWN","DOWN SIDE","DOWN SIDE"),("L_LEFT","LEFT SIDE","LEFT SIDE"),("L_RIGHT","RIGHT SIDE","RIGHT SIDE"),("L_UP","UP SIDE","UP SIDE")]
lfx_tex_list=[("00","00 - tex_star_00.dds","6 streaks"),("01","01 - tex_star_01.dds","6 streaks"),("02","02 - tex_star_02.dds","4 streaks"),("03","03 - tex_star_03.dds","4 streaks"),("04","04 - tex_star_04.dds","6 streaks"),("05","05 - tex_star_05.dds","4 streaks"),("06","06 - tex_star_06.dds","4 streaks")]
shaderlist=[("lmap","LightMap Shader","Default Old Shader"),("ref1","Glossy Shader","New Glossy Shader for similar iron_bars objects.."),("fld2","Field Shader","Ground Shader (only for BASE objects)")]

bpy.types.Object.droplist = EnumProperty(name="Parent List", items=parentlist)
bpy.types.Scene.lit_side = EnumProperty(name="Select Side for Lights",items=lit_sidelist,default="L_DOWN")
bpy.types.Scene.lfx_tex= EnumProperty(name="Texture Type for Light FX",items=lfx_tex_list,default="02")
bpy.types.Scene.fxe = FloatProperty(name="Energy ",min=0.25,max=5.0,subtype='FACTOR',default=2.5)
bpy.types.Object.fx_e = FloatProperty(name="Energy ",min=0.25,max=5.0,subtype='FACTOR',default=2.5)
bpy.types.Scene.rle = FloatProperty(name=" ",step=1,subtype='FACTOR',default=0.0,min=0.0,max=0.3,description="Assign Randomize Light Energy for Selected Lamps..")
bpy.types.Scene.row_space = FloatProperty(name=" ",step=1,subtype='FACTOR',default=5.0,min=0.0,max=10.0,description="Set a value for vertical space of seat rows. (Default: 5.00)")
bpy.types.Scene.cuda = BoolProperty(name=" ",default=1,description="Enable CUDA for fast DDS converting (if GFX Card supports CUDA)..")
bpy.types.Scene.uvtex = BoolProperty(name=" ",default=1,description="Export UV-map Textures instead of Material Textures..")
bpy.types.Scene.ac_dds = BoolProperty(name=" ",default=0,description="Convert only Active Object Textures to DDS Format (for save time)...")
bpy.types.Scene.export_path = StringProperty(name=" ",subtype='DIR_PATH',default="C:\\")
bpy.types.Scene.stadid = StringProperty(description="Stadium ID 'stxxx' (like st002)",default="st002")
bpy.types.Object.tra = BoolProperty(name=" ", default=0, description="Set as transparent object..")
bpy.types.Object.ts = BoolProperty(name=" ", default=0, description="Set as twosided object..")
bpy.types.Object.shader = EnumProperty(name="Set Shader Type", items=shaderlist, default="lmap")
bpy.types.Scene.night = BoolProperty(name=" ",default=0,description="Set Night Mode, if its untick Day Mode is active..")
bpy.types.Scene.sun = BoolProperty(name=" ",default=0,description="Export Sun light Location values..")
bpy.types.Scene.id_path = StringProperty(name=" ",subtype='DIR_PATH',default="C:\\")
bpy.types.Scene.old_id = StringProperty(description="Enter Old Stadium ID")
bpy.types.Scene.new_id = StringProperty(description="Enter New Stadium ID")
bpy.types.Scene.stadname = StringProperty(description="Enter Stadium Name")
bpy.types.Scene.nameid = StringProperty(description="Enter New Stadium ID")
bpy.types.Scene.time_mode = EnumProperty(name="Select Time/Weather",items=[("df","DAY FINE","DAY FINE"),("dr","DAY RAINY","DAY RAINY"),("nf","NIGHT FINE","NIGHT FINE"),("nr","NIGHT RAINY","NIGHT RAINY")],default="df")
bpy.types.Scene.cpk_path = StringProperty(name="CPK Path",subtype='FILE_PATH',default="Select 'build_cpk.bat'   --->")


def register():
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()










