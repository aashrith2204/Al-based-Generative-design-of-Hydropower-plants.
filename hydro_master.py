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

def build_intake_structure(v):
    """
    Dynamic intake builder. Reads parameters from v (dict of values)
    and builds the intake structure. Falls back to defaults if keys missing.
    """

    import math
    from mathutils import Vector
    import bpy

    RAD = math.radians

    # helper to get numeric param with fallback
    def par(key, default):
        return num(v.get(key, default))

    # Defaults (match your static script)
    BAY_COUNT        = int(par("bay_count", 7))
    BAY_WIDTH        = par("bay_width", 9.0)
    PIER_THICK       = par("pier_thick", 3.0)
    INTAKE_HEIGHT    = par("intake_height", 22.0)
    SILL_ELEV        = par("sill_elev", 4.0)
    DECK_ELEV        = par("deck_elev", 32.0)
    FACE_THICK       = par("face_thick", 10.0)
    TRASH_BAR_THICK  = par("trash_bar_thick", 0.20)
    TRASH_BAR_GAP    = par("trash_bar_gap", 0.60)
    TRASH_BAR_ROWS   = int(par("trash_bar_rows", 10))
    GATE_THICK       = par("gate_thick", 0.8)
    GATE_CLEAR_TOP   = par("gate_clear_top", 2.0)
    TUNNEL_DIAM      = par("tunnel_diam", 6.0)
    TUNNEL_LEN       = par("tunnel_len", 45.0)
    FLOOR_ELEV       = par("floor_elev", 0.0)
    WATER_ELEV_UP    = par("water_elev_up", 20.0)
    SIDE_WALL_EXTRA  = par("side_wall_extra", 10.0)
    STRUCT_DEPTH     = par("struct_depth", 30.0)
    CRANE_GAUGE      = par("crane_gauge", 18.0)
    CRANE_SPAN_XPAD  = par("crane_span_xpad", 8.0)

    # animation frames (optional incoming keys)
    FRAME_START      = int(par("frame_start", 1))
    FRAME_GATE_UP    = int(par("frame_gate_up", 60))
    FRAME_TROLLEY_1  = int(par("frame_trolley_1", 1))
    FRAME_TROLLEY_2  = int(par("frame_trolley_2", 180))
    FRAME_END        = int(par("frame_end", 240))

    # derived
    BAY_SPAN = BAY_WIDTH + PIER_THICK
    TOTAL_WIDTH = BAY_COUNT * BAY_WIDTH + (BAY_COUNT + 1) * PIER_THICK
    X0 = -TOTAL_WIDTH/2.0

    # Use existing create_material if available, otherwise fallback to a local, simple maker
    try:
        # create_material(name, color, metallic=0.4, roughness=0.3)
        MAT_CONCRETE = create_material("Intake_Concrete", (0.70,0.70,0.72,1), metallic=0.0, roughness=0.85)
        MAT_STEEL    = create_material("Intake_Steel", (0.15,0.30,0.75,1), metallic=0.6, roughness=0.35)
        MAT_RACK     = create_material("Intake_Rack", (0.12,0.12,0.12,1), metallic=0.2, roughness=0.6)
        MAT_WATER    = create_material("Intake_Water", (0.10,0.35,0.95,0.6), metallic=0.0, roughness=0.07)
        MAT_DECK     = create_material("Intake_Deck", (0.22,0.22,0.22,1), metallic=0.0, roughness=0.9)
        MAT_CRANE    = create_material("Intake_Crane", (0.95,0.75,0.10,1), metallic=0.1, roughness=0.4)
        MAT_SOIL     = create_material("Intake_Soil", (0.40,0.35,0.30,1), metallic=0.0, roughness=0.95)
        # set alpha for water
        if MAT_WATER.use_nodes:
            try:
                bsdf = MAT_WATER.node_tree.nodes["Principled BSDF"]
                bsdf.inputs["Alpha"].default_value = 0.55
                MAT_WATER.blend_method = 'BLEND'
            except Exception:
                pass
    except Exception:
        # fallback simple materials
        def simple_mat(name, rgba):
            m = bpy.data.materials.new(name)
            m.use_nodes = True
            try:
                bsdf = m.node_tree.nodes["Principled BSDF"]
                bsdf.inputs["Base Color"].default_value = rgba
                bsdf.inputs["Roughness"].default_value = 0.6
            except Exception:
                pass
            return m
        MAT_CONCRETE = simple_mat("IntakeConcrete", (0.7,0.7,0.7,1))
        MAT_STEEL    = simple_mat("IntakeSteel", (0.15,0.3,0.75,1))
        MAT_RACK     = simple_mat("IntakeRack", (0.12,0.12,0.12,1))
        MAT_WATER    = simple_mat("IntakeWater", (0.1,0.35,0.95,0.55))
        MAT_DECK     = simple_mat("IntakeDeck", (0.22,0.22,0.22,1))
        MAT_CRANE    = simple_mat("IntakeCrane", (0.95,0.75,0.10,1))
        MAT_SOIL     = simple_mat("IntakeSoil", (0.4,0.35,0.3,1))

    # helpers (local to avoid relying on other helpers)
    def make_cube(name, size, loc, rot=(0,0,0), mat=None):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
        o = bpy.context.active_object
        o.name = name
        o.scale = (size[0]/2, size[1]/2, size[2]/2)
        if mat:
            try:
                o.data.materials.append(mat)
            except:
                pass
        return o

    def make_plane(name, size_x, size_y, loc=(0,0,0), rot=(0,0,0), mat=None):
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
        o = bpy.context.active_object
        o.name = name
        o.scale = (size_x/2, size_y/2, 1)
        if mat:
            try:
                o.data.materials.append(mat)
            except:
                pass
        return o

    def make_cyl(name, radius, depth, loc=(0,0,0), rot=(0,0,0), mat=None, verts=64):
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
        o = bpy.context.active_object
        o.name = name
        if mat:
            try:
                o.data.materials.append(mat)
            except:
                pass
        return o

    def shade_smooth(obj):
        if obj and obj.type == 'MESH':
            try:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.shade_smooth()
            except:
                pass

    # Clear any pre-existing objects in case this is called standalone
    # (the top of hydro_master.py already clears scene before calling builders,
    #  but keep this safe — do not use select_all here if you want to preserve others)
    # bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

    # =========================
    # ground & upstream water
    ground = make_plane("Ground", TOTAL_WIDTH + 2*SIDE_WALL_EXTRA + 80, 200, (0, -10, FLOOR_ELEV-0.05), (0,0,0), MAT_SOIL)
    up_water = make_plane("UpstreamWater", TOTAL_WIDTH + 2*SIDE_WALL_EXTRA + 40, 160, (0, -30, WATER_ELEV_UP), (0,0,0), MAT_WATER)
    try:
        wave = up_water.modifiers.new(name="Wave", type='WAVE')
        wave.height, wave.width, wave.speed = 0.15, 8.0, 0.1
    except:
        pass

    # Upstream face & deck & side walls & floor
    face = make_cube("UpstreamFace",
                     (TOTAL_WIDTH + 2*SIDE_WALL_EXTRA, FACE_THICK, DECK_ELEV - FLOOR_ELEV),
                     (0, -FACE_THICK/2, (DECK_ELEV + FLOOR_ELEV)/2),
                     mat=MAT_CONCRETE)
    shade_smooth(face)

    deck = make_cube("Deck",
                     (TOTAL_WIDTH + 2*SIDE_WALL_EXTRA, 8.0, 2.0),
                     (0, 2.0, DECK_ELEV + 1.0),
                     mat=MAT_DECK)

    side_L = make_cube("SideWall_L",
                       (PIER_THICK, STRUCT_DEPTH, DECK_ELEV - FLOOR_ELEV),
                       (X0 - PIER_THICK/2, STRUCT_DEPTH/2 - FACE_THICK/2, (DECK_ELEV + FLOOR_ELEV)/2),
                       mat=MAT_CONCRETE)
    side_R = make_cube("SideWall_R",
                       (PIER_THICK, STRUCT_DEPTH, DECK_ELEV - FLOOR_ELEV),
                       (-X0 + PIER_THICK/2, STRUCT_DEPTH/2 - FACE_THICK/2, (DECK_ELEV + FLOOR_ELEV)/2),
                       mat=MAT_CONCRETE)

    floor = make_cube("Floor",
                      (TOTAL_WIDTH + 2*SIDE_WALL_EXTRA, STRUCT_DEPTH, 2.0),
                      (0, STRUCT_DEPTH/2 - FACE_THICK/2, FLOOR_ELEV - 1.0),
                      mat=MAT_CONCRETE)

    # =========================
    # Piers and bay frames
    piers = []
    for i in range(BAY_COUNT+1):
        x = X0 + i*BAY_SPAN
        pier = make_cube(f"Pier_{i}",
                         (PIER_THICK, FACE_THICK+1.0, DECK_ELEV - FLOOR_ELEV),
                         (x + PIER_THICK/2, 0.0, (DECK_ELEV + FLOOR_ELEV)/2),
                         mat=MAT_CONCRETE)
        piers.append(pier)
        shade_smooth(pier)

    reveal_depth = 0.7
    bay_frames = []
    for b in range(BAY_COUNT):
        cx = X0 + PIER_THICK + BAY_WIDTH/2 + b*BAY_SPAN
        frame = make_cube(f"BayFrame_{b}",
                          (BAY_WIDTH*0.98, reveal_depth, INTAKE_HEIGHT + 1.0),
                          (cx, -reveal_depth/2 - 0.1, SILL_ELEV + (INTAKE_HEIGHT+1.0)/2),
                          mat=MAT_CONCRETE)
        bay_frames.append(frame)

    # =========================
    # Trash racks
    racks = []
    for b in range(BAY_COUNT):
        cx = X0 + PIER_THICK + BAY_WIDTH/2 + b*BAY_SPAN
        n_bars = max(1, int(BAY_WIDTH // (TRASH_BAR_THICK + TRASH_BAR_GAP)))
        start_x = cx - BAY_WIDTH/2 + TRASH_BAR_GAP/2
        for i in range(n_bars):
            xb = start_x + i*(TRASH_BAR_THICK + TRASH_BAR_GAP)
            bar = make_cube(f"RackV_{b}_{i}",
                            (TRASH_BAR_THICK, 0.6, INTAKE_HEIGHT),
                            (xb, 0.3, SILL_ELEV + INTAKE_HEIGHT/2),
                            mat=MAT_RACK)
            racks.append(bar)
        for j in range(TRASH_BAR_ROWS):
            z = SILL_ELEV + (j+0.5) * (INTAKE_HEIGHT / TRASH_BAR_ROWS)
            beam = make_cube(f"RackH_{b}_{j}",
                             (BAY_WIDTH, 0.4, 0.25),
                             (cx, 0.45, z),
                             mat=MAT_RACK)
            racks.append(beam)

    # =========================
    # Gates and guides
    gates = []
    gate_guides = []
    for b in range(BAY_COUNT):
        cx = X0 + PIER_THICK + BAY_WIDTH/2 + b*BAY_SPAN
        gate = make_cube(f"Gate_{b}",
                         (BAY_WIDTH*0.98, GATE_THICK, INTAKE_HEIGHT+0.5),
                         (cx, -0.2, SILL_ELEV + (INTAKE_HEIGHT+0.5)/2),
                         mat=MAT_STEEL)
        gates.append(gate)
        gL = make_cube(f"GuideL_{b}", (0.45, 0.8, INTAKE_HEIGHT+4.0),
                       (cx - BAY_WIDTH/2 - 0.25, 0.0, SILL_ELEV + (INTAKE_HEIGHT+4.0)/2), mat=MAT_STEEL)
        gR = make_cube(f"GuideR_{b}", (0.45, 0.8, INTAKE_HEIGHT+4.0),
                       (cx + BAY_WIDTH/2 + 0.25, 0.0, SILL_ELEV + (INTAKE_HEIGHT+4.0)/2), mat=MAT_STEEL)
        gate_guides += [gL, gR]

    # =========================
    # Tunnels
    tunnels = []
    for b in range(BAY_COUNT):
        cx = X0 + PIER_THICK + BAY_WIDTH/2 + b*BAY_SPAN
        angle = RAD(-3.0)
        z_center = SILL_ELEV + TUNNEL_DIAM/2 - 1.0
        tunnel = make_cyl(f"Tunnel_{b}", TUNNEL_DIAM/2, TUNNEL_LEN,
                          loc=(cx, STRUCT_DEPTH/2 + TUNNEL_LEN/2 - FACE_THICK/2, z_center),
                          rot=(angle, 0, 0),
                          mat=MAT_CONCRETE)
        tunnels.append(tunnel)

    # =========================
    # Flows
    flows = []
    for b in range(BAY_COUNT):
        cx = X0 + PIER_THICK + BAY_WIDTH/2 + b*BAY_SPAN
        flow = make_plane(f"Flow_{b}", BAY_WIDTH*0.9, 3.5,
                          loc=(cx, -1.8, SILL_ELEV + INTAKE_HEIGHT*0.5),
                          rot=(RAD(90), 0, 0),
                          mat=MAT_WATER)
        # flatten thickness visually
        try:
            flow.scale.z = 0.02
        except:
            pass
        flows.append(flow)

    # =========================
    # Gantry crane
    rail_len = TOTAL_WIDTH + 2*CRANE_SPAN_XPAD
    rail_y = 3.0
    rail_z = DECK_ELEV + 3.0

    rail_L = make_cube("CraneRail_L", (rail_len, 0.40, 0.40),
                       (-CRANE_SPAN_XPAD/2, rail_y, rail_z), mat=MAT_CRANE)
    rail_R = make_cube("CraneRail_R", (rail_len, 0.40, 0.40),
                       (-CRANE_SPAN_XPAD/2, rail_y + CRANE_GAUGE, rail_z), mat=MAT_CRANE)

    end_L = make_cube("CraneEnd_L", (1.0, CRANE_GAUGE+0.8, 4.0),
                      (X0 - 4.0, rail_y + CRANE_GAUGE/2, rail_z + 2.0), mat=MAT_CRANE)
    end_R = make_cube("CraneEnd_R", (1.0, CRANE_GAUGE+0.8, 4.0),
                      (-X0 + 4.0, rail_y + CRANE_GAUGE/2, rail_z + 2.0), mat=MAT_CRANE)

    bridge = make_cube("CraneBridge", (TOTAL_WIDTH + 6.0, 0.8, 1.0),
                       (0, rail_y + CRANE_GAUGE/2, rail_z + 1.0), mat=MAT_CRANE)

    trolley = make_cube("Trolley", (2.4, 0.8, 1.0),
                        (X0 + 4.0, rail_y + CRANE_GAUGE/2, rail_z + 0.6), mat=MAT_CRANE)

    hook_rope = make_cyl("HookRope", 0.08, DECK_ELEV - (rail_z - 0.6),
                         loc=(trolley.location[0], trolley.location[1], (rail_z + 0.6 + DECK_ELEV)/2 - 2.0),
                         rot=(RAD(90), 0, 0), mat=MAT_STEEL, verts=24)
    hook_spreader = make_cube("HookSpreader", (1.2, 0.4, 0.3),
                              (trolley.location[0], trolley.location[1], DECK_ELEV - 1.5), mat=MAT_STEEL)

    hook_rope.parent = trolley
    hook_spreader.parent = trolley

    # outer shell & parapet
    outer_L = make_cube("OuterShell_L",
                        (PIER_THICK*1.2, 80.0, DECK_ELEV - FLOOR_ELEV + 6.0),
                        (X0 - SIDE_WALL_EXTRA, 10.0, (DECK_ELEV + FLOOR_ELEV)/2 + 3.0),
                        mat=MAT_CONCRETE)
    outer_R = make_cube("OuterShell_R",
                        (PIER_THICK*1.2, 80.0, DECK_ELEV - FLOOR_ELEV + 6.0),
                        (-X0 + SIDE_WALL_EXTRA, 10.0, (DECK_ELEV + FLOOR_ELEV)/2 + 3.0),
                        mat=MAT_CONCRETE)

    parapet = make_cube("UpParapet", (TOTAL_WIDTH + 2*SIDE_WALL_EXTRA, 1.2, 1.0),
                        (0, -FACE_THICK - 0.6, DECK_ELEV + 0.5), mat=MAT_CONCRETE)

    # =========================
    # Animations
    for gate in gates:
        try:
            gate.keyframe_insert(data_path="location", frame=FRAME_START)
            gate.location[2] = SILL_ELEV + (INTAKE_HEIGHT+0.5)/2 + INTAKE_HEIGHT + GATE_CLEAR_TOP
            gate.keyframe_insert(data_path="location", frame=FRAME_GATE_UP)
        except:
            pass

    try:
        trolley.keyframe_insert(data_path="location", frame=FRAME_TROLLEY_1)
        trolley.location[0] = -X0 - 4.0
        trolley.keyframe_insert(data_path="location", frame=FRAME_TROLLEY_2)
    except:
        pass

    for flow in flows:
        try:
            y0, z0 = flow.location[1], flow.location[2]
            flow.keyframe_insert(data_path="location", frame=FRAME_START)
            flow.location[1] = y0 + 1.2
            flow.location[2] = z0 - 0.8
            flow.keyframe_insert(data_path="location", frame=FRAME_GATE_UP + 20)
        except:
            pass

    # camera & lights (frame scene)
    try:
        # compute bounding box and position camera to frame scene
        mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
        if mesh_objs:
            mins = Vector((1e9,1e9,1e9))
            maxs = Vector((-1e9,-1e9,-1e9))
            for o in mesh_objs:
                for v in o.bound_box:
                    v_world = o.matrix_world @ Vector(v)
                    mins.x = min(mins.x, v_world.x)
                    mins.y = min(mins.y, v_world.y)
                    mins.z = min(mins.z, v_world.z)
                    maxs.x = max(maxs.x, v_world.x)
                    maxs.y = max(maxs.y, v_world.y)
                    maxs.z = max(maxs.z, v_world.z)
            center = (mins + maxs) / 2.0
            bbox_size = maxs - mins
            max_dim = max(bbox_size.x, bbox_size.y, bbox_size.z, 0.1)
            cam_distance = max_dim * 3.0 if max_dim < 30 else max_dim * 1.5
            cam_location = center + Vector((0.0, -cam_distance, max_dim * 1.2))
            bpy.ops.object.camera_add(location=cam_location, rotation=(RAD(72),0,0))
            cam = bpy.context.active_object
            bpy.context.scene.camera = cam
        else:
            # fallback to static camera similar to original script
            bpy.ops.object.camera_add(location=(0, -95, 55), rotation=(RAD(72), 0, 0))
            cam = bpy.context.active_object
            bpy.context.scene.camera = cam
    except:
        try:
            bpy.ops.object.camera_add(location=(0, -95, 55), rotation=(RAD(72), 0, 0))
            bpy.context.scene.camera = bpy.context.active_object
        except:
            pass

    try:
        bpy.ops.object.light_add(type='SUN', location=(0, -70, 150))
        sun = bpy.context.active_object
        sun.rotation_euler = (RAD(50), RAD(20), 0)
    except:
        pass

    try:
        bpy.ops.object.light_add(type='AREA', location=(0, 20, 40))
        fill = bpy.context.active_object
        try:
            fill.data.energy = 1200
        except:
            pass
    except:
        pass

    # smooth shading
    for o in bpy.data.objects:
        if o.type == 'MESH':
            shade_smooth(o)

    # timeline
    try:
        bpy.context.scene.frame_start = FRAME_START
        bpy.context.scene.frame_end   = FRAME_END
    except:
        pass

    print("✅ Dynamic Intake built using passed parameters.")

    




# ------------------------------
# Run builder
# ------------------------------
if component == "generator":
    build_generator(values)
elif component == "turbine":
    build_turbine(values)
elif component in ("intake", "intake_structure"):
    build_intake_structure(values)
else:
    print(f"⚠️ Unknown component '{component}' — no builder executed.")


# Export
export_path = os.path.join(export_folder, f"{component}.blend")
bpy.ops.wm.save_as_mainfile(filepath=export_path)
print(f"✅ {component.capitalize()} model created and animated successfully!")
