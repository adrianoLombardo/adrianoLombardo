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

# ---------------------------------------------------------------- opzioni da riga di comando
#   --ottica 0.8      rapporto di tiro (distanza / larghezza immagine)
#   --senza-porta     lato frontale aperto invece della parete con la porta
#   --salva <file>    salva il .blend
import sys
ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RAPPORTO_TIRO = float(ARGV[ARGV.index("--ottica") + 1]) if "--ottica" in ARGV else 2.0 / 6.0
CON_PORTA = "--senza-porta" not in ARGV
#   --distanza 4.8    distanza di tiro fissa (m): l'immagine diventa larga distanza / rapporto di tiro
#   (default 2,0 m: i tre proiettori sono raggruppati al centro, schiena contro schiena, come da schizzo)
DISTANZA_FISSA = float(ARGV[ARGV.index("--distanza") + 1]) if "--distanza" in ARGV else 2.0
FORMATO = 16 / 10            # WUXGA, il formato più comune nei proiettori da installazione

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

if CON_PORTA:
    # Parete frontale chiusa con porta d'ingresso (vano 1,0 x 2,2 m al centro)
    PORTA_L, PORTA_H = 1.0, 2.2
    YF = Y0 - SP_PARETE / 2
    lato = (L + 2 * SP_PARETE - PORTA_L) / 2
    box("Parete_frontale_sx", (X0 - SP_PARETE + lato / 2, YF, H / 2), (lato, SP_PARETE, H), M_STRUTTURA, C_STRUTTURA)
    box("Parete_frontale_dx", (X1 + SP_PARETE - lato / 2, YF, H / 2), (lato, SP_PARETE, H), M_STRUTTURA, C_STRUTTURA)
    box("Parete_frontale_architrave", (0, YF, (PORTA_H + H) / 2), (PORTA_L, SP_PARETE, H - PORTA_H), M_STRUTTURA, C_STRUTTURA)
    # telaio della porta
    M_TELAIO = mat_base("Telaio_porta", (0.05, 0.05, 0.055), rough=0.35, metal=1.0)
    T = 0.04
    box("Porta_telaio_sx", (-PORTA_L / 2 + T / 2, YF, PORTA_H / 2), (T, SP_PARETE + 0.01, PORTA_H), M_TELAIO, C_STRUTTURA)
    box("Porta_telaio_dx", (PORTA_L / 2 - T / 2, YF, PORTA_H / 2), (T, SP_PARETE + 0.01, PORTA_H), M_TELAIO, C_STRUTTURA)
    box("Porta_telaio_alto", (0, YF, PORTA_H - T / 2), (PORTA_L, SP_PARETE + 0.01, T), M_TELAIO, C_STRUTTURA)
    # anta aperta verso l'esterno, cerniera sul lato sinistro
    ANTA_L = PORTA_L - 2 * T
    from mathutils import Matrix
    anta = box("Porta_anta", (0, 0, 0), (ANTA_L, 0.045, PORTA_H - T - 0.01), M_STRUTTURA, C_STRUTTURA)
    anta.data.transform(Matrix.Translation((ANTA_L / 2, 0, (PORTA_H - T - 0.01) / 2)))  # origine sulla cerniera
    anta.location = (-PORTA_L / 2 + T, Y0 - SP_PARETE - 0.025, 0.005)
    anta.rotation_euler = (0, 0, math.radians(-75))
    box("Porta_maniglia", (0, 0, 0), (0.12, 0.03, 0.02), M_TELAIO, C_STRUTTURA).parent = anta
    anta.children[0].location = (ANTA_L - 0.1, -0.04, 1.05)

# Base del pavimento e pannello di legno del tetto
box("Base_pavimento", (0, 0, -SP_BASE / 2), (L + 2 * SP_PARETE, P + SP_PARETE, SP_BASE), M_STRUTTURA, C_STRUTTURA)
box("Tetto_pannello_legno", (0, 0, H + SP_TETTO / 2), (L + 2 * SP_PARETE, P + SP_PARETE, SP_TETTO), M_LEGNO, C_STRUTTURA)

