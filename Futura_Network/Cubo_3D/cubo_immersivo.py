# Cubo Immersivo — Futura Network
# Scena Blender: cubo 6 x 6 m, alto 3,5 m
# - 3 pareti proiettate (sinistra, fondo, destra)
# - pavimento e soffitto a specchio
# - 3 proiettori su staffa fissati al pannello di legno del tetto
# - lato frontale aperto (ingresso)
#
# Uso: Blender > Scripting > Apri questo file > Run Script.
# Unità: metri. Asse Z verso l'alto. Il cubo è centrato in X/Y sull'origine.

import bpy
import math
from mathutils import Vector

# ---------------------------------------------------------------- misure
L = 6.0          # larghezza (asse X)
P = 6.0          # profondità (asse Y)
H = 3.5          # altezza interna
SP_PARETE = 0.10 # spessore pareti
SP_TETTO = 0.08  # spessore pannello di legno del tetto
SP_BASE = 0.10   # spessore base del pavimento
X0, X1 = -L / 2, L / 2
Y0, Y1 = -P / 2, P / 2   # Y0 = lato aperto (ingresso), Y1 = parete di fondo

# ---------------------------------------------------------------- pulizia
def pulisci_scena():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    for blocco in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for d in list(blocco):
            if d.users == 0:
                blocco.remove(d)

pulisci_scena()
scena = bpy.context.scene
scena.unit_settings.system = 'METRIC'
scena.unit_settings.scale_length = 1.0

def collezione(nome):
    c = bpy.data.collections.new(nome)
    scena.collection.children.link(c)
    return c

C_STRUTTURA = collezione("Struttura")
C_SPECCHI = collezione("Specchi")
C_PROIETTORI = collezione("Proiettori")
C_PROIEZIONI = collezione("Coni_di_proiezione")
C_RIFERIMENTI = collezione("Riferimenti")
C_CAMERE = collezione("Camere_e_luci")

# ---------------------------------------------------------------- materiali
def mat_base(nome, colore, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*colore, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*colore, 1.0)
    return m

def mat_specchio(nome):
    m = mat_base(nome, (0.95, 0.95, 0.97), rough=0.02, metal=1.0)
    m.diffuse_color = (0.75, 0.8, 0.9, 1.0)
    return m

def mat_contenuto(nome, col_a, col_b, scala, fase):
    """Parete proiettata: texture a onde luminosa che simula il contenuto Notch."""
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs["Strength"].default_value = 2.5
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*col_a, 1)
    ramp.color_ramp.elements[1].color = (*col_b, 1)
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = scala
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 4.0
    wave.inputs["Phase Offset"].default_value = fase
    coord = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], emi.inputs["Color"])
    nt.links.new(emi.outputs["Emission"], out.inputs["Surface"])
    m.diffuse_color = (*col_b, 1)
    return m

M_LEGNO = mat_base("Legno_tetto", (0.45, 0.32, 0.2), rough=0.7)
M_STRUTTURA = mat_base("Struttura_esterna", (0.08, 0.08, 0.08), rough=0.8)
M_SPECCHIO = mat_specchio("Specchio")
M_PROIETTORE = mat_base("Proiettore_corpo", (0.05, 0.05, 0.05), rough=0.4)
M_STAFFA = mat_base("Staffa_metallo", (0.3, 0.3, 0.32), rough=0.4, metal=1.0)
M_PERSONA = mat_base("Persona_riferimento", (0.85, 0.85, 0.85), rough=0.9)
M_PARETE_SX = mat_contenuto("Contenuto_parete_sinistra", (0.02, 0.05, 0.25), (0.2, 0.8, 1.0), 0.6, 0.0)
M_PARETE_FONDO = mat_contenuto("Contenuto_parete_fondo", (0.15, 0.02, 0.3), (1.0, 0.35, 0.9), 0.6, 2.0)
M_PARETE_DX = mat_contenuto("Contenuto_parete_destra", (0.02, 0.05, 0.25), (0.2, 0.8, 1.0), 0.6, 4.0)

# ---------------------------------------------------------------- utilità
def box(nome, centro, dimensioni, materiale, coll):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centro)
    ob = bpy.context.active_object
    ob.name = nome
    ob.data.name = nome
    ob.scale = dimensioni
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(materiale)
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)
    return ob

def piano(nome, centro, dim_x, dim_y, materiale, coll, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=centro, rotation=rot)
    ob = bpy.context.active_object
    ob.name = nome
    ob.data.name = nome
    ob.scale = (dim_x, dim_y, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(materiale)
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)
    return ob

