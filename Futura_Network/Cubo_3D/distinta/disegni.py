# Disegni tecnici quotati del Cubo Immersivo (SVG, scala 1:50 su A4).
# Le misure sono le stesse di cubo_immersivo.py. Uso: python3 disegni.py  -> cartella disegni/

import os

QUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(QUI, "disegni")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- misure (m), come nello script della scena
L = P = 6.0
H = 3.5
SP_PARETE, SP_TETTO, SP_BASE = 0.10, 0.08, 0.10
PORTA_L, PORTA_H = 1.0, 2.2
D = 2.0                      # distanza di tiro
RT = D / 6.0                 # rapporto di tiro consigliato (0,33:1)
Z_LENTE = H - 0.30
CORPO = (0.45, 0.35, 0.18)
FORMATO = 16 / 10
IMG_W = D / RT
IMG_H = IMG_W / FORMATO
X0, X1, Y0, Y1 = -L / 2, L / 2, -P / 2, P / 2
SCALA = 50                   # 1:50  ->  1 m = 20 mm
K = 1000 / SCALA             # mm di carta per metro

# ---------------------------------------------------------------- utilità SVG (unità: mm di carta)
NERO, GRIGIO, VIOLA, ROSSO = "#1c1c22", "#9a9aa6", "#6b3fd4", "#d0452f"
COL = {"sx": "#e07a1e", "fondo": "#3aa64a", "dx": "#2a78d8", "ingresso": "#d23aa6"}

class Svg:
    def __init__(self, w, h, ox, oy, flip=True):
        self.w, self.h, self.ox, self.oy, self.flip = w, h, ox, oy, flip
        self.el = []
    def p(self, x, y):                       # metri -> mm carta
        return self.ox + x * K, (self.oy - y * K) if self.flip else (self.oy + y * K)
    def add(self, s):
        self.el.append(s)
    def rect(self, x0, y0, x1, y1, fill="none", stroke=NERO, sw=0.35, dash=None, op=1):
        (a, b), (c, d) = self.p(x0, y0), self.p(x1, y1)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{min(a,c):.2f}" y="{min(b,d):.2f}" width="{abs(c-a):.2f}" height="{abs(d-b):.2f}" '
                 f'fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
    def line(self, x0, y0, x1, y1, stroke=NERO, sw=0.25, dash=None):
        (a, b), (c, d) = self.p(x0, y0), self.p(x1, y1)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{a:.2f}" y1="{b:.2f}" x2="{c:.2f}" y2="{d:.2f}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
    def poly(self, pts, fill="none", stroke=NERO, sw=0.25, op=1, dash=None):
        q = " ".join(f"{a:.2f},{b:.2f}" for a, b in (self.p(x, y) for x, y in pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<polygon points="{q}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
    def text(self, x, y, t, size=2.6, anchor="middle", col=NERO, rot=0, bold=False, dx=0, dy=0):
        a, b = self.p(x, y)
        a, b = a + dx, b + dy
        tr = f' transform="rotate({rot} {a:.2f} {b:.2f})"' if rot else ""
        fw = ' font-weight="700"' if bold else ""
        self.add(f'<text x="{a:.2f}" y="{b:.2f}" font-size="{size}" text-anchor="{anchor}" fill="{col}"{fw}{tr}>{t}</text>')
    def quota(self, x0, y0, x1, y1, off, testo=None, col=NERO):
        """Quota allineata tra due punti, spostata di 'off' metri a sinistra della direzione 0->1."""
        import math
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy)
        nx, ny = -dy / n, dx / n
        a0, b0, a1, b1 = x0 + nx * off, y0 + ny * off, x1 + nx * off, y1 + ny * off
        u = 1.0 / K                                  # 1 mm di carta, in metri
        sg = 1 if off > 0 else -1
        self.line(x0 + nx * off * 0.15, y0 + ny * off * 0.15, a0 + nx * u * sg, b0 + ny * u * sg, col, 0.15)
        self.line(x1 + nx * off * 0.15, y1 + ny * off * 0.15, a1 + nx * u * sg, b1 + ny * u * sg, col, 0.15)
        self.line(a0, b0, a1, b1, col, 0.2)
        for ax, by in ((a0, b0), (a1, b1)):          # tacche oblique
            self.line(ax - 1.2 * u, by - 1.2 * u, ax + 1.2 * u, by + 1.2 * u, col, 0.35)
        ang = math.degrees(math.atan2(dy, dx))
        if self.flip:
            ang = -ang
        if ang > 90 or ang < -90:
            ang += 180
        t = testo if testo is not None else f"{n:.2f}".replace(".", ",")
        self.text((a0 + a1) / 2 + nx * 1.4 * u, (b0 + b1) / 2 + ny * 1.4 * u, t, 2.4, col=col, rot=ang)
    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}mm" height="{self.h}mm" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="Helvetica, Arial, sans-serif">'
                + "".join(self.el) + "</svg>")
    def salva(self, nome):
        with open(os.path.join(OUT, nome), "w") as f:
            f.write(self.svg())