# ---------------------------------------------------------------- specchi
OFF = 0.002  # piccolo distacco per evitare sovrapposizioni
# lastre a specchio da 1 x 1 m con fuga di 3 mm
LASTRA, FUGA = 1.0, 0.003
nx, ny = round(L / LASTRA), round(P / LASTRA)
for nome_s, z, rot in (("Specchio_pavimento", OFF, (0, 0, 0)), ("Specchio_soffitto", H - OFF, (math.pi, 0, 0))):
    for i in range(nx):
        for j in range(ny):
            cx = X0 + (i + 0.5) * L / nx
            cy = Y0 + (j + 0.5) * P / ny
            piano(f"{nome_s}_{i}_{j}", (cx, cy, z), L / nx - FUGA, P / ny - FUGA, M_SPECCHIO, C_SPECCHI, rot=rot)

# ---------------------------------------------------------------- proiettori
# Posizione calcolata dall'ottica: distanza di tiro D = rapporto di tiro x larghezza immagine.
# L'asse ottico è orizzontale e perpendicolare alla parete; l'immagine viene centrata sulla
# parete con il lens shift (verticale e orizzontale), come si fa con i proiettori reali.
# Disposizione (schizzo): i tre proiettori sono raggruppati al centro del cubo, ognuno rivolto
# verso la propria parete e alla stessa distanza da essa. Ogni proiettore è appeso al tetto con una staffa.
CORPO = (0.45, 0.35, 0.18)   # lunghezza (lungo l'asse ottico), larghezza, altezza (m)
Z_LENTE = H - 0.30           # quota dell'asse ottico
SCOSTAMENTO = 0.0            # proiettori sull'asse della propria parete (disposizione simmetrica)

pareti = [
    # nome, punto sulla parete, direzione verso la parete, asse "destra" dell'immagine, angoli
    ("Proiettore_parete_sinistra", Vector((X0, 0, 0)), Vector((-1, 0, 0)), Vector((0, SCOSTAMENTO, 0)),
     [Vector((X0, Y0, 0)), Vector((X0, Y1, 0)), Vector((X0, Y1, H)), Vector((X0, Y0, H))]),
    ("Proiettore_parete_destra", Vector((X1, 0, 0)), Vector((1, 0, 0)), Vector((0, -SCOSTAMENTO, 0)),
     [Vector((X1, Y1, 0)), Vector((X1, Y0, 0)), Vector((X1, Y0, H)), Vector((X1, Y1, H))]),
    ("Proiettore_parete_fondo", Vector((0, Y1, 0)), Vector((0, 1, 0)), Vector((0, 0, 0)),
     [Vector((X1, Y1, 0)), Vector((X0, Y1, 0)), Vector((X0, Y1, H)), Vector((X1, Y1, H))]),
]
LARGHEZZA_IMMAGINE = {"Proiettore_parete_sinistra": P, "Proiettore_parete_destra": P, "Proiettore_parete_fondo": L}