# ---------------------------------------------------------------- struttura
# Pareti (spessore verso l'esterno; la faccia interna è sul filo del cubo)
box("Parete_sinistra", (X0 - SP_PARETE / 2, 0, H / 2), (SP_PARETE, P, H), M_STRUTTURA, C_STRUTTURA)
box("Parete_destra", (X1 + SP_PARETE / 2, 0, H / 2), (SP_PARETE, P, H), M_STRUTTURA, C_STRUTTURA)
box("Parete_fondo", (0, Y1 + SP_PARETE / 2, H / 2), (L + 2 * SP_PARETE, SP_PARETE, H), M_STRUTTURA, C_STRUTTURA)

# Superfici proiettate: solo la faccia interna di ogni parete è luminosa
SP = 0.002
piano("Proiezione_parete_sinistra", (X0 + SP, 0, H / 2), H, P, M_PARETE_SX, C_STRUTTURA, rot=(0, math.pi / 2, 0))
piano("Proiezione_parete_destra", (X1 - SP, 0, H / 2), H, P, M_PARETE_DX, C_STRUTTURA, rot=(0, -math.pi / 2, 0))
piano("Proiezione_parete_fondo", (0, Y1 - SP, H / 2), L, H, M_PARETE_FONDO, C_STRUTTURA, rot=(math.pi / 2, 0, 0))

# Base del pavimento e pannello di legno del tetto
box("Base_pavimento", (0, 0, -SP_BASE / 2), (L + 2 * SP_PARETE, P + SP_PARETE, SP_BASE), M_STRUTTURA, C_STRUTTURA)
box("Tetto_pannello_legno", (0, 0, H + SP_TETTO / 2), (L + 2 * SP_PARETE, P + SP_PARETE, SP_TETTO), M_LEGNO, C_STRUTTURA)

# ---------------------------------------------------------------- specchi
OFF = 0.002  # piccolo distacco per evitare sovrapposizioni
piano("Specchio_pavimento", (0, 0, OFF), L, P, M_SPECCHIO, C_SPECCHI)
piano("Specchio_soffitto", (0, 0, H - OFF), L, P, M_SPECCHIO, C_SPECCHI, rot=(math.pi, 0, 0))

# ---------------------------------------------------------------- proiettori
# Ogni proiettore è appeso con una staffa al pannello del tetto, sul lato opposto
# alla parete che proietta, e punta verso il centro di quella parete.
CORPO = (0.45, 0.35, 0.18)   # dimensioni indicative proiettore (m)
Z_PROIETTORE = H - 0.35      # quota del corpo proiettore

proiettori = [
    # nome, posizione, centro della parete bersaglio, angoli della parete bersaglio
    ("Proiettore_parete_sinistra", Vector((X1 - 0.6, 0.0, Z_PROIETTORE)),
     [Vector((X0, Y0, 0)), Vector((X0, Y1, 0)), Vector((X0, Y1, H)), Vector((X0, Y0, H))]),
    ("Proiettore_parete_destra", Vector((X0 + 0.6, 0.0, Z_PROIETTORE)),
     [Vector((X1, Y1, 0)), Vector((X1, Y0, 0)), Vector((X1, Y0, H)), Vector((X1, Y1, H))]),
    ("Proiettore_parete_fondo", Vector((0.0, Y0 + 0.6, Z_PROIETTORE)),
     [Vector((X1, Y1, 0)), Vector((X0, Y1, 0)), Vector((X0, Y1, H)), Vector((X1, Y1, H))]),
]

