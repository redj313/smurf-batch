import bpy
import pathlib

# Adjust this for where you have the OBJ files.
obj_root = pathlib.Path('Z:/Assets_SMF_3D_Models/Posed_Characters_Series/_ToSort/_SELECTION POUR TEST/temp2')

# Before we start, make sure nothing is selected. The importer will select
# imported objects, which allows us to delete them after rendering.
bpy.ops.object.select_all(action='DESELECT')
render = bpy.context.scene.render
colored_mtl = bpy.data.materials['Mat.Color']
monochrome_mtl = bpy.data.materials['Mat.Monochrome']

frames = [12,25,37,50,62,75,87,100]

for obj_fname in obj_root.glob('*.obj'):
    bpy.ops.wm.obj_import(filepath=str(obj_fname))
    sel = bpy.context.selected_objects
    
    # If the imported object is composed of separated meshes, let's join them
    if len(sel) > 1:
        bpy.ops.object.join()
    
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
    sel[0].data.materials.clear()
    bpy.ops.object.material_slot_add()
    bpy.ops.object.shade_smooth()
    
    # A different material is set depending on whether the object has Vertex Colors or not    
    
    if sel[0].data.attributes.active_color == None:
        sel[0].active_material = monochrome_mtl
    else:
        sel[0].active_material = colored_mtl
    
    
    # Scaling to match the bounding box and placement on the ground
    length = max(sel[0].dimensions)
    print("The longest dimension is "+ str(length))
    scale_fac = 2.0 / length
    bpy.ops.transform.resize(value=(scale_fac, scale_fac, scale_fac))
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    height = sel[0].dimensions[2] / 2
    bpy.context.object.location = 0, 0, height
    
    # Setup the output format for transparent PNG
    bpy.data.objects['Ground'].is_holdout = True
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.image_settings.compression = 85
    bpy.context.scene.render.use_file_extension = True
    
    fcount = 0
    
    # Render of 8 still images
    for f in frames:
        fcount += 1
        bpy.context.scene.frame_current = f
        render.filepath = str(obj_root) + '/' + obj_fname.stem + '_' + str('{num:0{width}}'.format(num=fcount, width=3))
        bpy.ops.render.render(write_still=True)
    
    # Setup and Render of the turntable animation
    render.filepath = ''
    bpy.data.objects['Ground'].is_holdout = False   
    bpy.context.scene.frame_current = 1
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MKV'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    bpy.context.scene.render.use_file_extension = False
    
    render.filepath = str(obj_root) + '/' + obj_fname.stem + '_turn.mkv'
    bpy.ops.render.render(animation=True)

    # Remember which meshes were just imported
    meshes_to_remove = []
    for ob in bpy.context.selected_objects:
        meshes_to_remove.append(ob.data)

    bpy.ops.object.delete()

    # Remove the meshes from memory too
    for mesh in meshes_to_remove:
        bpy.data.meshes.remove(mesh)