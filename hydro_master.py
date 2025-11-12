import bpy
import sys
import json
import math
import os

# ------------------------------
# Clear Scene
# ------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ------------------------------
# Read Config
# ------------------------------
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
config_file = argv[0] if argv else None
if not config_file or not os.path.exists(config_file):
    raise ValueError("Config file not provided or not found!")

with open(config_file, "r") as f:
    config = json.load(f)

component = config["component"]
values = config["values"]
export_folder = config["export_folder"]

def num(v):
    """Convert string to int or float"""
    try:
        if "." in str(v):
            return float(v)
        return int(v)
    except:
        return 1

# ------------------------------
# Materials
# ------------------------------
def create_material(name, color, metallic=0.4, roughness=0.3):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

# Generator / Turbine materials
mat_rotor = create_material("RedRotor", (1,0,0,1))
mat_stator = create_material("BlueStator", (0,0.2,1,1))
mat_exciter = create_material("YellowExciter", (1,0.8,0,1))
mat_shaft = create_material("GreyShaft", (0.4,0.4,0.4,1))
mat_base = create_material("GreenBase", (0.2,0.6,0.2,1))

mat_spiral = create_material("SpiralCasing", (0.6,0.2,0.2,1))
mat_vanes = create_material("GuideVanes", (0.2,0.4,1,1))
mat_runner = create_material("Runner", (0.9,0.7,0.2,1))
mat_draft = create_material("DraftTube", (0.3,0.8,0.3,1))

# Intake Structure material
mat_intake = create_material("IntakeConcrete", (0.7,0.7,0.7,1))
mat_water  = create_material("IntakeWater", (0.1,0.35,0.95,0.6), metallic=0.0, roughness=0.07)

# ------------------------------
# Generator
# ------------------------------
def build_generator(v):
    bpy.ops.mesh.primitive_cylinder_add(radius=num(v["base_radius"]), depth=num(v["base_height"]), location=(0,0,0.5))
    base = bpy.context.active_object
    base.data.materials.append(mat_base)

    bpy.ops.mesh.primitive_cylinder_add(radius=num(v["stator_radius"]), depth=num(v["stator_height"]), location=(0,0,2))
    stator = bpy.context.active_object
    stator.data.materials.append(mat_stator)

    bpy.ops.mesh.primitive_cylinder_add(radius=num(v["rotor_radius"]), depth=num(v["rotor_height"]), location=(0,0,2))
    rotor = bpy.context.active_object
    rotor.data.materials.append(mat_rotor)

    bpy.ops.mesh.primitive_cylinder_add(radius=num(v["shaft_radius"]), depth=num(v["shaft_height"]), location=(0,0,0.5))
    shaft = bpy.context.active_object
    shaft.data.materials.append(mat_shaft)

    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=0.5, location=(0,0,3.5))
    exciter = bpy.context.active_object
    exciter.data.materials.append(mat_exciter)

    # Animation
    for obj in [rotor, shaft]:
        obj.rotation_mode = 'XYZ'
        obj.keyframe_insert(data_path="rotation_euler", frame=1)
        obj.rotation_euler[2] = math.radians(360)
        obj.keyframe_insert(data_path="rotation_euler", frame=100)
        obj.animation_data.action.fcurves[0].modifiers.new(type='CYCLES')