def proiettori(con_porta=True, girandola=0.0):
    """(sigla, chiave colore, posizione ottica (x,y), direzione (dx,dy))"""
    lst = [("P3", "sx", (-1, 0)), ("P1", "dx", (1, 0)), ("P2", "fondo", (0, 1))]
    if con_porta:
        lst.append(("P4", "ingresso", (0, -1)))
    out = []
    for sig, k, (dx, dy) in lst:
        x, y = dx * (3 - D), dy * (3 - D)
        x, y = x + dy * girandola, y - dx * girandola
        out.append((sig, k, (x, y), (dx, dy)))
    return out

# ---------------------------------------------------------------- 1. pianta
def pianta(con_porta=True, nome="01_pianta_con_porta.svg"):
    s = Svg(200, 175, 85, 92)
    # lastre a specchio
    for i in range(7):
        s.line(X0 + i, Y0, X0 + i, Y1, GRIGIO, 0.1)
        s.line(X0, Y0 + i, X1, Y0 + i, GRIGIO, 0.1)
    # pareti
    e = SP_PARETE
    s.rect(X0 - e, Y0 - (e if con_porta else 0), X0, Y1 + e, "#2a2a32")
    s.rect(X1, Y0 - (e if con_porta else 0), X1 + e, Y1 + e, "#2a2a32")
    s.rect(X0 - e, Y1, X1 + e, Y1 + e, "#2a2a32")
    if con_porta:
        s.rect(X0, Y0 - e, -PORTA_L / 2, Y0, "#2a2a32")
        s.rect(PORTA_L / 2, Y0 - e, X1, Y0, "#2a2a32")
        # anta aperta verso l'esterno (75°) e arco di apertura
        import math
        hx, hy = -PORTA_L / 2 + 0.04, Y0 - e
        a = math.radians(-75)
        lun = PORTA_L - 0.08
        s.line(hx, hy, hx + lun * math.cos(a), hy + lun * math.sin(a), NERO, 0.5)
        arc = [(hx + lun * math.cos(math.radians(t)), hy + lun * math.sin(math.radians(t))) for t in range(-75, 1, 5)]
        for (ax, ay), (bx, by) in zip(arc, arc[1:]):
            s.line(ax, ay, bx, by, GRIGIO, 0.15, "0.8 0.6")
        s.text(-0.75, Y0 - e - 0.45, "PORTA 1,00 × 2,20", 2.4, col=NERO, bold=True, anchor="end")
    else:
        s.line(X0, Y0, X1, Y0, GRIGIO, 0.3, "2 1.2")
        s.text(0, Y0 - 0.3, "LATO APERTO (INGRESSO)", 2.4, bold=True)
    # superfici proiettate
    for (x0, y0, x1, y1, k) in ((X0, Y0, X0 + 0.04, Y1, "sx"), (X1 - 0.04, Y0, X1, Y1, "dx"), (X0, Y1 - 0.04, X1, Y1, "fondo")):
        s.rect(x0, y0, x1, y1, COL[k], stroke="none")
    if con_porta:
        s.rect(X0, Y0, -PORTA_L / 2, Y0 + 0.04, COL["ingresso"], stroke="none")
        s.rect(PORTA_L / 2, Y0, X1, Y0 + 0.04, COL["ingresso"], stroke="none")
    # coni di proiezione (immagine 6,00 m esatta in larghezza) e proiettori
    for sig, k, (x, y), (dx, dy) in proiettori(con_porta):
        wx, wy = (x + dx * D, y + dy * D)                   # punto sulla parete
        px, py = -dy, dx                                    # direzione lungo la parete
        a = (wx + px * IMG_W / 2, wy + py * IMG_W / 2)
        b = (wx - px * IMG_W / 2, wy - py * IMG_W / 2)
        s.poly([(x, y), a, b], COL[k], COL[k], 0.2, op=0.10)
        # corpo
        cx, cy = x - dx * (CORPO[0] / 2 + 0.03), y - dy * (CORPO[0] / 2 + 0.03)
        hl, hw = CORPO[0] / 2, CORPO[1] / 2
        if dx:
            s.rect(cx - hl, cy - hw, cx + hl, cy + hw, "#16161c")
        else:
            s.rect(cx - hw, cy - hl, cx + hw, cy + hl, "#16161c")
        s.text(cx + (0 if dx else -0.5), cy + (-0.42 if dx else 0), sig, 3.0, col=COL[k], bold=True, dy=1)
    # quote
    s.quota(X0, Y1 + SP_PARETE, X1, Y1 + SP_PARETE, 0.45, "6,00 (interno)")
    s.quota(X0, Y0, X0, Y1, 0.55 + SP_PARETE, "6,00 (interno)")
    s.quota(-1, -0.0, X0, 0.0, -0.25, "2,00")
    s.quota(1, 0.0, X1, 0.0, 0.25, "2,00")
    s.quota(0.0, 1, 0.0, Y1, -0.25, "2,00")
    if con_porta:
        s.quota(0.0, -1, 0.0, Y0, 0.25, "2,00")
        s.quota(-PORTA_L / 2, Y0 - SP_PARETE, PORTA_L / 2, Y0 - SP_PARETE, -0.3, "1,00")
    # linea di sezione A-A
    s.line(0, Y0 - 1.15, 0, Y0 - 0.8, ROSSO, 0.5)
    s.line(0, Y1 + 0.12, 0, Y1 + 0.42, ROSSO, 0.5)
    s.text(0.15, Y0 - 1.1, "A", 3.2, col=ROSSO, bold=True, anchor="start")
    s.text(0.15, Y1 + 0.2, "A", 3.2, col=ROSSO, bold=True, anchor="start")
    # nord di progetto
    s.text(X0 - 0.9, Y1 + 0.95, "FONDO ↑", 2.4, anchor="start", col=GRIGIO)
    s.salva(nome)

