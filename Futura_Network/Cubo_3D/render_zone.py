# Render delle zone di proiezione e delle zone d'ombra, per confrontare le ottiche.
# Costruisce la scena con l'ottica scelta, poi:
#   - pareti, pavimento e soffitto diventano bianco/grigio opaco (niente specchi, niente contenuto);
#   - ogni proiettore diventa una luce con il tronco di proiezione esatto, in un colore proprio
#     (sinistra = arancio, fondo = verde, destra = azzurro): le sovrapposizioni si vedono come
#     mescolanza di colori, le ombre (persone, altri proiettori, staffe) come zone scure;
#   - una leggera foschia rende visibili i fasci nell'aria.
# Uso:
#   blender --background --factory-startup --python render_zone.py -- --ottica 0.5 [--senza-porta]
# Escono: zone_ottica_<rt>_interna.png e zone_ottica_<rt>_pianta.png nella cartella dello script.

import bpy, os, sys, math
from mathutils import Vector

cartella = os.path.dirname(os.path.abspath(__file__))
exec(compile(open(os.path.join(cartella, "cubo_immersivo.py")).read(), "cubo_immersivo.py", "exec"))

scena = bpy.context.scene
COLORI = {"Proiettore_parete_sinistra": (1.0, 0.45, 0.08),
          "Proiettore_parete_fondo": (0.15, 1.0, 0.25),
          "Proiettore_parete_destra": (0.1, 0.45, 1.0),
          "Proiettore_parete_ingresso": (1.0, 0.15, 0.75)}

def opaco(nome, grigio):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (grigio, grigio, grigio, 1)
    b.inputs["Roughness"].default_value = 0.9
    return m

M_SCHERMO = opaco("Zona_parete_bianca", 0.8)
M_PIANO = opaco("Zona_pavimento_grigio", 0.45)
for ob in bpy.data.objects:
    if ob.type != 'MESH':
        continue
    if ob.name.startswith("Proiezione_parete"):
        ob.data.materials[0] = M_SCHERMO
    elif ob.name.startswith("Specchio_"):
        ob.data.materials[0] = M_PIANO

# fasci accesi, colorati per proiettore
for nome, col in COLORI.items():
    luce = bpy.data.objects.get(nome + "_fascio")
    if luce is None:
        continue
    luce.hide_render = False
    luce.data.node_tree.nodes["Emission"].inputs["Color"].default_value = (*col, 1)

# niente luce ambiente: si vede solo ciò che i proiettori illuminano
bpy.data.objects["Luce_ambiente"].hide_render = True
scena.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0

# foschia leggera dentro il cubo per vedere i fasci
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, H / 2))
nebbia = bpy.context.active_object
nebbia.name = "Foschia_fasci"
nebbia.scale = (L - 0.02, P - 0.02, H - 0.02)
mn = bpy.data.materials.new("Foschia")
mn.use_nodes = True
nt = mn.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputMaterial")
vol = nt.nodes.new("ShaderNodeVolumeScatter")
vol.inputs["Density"].default_value = 0.02
nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
nebbia.data.materials.append(mn)
nebbia.visible_shadow = False

# camere: vista interna grandangolare e pianta dall'alto (tetto e soffitto nascosti)
def camera(nome, pos, guarda, lente_mm=None, orto=None):
    cd = bpy.data.cameras.new(nome)
    if orto:
        cd.type = 'ORTHO'
        cd.ortho_scale = orto
    else:
        cd.lens = lente_mm
    cam = bpy.data.objects.new(nome, cd)
    cam.location = pos
    cam.rotation_euler = (Vector(guarda) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    scena.collection.objects.link(cam)
    return cam

cam_interna = camera("Camera_zone_interna", (X1 - 0.4, Y0 + 0.4, 1.7), (X0 + 1.2, Y1 - 1.0, 1.5), lente_mm=12)
cam_porta = camera("Camera_zone_verso_porta", (X0 + 0.4, Y1 - 0.4, 1.7), (X1 - 1.2, Y0 + 1.0, 1.5), lente_mm=12)
cam_pianta = camera("Camera_zone_pianta", (0, 0.6999, 25), (0, 0.7, 0), orto=12.5)
da_nascondere_in_pianta = [o for o in bpy.data.objects
                           if o.name.startswith(("Tetto_", "Specchio_soffitto", "Fondo_soffitto"))]

scena.cycles.samples = int(os.environ.get("CAMPIONI_ZONE", "256"))
scena.cycles.volume_bounces = 1
scena.render.resolution_x, scena.render.resolution_y = 1920, 1080
scena.render.resolution_percentage = int(os.environ.get("PERCENTUALE", "100"))

# GPU se disponibile
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for tipo in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            if any(d.type == tipo for d in prefs.devices):
                for d in prefs.devices:
                    d.use = True
                scena.cycles.device = "GPU"
                print("Render su GPU:", tipo)
                break
        except Exception:
            continue
except Exception as e:
    print("GPU non attivata, uso CPU:", e)

# etichetta sul render: ottica e distanza di tiro
r = scena.render
r.use_stamp = True
for k in ("date", "time", "render_time", "frame", "frame_range", "memory", "hostname", "camera",
          "lens", "scene", "marker", "filename", "sequencer_strip", "peak_memory"):
    if hasattr(r, "use_stamp_" + k):
        setattr(r, "use_stamp_" + k, False)
r.use_stamp_note = True
_D = DISTANZA_FISSA if DISTANZA_FISSA else RAPPORTO_TIRO * 6
_w = _D / RAPPORTO_TIRO
r.stamp_note_text = (f"Ottica {RAPPORTO_TIRO:.2f}:1  -  distanza {_D:.2f} m  -  immagine {_w:.2f} x {_w / FORMATO:.2f} m (16:10) "
                     f"su parete 6,00 x 3,50 m  -  arancio = sinistra, verde = fondo, azzurro = destra"
                     + (", magenta = ingresso" if CON_PORTA else "")
                     + (f"  -  proiettori a girandola, spostati di {GIRANDOLA:.2f} m di lato" if GIRANDOLA else ""))
r.stamp_font_size = 26

etichetta = f"{RAPPORTO_TIRO:.2f}".replace(".", "_") + f"_dist_{_D:.1f}".replace(".", "_") + ("_girandola" if GIRANDOLA else "") + ("" if CON_PORTA else "_senza_porta")
viste = [(cam_interna, "interna", []), (cam_pianta, "pianta", da_nascondere_in_pianta)]
if CON_PORTA:
    viste.insert(1, (cam_porta, "verso_porta", []))
for cam, vista, nascondi in viste:
    for o in nascondi:
        o.hide_render = True
    scena.camera = cam
    scena.render.filepath = os.path.join(cartella, f"zone_ottica_{etichetta}_{vista}.png")
    bpy.ops.render.render(write_still=True)
    print("Render salvato:", scena.render.filepath)
    for o in nascondi:
        o.hide_render = False