# ------------------------------
# Turbine
# ------------------------------
def build_turbine(v):
    bpy.ops.mesh.primitive_torus_add(major_radius=num(v["spiral_major_radius"]), minor_radius=num(v["spiral_minor_radius"]), location=(0,0,1))
    spiral = bpy.context.active_object
    spiral.data.materials.append(mat_spiral)

    # Stay vanes
    for i in range(num(v["stay_vane_count"])):
        angle = math.radians(i * (360/num(v["stay_vane_count"])))
        x = 2.5 * math.cos(angle)
        y = 2.5 * math.sin(angle)
        bpy.ops.mesh.primitive_cube_add(size=0.3, location=(x,y,1.5))
        vane = bpy.context.active_object
        vane.scale = (0.2,1,1.5)
        vane.rotation_euler[2] = angle
        vane.data.materials.append(mat_vanes)

    # Guide vanes
    for i in range(num(v["guide_vane_count"])):
        angle = math.radians(i * (360/num(v["guide_vane_count"])))
        x = 1.8 * math.cos(angle)
        y = 1.8 * math.sin(angle)
        bpy.ops.mesh.primitive_cube_add(size=0.25, location=(x,y,1.5))
        guide = bpy.context.active_object
        guide.scale = (0.15,0.8,1)
        guide.rotation_euler[2] = angle
        guide.data.materials.append(mat_vanes)

    # Runner
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=num(v["runner_radius"]), depth=num(v["runner_depth"]), location=(0,0,1.5))
    runner = bpy.context.active_object
    runner.data.materials.append(mat_runner)

    # Blades
    for i in range(num(v["blade_count"])):
        angle = math.radians(i * (360/num(v["blade_count"])))
        x = 0.7 * math.cos(angle)
        y = 0.7 * math.sin(angle)
        bpy.ops.mesh.primitive_cylinder_add(radius=num(v["blade_radius"]), depth=num(v["blade_depth"]), location=(x,y,1.5))
        blade = bpy.context.active_object
        blade.rotation_euler[2] = angle
        blade.data.materials.append(mat_runner)
        blade.parent = runner

    bpy.ops.mesh.primitive_cylinder_add(radius=num(v["shaft_radius"]), depth=num(v["shaft_height"]), location=(0,0,0.5))
    shaft = bpy.context.active_object
    shaft.data.materials.append(mat_shaft)
    runner.parent = shaft

    bpy.ops.mesh.primitive_cone_add(radius1=num(v["draft_radius1"]), radius2=num(v["draft_radius2"]), depth=num(v["draft_depth"]), location=(0,0,-0.5))
    draft = bpy.context.active_object
    draft.data.materials.append(mat_draft)

    # Shaft Animation
    shaft.rotation_mode = 'XYZ'
    shaft.keyframe_insert(data_path="rotation_euler", frame=1)
    shaft.rotation_euler[2] = math.radians(360)
    shaft.keyframe_insert(data_path="rotation_euler", frame=100)
    shaft.animation_data.action.fcurves[0].modifiers.new(type='CYCLES')