def luce_proiettore(nome, lente, direzione, centro_parete, larghezza_img, colore=(1, 1, 1)):
    """Luce spot con il tronco di proiezione reale (formato 16:10, centrato sulla parete con il
    lens shift) e una griglia di test. Non è ritagliata sulla parete: se l'immagine è più grande,
    la parte in eccesso cade su pavimento, soffitto e pareti vicine, come nella realtà."""
    ld = bpy.data.lights.new(nome + "_fascio", type='SPOT')
    ld.shadow_soft_size = 0.03          # pupilla dell'ottica: ombre nette come nella realtà
    ob = bpy.data.objects.new(nome + "_fascio", ld)
    ob.location = lente
    ob.rotation_euler = direzione.to_track_quat('-Z', 'Y').to_euler()
    C_PROIEZIONI.objects.link(ob)
    mat = ob.rotation_euler.to_matrix()
    destra, alto = mat @ Vector((1, 0, 0)), mat @ Vector((0, 1, 0))
    dist = (centro_parete - lente).dot(direzione)
    cu = (centro_parete - lente).dot(destra) / dist
    cv = (centro_parete - lente).dot(alto) / dist
    mu, mv = larghezza_img / 2 / dist, larghezza_img / FORMATO / 2 / dist
    umin, umax, vmin, vmax = cu - mu, cu + mu, cv - mv, cv + mv
    ld.spot_size = min(math.radians(179), 2 * math.atan(math.hypot(max(-umin, umax), max(-vmin, vmax))) + 0.02)
    ld.spot_blend = 0.0
    ld.energy = 120 * dist ** 2 * (6.0 / larghezza_img) ** 2   # luminosità costante per m² a parità di proiettore
    ld.use_nodes = True
    nt = ld.node_tree
    emi = nt.nodes.get("Emission")
    emi.inputs["Color"].default_value = (*colore, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Normal"], sep.inputs["Vector"])
    def m(op, a, b=0.0):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, x in enumerate((a, b)):
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                nt.links.new(x, n.inputs[i])
        return n.outputs[0]
    zneg = m('MULTIPLY', sep.outputs["Z"], -1.0)
    u = m('DIVIDE', sep.outputs["X"], zneg)
    v = m('DIVIDE', sep.outputs["Y"], zneg)
    U = m('DIVIDE', m('SUBTRACT', u, umin), umax - umin)       # 0..1 sull'immagine
    V = m('DIVIDE', m('SUBTRACT', v, vmin), vmax - vmin)
    dentro = m('MULTIPLY', m('MULTIPLY', m('GREATER_THAN', U, 0.0), m('LESS_THAN', U, 1.0)),
               m('MULTIPLY', m('GREATER_THAN', V, 0.0), m('LESS_THAN', V, 1.0)))
    # griglia 16 x 10 (celle quadrate), cornice e croce centrale
    def linee(X, n, sp):
        f = m('FRACT', m('MULTIPLY', X, n))
        return m('MAXIMUM', m('LESS_THAN', f, sp), m('GREATER_THAN', f, 1 - sp))
    griglia = m('MAXIMUM', linee(U, 16, 0.025), linee(V, 10, 0.025))
    bordo = m('MAXIMUM', linee(U, 1, 0.006), linee(V, 1, 0.009))
    croce = m('MAXIMUM', m('LESS_THAN', m('ABSOLUTE', m('SUBTRACT', U, 0.5)), 0.003),
              m('LESS_THAN', m('ABSOLUTE', m('SUBTRACT', V, 0.5)), 0.005))
    tratti = m('MAXIMUM', m('MAXIMUM', griglia, bordo), croce)
    nt.links.new(m('MULTIPLY', dentro, m('ADD', 0.35, m('MULTIPLY', tratti, 1.6))), emi.inputs["Strength"])
    ob.hide_render = True               # spenta nella scena realistica (le pareti sono già luminose)
    ob["immagine_m"] = [larghezza_img, larghezza_img / FORMATO]
    return ob

for nome, punto, direzione, scost, angoli in pareti:
    D = DISTANZA_FISSA if DISTANZA_FISSA else RAPPORTO_TIRO * LARGHEZZA_IMMAGINE[nome]
    larghezza_img = D / RAPPORTO_TIRO
    lente_pos = Vector((punto.x, punto.y, Z_LENTE)) - direzione * D + scost
    rot = direzione.to_track_quat('X', 'Z').to_euler()

    # corpo del proiettore dietro l'ottica (asse X locale = asse ottico)
    centro_corpo = lente_pos - direzione * (CORPO[0] / 2 + 0.03)
    corpo = box(nome, centro_corpo, CORPO, M_PROIETTORE, C_PROIETTORI)
    corpo.rotation_euler = rot
    corpo["distanza_di_tiro_m"] = D
    corpo["rapporto_di_tiro"] = RAPPORTO_TIRO

    # obiettivo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.06, location=lente_pos - direzione * 0.03)
    lente = bpy.context.active_object
    lente.name = nome + "_ottica"
    lente.rotation_euler = direzione.to_track_quat('Z', 'Y').to_euler()
    lente.data.materials.append(M_STAFFA)
    for c in lente.users_collection:
        c.objects.unlink(lente)
    C_PROIETTORI.objects.link(lente)

    # staffa: asta verticale dal corpo al pannello del tetto + piastra
    top_corpo = Z_LENTE + CORPO[2] / 2
    alt_asta = H - top_corpo
    box(nome + "_staffa_asta", (centro_corpo.x, centro_corpo.y, top_corpo + alt_asta / 2),
        (0.05, 0.05, alt_asta), M_STAFFA, C_PROIETTORI)
    box(nome + "_staffa_piastra", (centro_corpo.x, centro_corpo.y, H - 0.01), (0.3, 0.3, 0.02), M_STAFFA, C_PROIETTORI)

    # fascio luminoso per i render delle zone di proiezione
    luce_proiettore(nome, lente_pos, direzione, sum(angoli, Vector()) / 4, larghezza_img)

    # cono di proiezione (solo guida in viewport, non va in render)
    me = bpy.data.meshes.new(nome + "_cono")
    verts = [lente_pos] + angoli
    facce = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1)]
    me.from_pydata([tuple(v) for v in verts], [], facce)
    cono = bpy.data.objects.new(nome + "_cono", me)
    cono.display_type = 'WIRE'
    cono.hide_render = True
    C_PROIEZIONI.objects.link(cono)