# ---------------------------------------------------------------- 2. sezione A-A (asse Y-Z, x = 0)
def sezione(con_porta=True, nome="03_sezione_AA.svg"):
    s = Svg(200, 120, 85, 98)
    # pavimento e tetto
    s.rect(Y0 - SP_PARETE, -SP_BASE, Y1 + SP_PARETE, 0, "#2a2a32")
    s.rect(Y0 - SP_PARETE, H, Y1 + SP_PARETE, H + SP_TETTO, "#a8794a")
    s.line(Y0, 0.005, Y1, 0.005, "#7fa6c8", 0.6)            # specchio pavimento
    s.line(Y0, H - 0.005, Y1, H - 0.005, "#7fa6c8", 0.6)    # specchio soffitto
    # parete di fondo
    s.rect(Y1, 0, Y1 + SP_PARETE, H, "#2a2a32")
    s.rect(Y1 - 0.04, 0, Y1, H, COL["fondo"], stroke="none")
    # parete d'ingresso con porta (taglio sul vano)
    if con_porta:
        s.rect(Y0 - SP_PARETE, PORTA_H, Y0, H, "#2a2a32")
        s.rect(Y0, PORTA_H, Y0 + 0.04, H, COL["ingresso"], stroke="none")
        s.line(Y0 - SP_PARETE, PORTA_H, Y0, PORTA_H, NERO, 0.3)
    # coni verticali: P2 (fondo) e P4 (ingresso)
    imm_basso, imm_alto = H / 2 - IMG_H / 2, H / 2 + IMG_H / 2
    lst = [("P2", "fondo", 1, 1)] + ([("P4", "ingresso", -1, -1)] if con_porta else [])
    for sig, k, yl, dy in lst:
        wy = yl + dy * D
        s.poly([(yl, Z_LENTE), (wy, imm_basso), (wy, imm_alto)], COL[k], COL[k], 0.2, op=0.10)
        cy = yl - dy * (CORPO[0] / 2 + 0.03)
        s.rect(cy - CORPO[0] / 2, Z_LENTE - CORPO[2] / 2, cy + CORPO[0] / 2, Z_LENTE + CORPO[2] / 2, "#16161c")
        s.rect(cy - 0.025, Z_LENTE + CORPO[2] / 2, cy + 0.025, H, "#8a8a95")
        s.rect(cy - 0.15, H - 0.02, cy + 0.15, H, "#8a8a95")
        s.text(cy, Z_LENTE - 0.35, sig, 3.0, col=COL[k], bold=True)
    # manichino di scala
    s.rect(-0.55, 0, -0.25, 1.75, "#d8d8de", GRIGIO, 0.2)
    s.text(-0.4, 0.9, "1,75", 2.0, rot=-90, col=GRIGIO)
    # quote
    s.quota(Y1 + SP_PARETE, 0, Y1 + SP_PARETE, H, -0.35, "3,50")
    s.quota(Y1 + SP_PARETE, H, Y1 + SP_PARETE, H + SP_TETTO, -0.35, "")
    s.text(Y1 + 1.05, H + 0.1, "tetto 0,08", 2.2, anchor="start", col=GRIGIO)
    s.quota(Y1 + SP_PARETE, -SP_BASE, Y1 + SP_PARETE, 0, -0.35, "")
    s.text(Y1 + 1.05, -0.12, "base 0,10", 2.2, anchor="start", col=GRIGIO)
    s.quota(1, Z_LENTE, Y1, Z_LENTE, -0.3, "2,00")
    s.quota(Y1 + SP_PARETE, imm_basso, Y1 + SP_PARETE, imm_alto, -0.75, f"immagine {IMG_H:.2f}".replace(".", ","), VIOLA)
    s.quota(0.2, 0, 0.2, Z_LENTE, 0.0001, " ")
    s.text(0.3, Z_LENTE / 2, "asse ottico 3,20", 2.3, anchor="start", col=NERO)
    s.line(-0.4, Z_LENTE, 1.0, Z_LENTE, GRIGIO, 0.15, "1 0.6")
    if con_porta:
        s.quota(Y0, 0, Y0, PORTA_H, 0.35, "2,20")
        s.quota(-1, Z_LENTE, Y0, Z_LENTE, 0.3, "2,00")
    s.quota(Y0, -SP_BASE, Y1, -SP_BASE, -0.5, "6,00 (interno)")
    s.text(Y0 - 0.3, H + 0.45, "SEZIONE A-A", 3.2, anchor="start", bold=True, col=ROSSO)
    s.text(Y0 - 0.3, H + 0.22, "(ingresso a sinistra, fondo a destra)", 2.2, anchor="start", col=GRIGIO)
    s.salva(nome)