# ------------------------------
# Intake Structure (fully dynamic)
# ------------------------------
def build_intake_structure(v):
    BAY_COUNT = num(v["bay_count"])
    BAY_WIDTH = num(v["bay_width"])
    PIER_THICK = num(v["pier_thick"])
    INTAKE_HEIGHT = num(v["intake_height"])
    SILL_ELEV = num(v["sill_elev"])
    DECK_ELEV = num(v["deck_elev"])
    FACE_THICK = num(v["face_thick"])
    TRASH_BAR_THICK = num(v["trash_bar_thick"])
    TRASH_BAR_GAP = num(v["trash_bar_gap"])
    TRASH_BAR_ROWS = num(v["trash_bar_rows"])
    GATE_THICK = num(v["gate_thick"])
    GATE_CLEAR_TOP = num(v["gate_clear_top"])
    TUNNEL_DIAM = num(v["tunnel_diam"])
    TUNNEL_LEN = num(v["tunnel_len"])
    FLOOR_ELEV = num(v["floor_elev"])
    SIDE_WALL_EXTRA = num(v["side_wall_extra"])
    CRANE_GAUGE = num(v["crane_gauge"])
    CRANE_SPAN_XPAD = num(v["crane_span_xpad"])

    # Piers
    for i in range(BAY_COUNT + 1):
        x = i * BAY_WIDTH
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x,0,INTAKE_HEIGHT/2))
        pier = bpy.context.active_object
        pier.scale = (PIER_THICK/2, (BAY_WIDTH+SIDE_WALL_EXTRA)/2, INTAKE_HEIGHT/2)
        pier.data.materials.append(mat_intake)

    # Deck
    bpy.ops.mesh.primitive_cube_add(size=1, location=(BAY_COUNT*BAY_WIDTH/2,0,DECK_ELEV-FACE_THICK/2))
    deck = bpy.context.active_object
    deck.scale = (BAY_COUNT*BAY_WIDTH/2, (BAY_WIDTH+SIDE_WALL_EXTRA)/2, FACE_THICK/2)
    deck.data.materials.append(mat_intake)

    # Trash Bars
    for i in range(BAY_COUNT):
        x_start = i*BAY_WIDTH
        for row in range(TRASH_BAR_ROWS):
            z = SILL_ELEV + row*(TRASH_BAR_THICK+TRASH_BAR_GAP)
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x_start + BAY_WIDTH/2, 0, z))
            bar = bpy.context.active_object
            bar.scale = (BAY_WIDTH/2, TRASH_BAR_THICK/2, TRASH_BAR_THICK/2)
            bar.data.materials.append(mat_intake)

    # Gates
    for i in range(BAY_COUNT):
        x = i*BAY_WIDTH + BAY_WIDTH/2
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x,0,SILL_ELEV + (INTAKE_HEIGHT-SILL_ELEV)/2))
        gate = bpy.context.active_object
        gate.scale = (BAY_WIDTH/2, GATE_THICK/2, (INTAKE_HEIGHT-SILL_ELEV)/2)
        gate.data.materials.append(mat_intake)
        gate.keyframe_insert(data_path="location", frame=1)
        gate.location[2] += GATE_CLEAR_TOP
        gate.keyframe_insert(data_path="location", frame=50)
        gate.animation_data.action.fcurves[0].modifiers.new(type='CYCLES')

    # Tunnels
    for i in range(BAY_COUNT):
        x = i*BAY_WIDTH + BAY_WIDTH/2
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=TUNNEL_DIAM/2, depth=TUNNEL_LEN, location=(x, -(TUNNEL_LEN/2 + PIER_THICK), FLOOR_ELEV + TUNNEL_DIAM/2))
        tunnel = bpy.context.active_object
        tunnel.rotation_euler[0] = math.radians(90)
        tunnel.data.materials.append(mat_intake)

    # Crane
    bpy.ops.mesh.primitive_cube_add(size=1, location=(BAY_COUNT*BAY_WIDTH/2,0,DECK_ELEV + CRANE_GAUGE/2))
    crane = bpy.context.active_object
    crane.scale = (BAY_COUNT*BAY_WIDTH/2 + CRANE_SPAN_XPAD, CRANE_GAUGE/2, CRANE_GAUGE/2)
    crane.data.materials.append(mat_intake)
    crane.keyframe_insert(data_path="location", frame=1)
    crane.location[0] -= (BAY_COUNT*BAY_WIDTH/4)
    crane.keyframe_insert(data_path="location", frame=100)
    crane.animation_data.action.fcurves[0].modifiers.new(type='CYCLES')

    # Camera + Light
    cam_x = BAY_COUNT*BAY_WIDTH
    cam_y = -BAY_COUNT*BAY_WIDTH
    cam_z = DECK_ELEV*1.2
    bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z), rotation=(math.radians(65),0,math.radians(45)))
    bpy.context.scene.camera = bpy.context.active_object

    light_x = BAY_COUNT*BAY_WIDTH/2
    light_y = -BAY_COUNT*BAY_WIDTH/2
    light_z = DECK_ELEV*1.5
    bpy.ops.object.light_add(type='AREA', location=(light_x, light_y, light_z))
    bpy.context.active_object.data.energy = 1000

    print("✅ Intake Structure built and animated successfully!")

# ------------------------------
# Run builder
# ------------------------------
if component == "generator":
    build_generator(values)
elif component == "turbine":
    build_turbine(values)
elif component == "intake":
    build_intake_structure(values)

# Export
export_path = os.path.join(export_folder, f"{component}.blend")
bpy.ops.wm.save_as_mainfile(filepath=export_path)
print(f"✅ {component.capitalize()} model created and animated successfully!")