_D = DISTANZA_FISSA if DISTANZA_FISSA else RAPPORTO_TIRO * 6
print(f"Ottica {RAPPORTO_TIRO:.2f}:1, distanza {_D:.2f} m -> immagine {_D / RAPPORTO_TIRO:.2f} x {_D / RAPPORTO_TIRO / FORMATO:.2f} m")

# proiettori e staffe mascherati: invisibili nei riflessi degli specchi
for ob in C_PROIETTORI.objects:
    ob.visible_glossy = False

# ---------------------------------------------------------------- realismo
# Materiali PBR, ambiente del padiglione, bordi smussati, manichini di scala.

def nodi(m):
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    return nt, nt.nodes.new("ShaderNodeOutputMaterial")

# contenuto proiettato: nebulosa fluida a più livelli, come un generativo Notch
def contenuto_realistico(m, colori, scala, seme, forza=1.4):
    nt, out = nodi(m)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Location"].default_value = (seme, seme * 0.37, seme * 0.71)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    # distorsione del dominio
    dist = nt.nodes.new("ShaderNodeTexNoise")
    dist.inputs["Scale"].default_value = scala * 0.6
    dist.inputs["Detail"].default_value = 4.0
    nt.links.new(mapping.outputs["Vector"], dist.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = 'VECTOR'
    mix.inputs["Factor"].default_value = 0.55
    nt.links.new(mapping.outputs["Vector"], mix.inputs["A"])
    nt.links.new(dist.outputs["Color"], mix.inputs["B"])
    rumore = nt.nodes.new("ShaderNodeTexNoise")
    rumore.inputs["Scale"].default_value = scala
    rumore.inputs["Detail"].default_value = 10.0
    rumore.inputs["Roughness"].default_value = 0.62
    nt.links.new(mix.outputs["Result"], rumore.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = 'B_SPLINE'
    for k, (pos, col) in enumerate(colori):
        el = cr.elements[k] if k < 2 else cr.elements.new(pos)
        el.position = pos
        el.color = (*col, 1)
    nt.links.new(rumore.outputs["Fac"], ramp.inputs["Fac"])
    emi = nt.nodes.new("ShaderNodeEmission")
    emi.inputs["Strength"].default_value = forza
    nt.links.new(ramp.outputs["Color"], emi.inputs["Color"])
    # la parete resta un pannello bianco opaco: un po' di diffuso sotto la proiezione
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (0.25, 0.25, 0.25, 1)
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(diff.outputs["BSDF"], add.inputs[0])
    nt.links.new(emi.outputs["Emission"], add.inputs[1])
    nt.links.new(add.outputs["Shader"], out.inputs["Surface"])
    m.diffuse_color = (*colori[-2][1], 1)

palette_fredda = [(0.30, (0.0, 0.002, 0.02)), (0.42, (0.0, 0.05, 0.4)), (0.50, (0.0, 0.35, 1.0)),
                  (0.58, (0.45, 0.05, 0.9)), (0.70, (0.6, 0.95, 1.0))]
palette_calda = [(0.30, (0.01, 0.0, 0.02)), (0.42, (0.25, 0.0, 0.45)), (0.50, (1.0, 0.05, 0.45)),
                 (0.58, (0.1, 0.15, 1.0)), (0.70, (1.0, 0.75, 0.4))]
contenuto_realistico(M_PARETE_SX, palette_fredda, 0.9, 1.3)
contenuto_realistico(M_PARETE_DX, palette_fredda, 0.9, 7.9)
contenuto_realistico(M_PARETE_FONDO, palette_calda, 0.8, 4.2)

# specchio: vetro argentato con leggerissima tinta e micro-variazione di rugosità
nt, out = nodi(M_SPECCHIO)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.9, 0.93, 0.93, 1)
bsdf.inputs["Metallic"].default_value = 1.0
mr = nt.nodes.new("ShaderNodeTexNoise")
mr.inputs["Scale"].default_value = 3.0
mrr = nt.nodes.new("ShaderNodeMapRange")
mrr.inputs["To Min"].default_value = 0.0
mrr.inputs["To Max"].default_value = 0.012
nt.links.new(mr.outputs["Fac"], mrr.inputs["Value"])
nt.links.new(mrr.outputs["Result"], bsdf.inputs["Roughness"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# legno del tetto: multistrato con venatura procedurale
nt, out = nodi(M_LEGNO)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
coord = nt.nodes.new("ShaderNodeTexCoord")
mp = nt.nodes.new("ShaderNodeMapping")
mp.inputs["Scale"].default_value = (1.0, 0.08, 1.0)
nt.links.new(coord.outputs["Object"], mp.inputs["Vector"])
onde = nt.nodes.new("ShaderNodeTexWave")
onde.wave_type = 'RINGS'
onde.inputs["Scale"].default_value = 1.6
onde.inputs["Distortion"].default_value = 9.0
onde.inputs["Detail"].default_value = 6.0
nt.links.new(mp.outputs["Vector"], onde.inputs["Vector"])
rmp = nt.nodes.new("ShaderNodeValToRGB")
rmp.color_ramp.elements[0].color = (0.28, 0.16, 0.08, 1)
rmp.color_ramp.elements[1].color = (0.62, 0.43, 0.26, 1)
nt.links.new(onde.outputs["Fac"], rmp.inputs["Fac"])
nt.links.new(rmp.outputs["Color"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.55
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.08
nt.links.new(onde.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

# struttura esterna: pannello verniciato nero satinato
M_STRUTTURA.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.45
M_STRUTTURA.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.015, 0.015, 0.017, 1)

# proiettori: scocca in plastica satinata, ottica in vetro
M_PROIETTORE.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.022, 1)
M_PROIETTORE.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
M_VETRO = bpy.data.materials.new("Vetro_ottica")
nt, out = nodi(M_VETRO)
g = nt.nodes.new("ShaderNodeBsdfGlass")
g.inputs["Color"].default_value = (0.6, 0.7, 0.8, 1)
g.inputs["Roughness"].default_value = 0.02
nt.links.new(g.outputs["BSDF"], out.inputs["Surface"])
for ob in C_PROIETTORI.objects:
    if ob.name.endswith("_ottica"):
        ob.data.materials.append(M_VETRO)  # cilindro: anello metallico + vetro sulla faccia
        for poly in ob.data.polygons:
            if len(poly.vertices) > 4:
                poly.material_index = 1
        ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons))

# bordi smussati su tutte le scatole (niente spigoli "da computer")
for coll, larg in ((C_STRUTTURA, 0.004), (C_PROIETTORI, 0.006)):
    for ob in coll.objects:
        if ob.type == 'MESH' and len(ob.data.polygons) == 6:
            mod = ob.modifiers.new("Smusso", 'BEVEL')
            mod.width = larg
            mod.segments = 3
            mod.limit_method = 'NONE'

# pavimento del padiglione: cemento levigato
M_CEMENTO = bpy.data.materials.new("Cemento_padiglione")
nt, out = nodi(M_CEMENTO)
bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
n1 = nt.nodes.new("ShaderNodeTexNoise")
n1.inputs["Scale"].default_value = 1.5
n1.inputs["Detail"].default_value = 12.0
r1 = nt.nodes.new("ShaderNodeValToRGB")
r1.color_ramp.elements[0].color = (0.10, 0.10, 0.10, 1)
r1.color_ramp.elements[1].color = (0.22, 0.21, 0.20, 1)
nt.links.new(n1.outputs["Fac"], r1.inputs["Fac"])
nt.links.new(r1.outputs["Color"], bsdf.inputs["Base Color"])
r2 = nt.nodes.new("ShaderNodeMapRange")
r2.inputs["To Min"].default_value = 0.18
r2.inputs["To Max"].default_value = 0.55
nt.links.new(n1.outputs["Fac"], r2.inputs["Value"])
nt.links.new(r2.outputs["Result"], bsdf.inputs["Roughness"])
nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
C_AMBIENTE = collezione("Ambiente")
piano("Pavimento_padiglione", (0, 0, -SP_BASE - 0.001), 80, 80, M_CEMENTO, C_AMBIENTE)

# ---------------------------------------------------------------- manichini di scala (1,75 m)
M_PERSONA.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5
M_PERSONA.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.7, 0.7, 0.7, 1)

def manichino(nome, x, y, rot_z, altezza=1.75):
    k = altezza / 1.75
    v = [(0, 0, 0.95), (0, 0, 1.08), (0, 0, 1.32), (0, 0, 1.47), (0, 0, 1.53)]
    r = [(0.13, 0.09), (0.12, 0.085), (0.165, 0.10), (0.05, 0.05), (0.05, 0.05)]
    e = [(0, 1), (1, 2), (2, 3), (3, 4)]
    for s in (1, -1):
        b = len(v)
        v += [(s * 0.09, 0, 0.90), (s * 0.10, 0.01, 0.50), (s * 0.10, 0, 0.09), (s * 0.10, -0.15, 0.045)]
        r += [(0.075, 0.075), (0.052, 0.052), (0.042, 0.042), (0.035, 0.035)]
        e += [(0, b), (b, b + 1), (b + 1, b + 2), (b + 2, b + 3)]
        b = len(v)
        v += [(s * 0.19, 0, 1.40), (s * 0.23, 0.02, 1.13), (s * 0.25, -0.02, 0.88), (s * 0.255, -0.025, 0.79)]
        r += [(0.052, 0.052), (0.040, 0.040), (0.030, 0.030), (0.038, 0.020)]
        e += [(2, b), (b, b + 1), (b + 1, b + 2), (b + 2, b + 3)]
    me = bpy.data.meshes.new(nome)
    me.from_pydata([tuple(c * k for c in p) for p in v], e, [])
    ob = bpy.data.objects.new(nome, me)
    C_RIFERIMENTI.objects.link(ob)
    ob.modifiers.new("Pelle", 'SKIN')
    sv = me.skin_vertices[0].data
    for i, (rx, ry) in enumerate(r):
        sv[i].radius = (rx * k, ry * k)
    sv[0].use_root = True
    sub = ob.modifiers.new("Morbido", 'SUBSURF')
    sub.levels = sub.render_levels = 2
    me.materials.append(M_PERSONA)
    # testa
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1 * k, segments=48, ring_count=24,
                                         location=(0, 0.005 * k, 1.645 * k))
    testa = bpy.context.active_object
    testa.name = nome + "_testa"
    testa.scale = (0.85, 1.0, 1.08)
    bpy.ops.object.shade_smooth()
    testa.data.materials.append(M_PERSONA)
    for c in testa.users_collection:
        c.objects.unlink(testa)
    C_RIFERIMENTI.objects.link(testa)
    testa.parent = ob
    ob.location = (x, y, OFF)
    ob.rotation_euler = (0, 0, rot_z)
    return ob