# ---------------------------------------------------------------- 3. prospetti delle pareti proiettate
def prospetto(titolo, chiave, con_porta_parete, nome):
    s = Svg(200, 105, 92, 82)
    s.rect(X0, 0, X1, H, "#f4f4f6", NERO, 0.4)
    if con_porta_parete:
        s.rect(-PORTA_L / 2, 0, PORTA_L / 2, PORTA_H, "#2a2a32")
        s.text(0, PORTA_H / 2, "porta", 2.4, col="#ffffff")
    # rettangolo immagine (16:10) e griglia
    b0, b1 = H / 2 - IMG_H / 2, H / 2 + IMG_H / 2
    s.rect(-IMG_W / 2, b0, IMG_W / 2, b1, COL[chiave], COL[chiave], 0.35, op=0.12)
    for i in range(1, 16):
        x = -IMG_W / 2 + i * IMG_W / 16
        s.line(x, b0, x, b1, COL[chiave], 0.08)
    for j in range(1, 10):
        z = b0 + j * IMG_H / 10
        s.line(-IMG_W / 2, z, IMG_W / 2, z, COL[chiave], 0.08)
    s.rect(-IMG_W / 2, H, IMG_W / 2, b1, "#d0452f", "none", op=0.25)
    s.rect(-IMG_W / 2, b0, IMG_W / 2, 0, "#d0452f", "none", op=0.25)
    s.text(X1 + 0.15, (H + b1) / 2, "abbondanza 0,125 su soffitto", 2.1, anchor="start", col=ROSSO, dy=0.8)
    s.text(X1 + 0.15, b0 / 2, "abbondanza 0,125 su pavimento", 2.1, anchor="start", col=ROSSO, dy=0.8)
    s.quota(X0, 0, X1, 0, -0.35, "6,00")
    s.quota(X0, 0, X0, H, 0.35, "3,50")
    s.quota(X0, b0, X0, b1, 0.85, f"immagine {IMG_H:.2f}".replace(".", ","), VIOLA)
    if con_porta_parete:
        s.quota(-PORTA_L / 2, PORTA_H, PORTA_L / 2, PORTA_H, 0.2, "1,00")
        s.quota(PORTA_L / 2, 0, PORTA_L / 2, PORTA_H, -0.25, "2,20")
    s.text(X0, H + 0.42, titolo, 3.2, anchor="start", bold=True)
    s.text(X0, H + 0.2, f"immagine {IMG_W:.2f} × {IMG_H:.2f} m (16:10), ottica {RT:.2f}:1 a {D:.2f} m".replace(".", ","),
           2.2, anchor="start", col=GRIGIO)
    s.salva(nome)