for nome, pos, angoli in proiettori:
    centro_parete = sum(angoli, Vector()) / 4
    direzione = (centro_parete - pos).normalized()
    rot = direzione.to_track_quat('X', 'Z').to_euler()

    # corpo del proiettore, orientato verso la parete (asse X = obiettivo)
    corpo = box(nome, pos, CORPO, M_PROIETTORE, C_PROIETTORI)
    corpo.rotation_euler = rot

    # obiettivo
    lente_pos = pos + direzione * (CORPO[0] / 2 + 0.03)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.06, location=lente_pos)
    lente = bpy.context.active_object
    lente.name = nome + "_ottica"
    lente.rotation_euler = direzione.to_track_quat('Z', 'Y').to_euler()
    lente.data.materials.append(M_STAFFA)
    for c in lente.users_collection:
        c.objects.unlink(lente)
    C_PROIETTORI.objects.link(lente)

    # staffa: asta verticale dal corpo al pannello del tetto + piastra
    alt_asta = H - (pos.z + CORPO[2] / 2)
    box(nome + "_staffa_asta", (pos.x, pos.y, pos.z + CORPO[2] / 2 + alt_asta / 2),
        (0.05, 0.05, alt_asta), M_STAFFA, C_PROIETTORI)
    box(nome + "_staffa_piastra", (pos.x, pos.y, H - 0.01), (0.3, 0.3, 0.02), M_STAFFA, C_PROIETTORI)

    # cono di proiezione (solo guida in viewport, non va in render)
    me = bpy.data.meshes.new(nome + "_cono")
    verts = [lente_pos] + angoli
    facce = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1)]
    me.from_pydata([tuple(v) for v in verts], [], facce)
    cono = bpy.data.objects.new(nome + "_cono", me)
    cono.display_type = 'WIRE'
    cono.hide_render = True
    C_PROIEZIONI.objects.link(cono)

# proiettori e staffe mascherati: invisibili nei riflessi degli specchi
for ob in C_PROIETTORI.objects:
    ob.visible_glossy = False

# ---------------------------------------------------------------- riferimenti di scala
for i, (x, y) in enumerate([(-0.8, -0.5), (1.0, 0.8)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.75, location=(x, y, OFF + 1.75 / 2))
    pers = bpy.context.active_object
    pers.name = f"Persona_riferimento_{i + 1}"
    pers.data.materials.append(M_PERSONA)
    for c in pers.users_collection:
        c.objects.unlink(pers)
    C_RIFERIMENTI.objects.link(pers)

# ---------------------------------------------------------------- camere
def camera(nome, pos, guarda, lente_mm):
    cam_data = bpy.data.cameras.new(nome)
    cam_data.lens = lente_mm
    cam = bpy.data.objects.new(nome, cam_data)
    cam.location = pos
    cam.rotation_euler = (Vector(guarda) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    C_CAMERE.objects.link(cam)
    return cam

cam_ingresso = camera("Camera_ingresso", (0, Y0 - 4.5, 1.7), (0, 0, 1.6), 24)
camera("Camera_interna", (0, Y0 + 1.0, 1.6), (0, Y1, 1.9), 14)
camera("Camera_esterna_3-4", (X1 + 6, Y0 - 7, 5.5), (0, 0, 1.5), 28)
scena.camera = cam_ingresso

# luce ambiente debole (il cubo si illumina con le proiezioni)
luce_data = bpy.data.lights.new("Luce_ambiente", type='AREA')
luce_data.energy = 150
luce_data.size = 6
luce = bpy.data.objects.new("Luce_ambiente", luce_data)
luce.location = (0, Y0 - 6, 6)
luce.rotation_euler = (Vector((0, 0, 0)) - Vector(luce.location)).to_track_quat('-Z', 'Y').to_euler()
C_CAMERE.objects.link(luce)

# mondo scuro
if scena.world is None:
    scena.world = bpy.data.worlds.new("Mondo")
scena.world.use_nodes = True
sfondo = scena.world.node_tree.nodes.get("Background")
if sfondo:
    sfondo.inputs["Color"].default_value = (0.005, 0.005, 0.008, 1)
    sfondo.inputs["Strength"].default_value = 1.0

# ---------------------------------------------------------------- render
# Cycles per vedere bene il riflesso infinito tra pavimento e soffitto a specchio
scena.render.engine = 'CYCLES'
scena.cycles.samples = 128
scena.cycles.use_denoising = True
scena.cycles.max_bounces = 32
scena.cycles.glossy_bounces = 32
scena.cycles.transparent_max_bounces = 8
scena.render.resolution_x = 1920
scena.render.resolution_y = 1080
try:
    scena.view_settings.view_transform = 'AgX'
except TypeError:
    scena.view_settings.view_transform = 'Filmic'

print("Cubo immersivo creato: 6 x 6 m, h 3,5 m — 3 pareti proiettate, pavimento e soffitto a specchio, 3 proiettori.")

# ---------------------------------------------------------------- salvataggio (da riga di comando)
import sys
if "--" in sys.argv:
    argv = sys.argv[sys.argv.index("--") + 1:]
    if "--salva" in argv:
        percorso = argv[argv.index("--salva") + 1]
        bpy.ops.wm.save_as_mainfile(filepath=percorso)
        print("Salvato:", percorso)