# rivolti verso la parete di fondo (le punte dei piedi vanno verso +Y)
manichino("Persona_riferimento_1", -0.8, -0.5, math.pi + 0.35)
manichino("Persona_riferimento_2", 1.0, 0.8, math.pi - 0.5)

# ---------------------------------------------------------------- camere
def camera(nome, pos, guarda, lente_mm):
    cam_data = bpy.data.cameras.new(nome)
    cam_data.lens = lente_mm
    cam = bpy.data.objects.new(nome, cam_data)
    cam.location = pos
    cam.rotation_euler = (Vector(guarda) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    C_CAMERE.objects.link(cam)
    return cam

if CON_PORTA:
    cam_ingresso = camera("Camera_ingresso", (0.6, Y0 - 3.6, 1.55), (0, Y0, 1.3), 24)
else:
    cam_ingresso = camera("Camera_ingresso", (0, Y0 - 4.5, 1.7), (0, 0, 1.6), 24)
camera("Camera_interna", (0, Y0 + 1.0, 1.6), (0, Y1, 1.9), 14)
camera("Camera_esterna_3-4", (X1 + 6, Y0 - 7, 5.5), (0, 0, 1.5), 28)
scena.camera = cam_ingresso

# luce ambiente debole (il cubo si illumina con le proiezioni)
luce_data = bpy.data.lights.new("Luce_ambiente", type='AREA')
luce_data.energy = 40
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
    sfondo.inputs["Color"].default_value = (0.012, 0.012, 0.015, 1)
    sfondo.inputs["Strength"].default_value = 1.0

# ---------------------------------------------------------------- render
# Cycles per vedere bene il riflesso infinito tra pavimento e soffitto a specchio
scena.render.engine = 'CYCLES'
scena.cycles.samples = 1024
scena.cycles.use_adaptive_sampling = True
scena.cycles.adaptive_threshold = 0.008
scena.cycles.use_denoising = True
scena.cycles.max_bounces = 48
scena.cycles.glossy_bounces = 48      # riflesso infinito tra i due specchi
scena.cycles.diffuse_bounces = 4
scena.cycles.sample_clamp_indirect = 10
scena.cycles.caustics_reflective = False
scena.cycles.caustics_refractive = False
scena.cycles.transparent_max_bounces = 8
scena.render.resolution_x = 1920
scena.render.resolution_y = 1080
try:
    scena.view_settings.view_transform = 'AgX'
except TypeError:
    scena.view_settings.view_transform = 'Filmic'

print("Cubo immersivo creato: 6 x 6 m, h 3,5 m — 3 pareti proiettate, pavimento e soffitto a specchio, 3 proiettori.")

# ---------------------------------------------------------------- salvataggio (da riga di comando)
if "--salva" in ARGV:
    percorso = ARGV[ARGV.index("--salva") + 1]
    bpy.ops.wm.save_as_mainfile(filepath=percorso)
    print("Salvato:", percorso)