# ---------------------------------------------------------------- 4. dettaglio proiettore e staffa (scala 1:10)
def dettaglio(nome="06_dettaglio_proiettore.svg"):
    global K
    k_old, K = K, 100                      # 1:10
    s = Svg(200, 105, 20, 62)
    zl = 0.0                               # asse ottico come riferimento locale
    top = CORPO[2] / 2
    asta = H - (Z_LENTE + top)             # 0,21 m
    # vista laterale
    s.rect(0, -top, CORPO[0], top, "#16161c")
    s.rect(CORPO[0], -0.06, CORPO[0] + 0.06, 0.06, "#8a8a95")         # ottica
    s.line(CORPO[0] + 0.06, 0, CORPO[0] + 0.3, 0, GRIGIO, 0.2, "2 1")
    cx = CORPO[0] / 2
    s.rect(cx - 0.025, top, cx + 0.025, top + asta, "#8a8a95")
    s.rect(cx - 0.15, top + asta - 0.02, cx + 0.15, top + asta, "#8a8a95")
    s.rect(-0.1, top + asta, CORPO[0] + 0.45, top + asta + SP_TETTO, "#a8794a")
    s.text(-0.1, top + asta + SP_TETTO + 0.04, "DETTAGLIO PROIETTORE E STAFFA  (scala 1:10)", 3.0, anchor="start", bold=True)
    s.text(CORPO[0] + 0.48, top + asta + 0.025, "tetto in legno 0,08", 2.4, anchor="start", col=GRIGIO, dy=0.9)
    s.quota(0, -top, CORPO[0], -top, -0.06, "0,45")
    s.quota(CORPO[0] + 0.06, -top, CORPO[0] + 0.06, top, -0.12, "0,18")
    s.quota(cx + 0.15, top, cx + 0.15, top + asta, -0.12, f"{asta:.2f}".replace(".", ","))
    s.quota(cx + 0.15, top + asta - 0.02, cx - 0.15, top + asta - 0.02, 0.06, " ")
    s.text(cx - 0.17, top + asta - 0.08, "piastra 0,30", 2.4, anchor="end", dy=0.9)
    s.text(CORPO[0] + 0.24, -0.035, "asse ottico (quota 3,20)", 2.4, anchor="start", dy=0.9)
    s.text(cx, -top - 0.2, "VISTA LATERALE", 2.8, bold=True)
    # vista dall'alto
    ox = 0.95
    s.rect(ox, -CORPO[1] / 2, ox + CORPO[0], CORPO[1] / 2, "#16161c")
    s.rect(ox + CORPO[0], -0.06, ox + CORPO[0] + 0.06, 0.06, "#8a8a95")
    s.rect(ox + cx - 0.15, -0.15, ox + cx + 0.15, 0.15, "none", "#8a8a95", 0.4, "1 0.6")
    s.rect(ox + cx - 0.025, -0.025, ox + cx + 0.025, 0.025, "#8a8a95")
    s.quota(ox, -CORPO[1] / 2, ox + CORPO[0], -CORPO[1] / 2, -0.06, "0,45")
    s.quota(ox + CORPO[0] + 0.06, -CORPO[1] / 2, ox + CORPO[0] + 0.06, CORPO[1] / 2, -0.12, "0,35")
    s.text(ox + cx, CORPO[1] / 2 + 0.06, "VISTA DALL'ALTO", 2.8, bold=True)
    s.text(ox, -0.30, "piastra 0,30 × 0,30 × 0,02  ·  asta 0,05 × 0,05", 2.3, anchor="start", col=GRIGIO)
    s.text(ox, -0.335, "ingombro del corpo indicativo, da adeguare al modello scelto", 2.3, anchor="start", col=GRIGIO)
    s.salva(nome)
    K = k_old

# ---------------------------------------------------------------- 5. pianta variante a girandola (ottica 0,5:1)
def pianta_girandola(nome="07_pianta_girandola_0_5.svg", a=0.4):
    s = Svg(200, 175, 85, 92)
    e = SP_PARETE
    s.rect(X0 - e, Y0 - e, X0, Y1 + e, "#2a2a32")
    s.rect(X1, Y0 - e, X1 + e, Y1 + e, "#2a2a32")
    s.rect(X0 - e, Y1, X1 + e, Y1 + e, "#2a2a32")
    s.rect(X0, Y0 - e, -PORTA_L / 2, Y0, "#2a2a32")
    s.rect(PORTA_L / 2, Y0 - e, X1, Y0, "#2a2a32")
    d5 = 3.0
    for sig, k, (dx, dy) in [("P3", "sx", (-1, 0)), ("P1", "dx", (1, 0)), ("P2", "fondo", (0, 1)), ("P4", "ingresso", (0, -1))]:
        x, y = dy * a, -dx * a
        wx, wy = x + dx * d5, y + dy * d5
        px, py = -dy, dx
        cxw, cyw = (dx * 3, dy * 3)
        A = (cxw + px * 3, cyw + py * 3) if dx else (cxw + px * 3, cyw + py * 3)
        B = (cxw - px * 3, cyw - py * 3)
        s.poly([(x, y), A, B], COL[k], COL[k], 0.2, op=0.10)
        cx, cy = x - dx * (CORPO[0] / 2 + 0.03), y - dy * (CORPO[0] / 2 + 0.03)
        hl, hw = CORPO[0] / 2, CORPO[1] / 2
        if dx:
            s.rect(cx - hl, cy - hw, cx + hl, cy + hw, "#16161c")
        else:
            s.rect(cx - hw, cy - hl, cx + hw, cy + hl, "#16161c")
        s.text(cx + dy * 0.55, cy - dx * 0.55, sig, 3.0, col=COL[k], bold=True, dy=1)
    s.quota(0, 0, X0, 0, 1.6, "3,00")
    s.quota(X0, Y0, X0, Y1, 0.55 + e, "6,00 (interno)")
    s.text(0, Y0 - 0.55, "VARIANTE: ottica 0,5:1 a 3,00 m, proiettori a girandola spostati di 0,40 m", 2.6, bold=True)
    s.text(0, Y0 - 0.85, "immagine ricentrata con lens shift orizzontale (circa 7%)", 2.3, col=GRIGIO)
    s.salva(nome)

pianta(True, "01_pianta_con_porta.svg")
pianta(False, "02_pianta_senza_porta.svg")
sezione(True, "03_sezione_AA.svg")
prospetto("PROSPETTO PARETE DI FONDO (P2)", "fondo", False, "04_prospetto_fondo.svg")
prospetto("PROSPETTO PARETE D'INGRESSO (P4)", "ingresso", True, "05_prospetto_ingresso.svg")
dettaglio()
pianta_girandola()
print("Disegni creati in", OUT)
