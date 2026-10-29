# Crea la distinta PDF del Cubo Immersivo per Music Box.
# Uso: python3 crea_distinta.py   (poi: node stampa_pdf.js)
# Legge i render dalla cartella superiore e scrive distinta.html accanto a questo script.

import os, html

QUI = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.dirname(QUI)

def img(nome):
    """Copia JPEG compressa del render (il PNG originale pesa troppo per un PDF da inviare)."""
    src = os.path.join(RENDER, nome)
    if not os.path.exists(src):
        return src
    from PIL import Image
    dst = os.path.join(QUI, "img", os.path.splitext(nome)[0] + ".jpg")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
        im = Image.open(src).convert("RGB")
        im.thumbnail((1600, 1600))
        im.save(dst, quality=82, optimize=True)
    return dst

def esiste(nome):
    return os.path.exists(os.path.join(RENDER, nome))

OTTICHE = [
    ("0_25_dist_2_0", "0,25:1", "2,00 m", "8,00 × 5,00 m",
     "L'immagine è molto più grande della parete. L'abbondanza cade su pavimento, soffitto e pareti adiacenti, "
     "e nei quattro angoli i fasci di due proiettori si sovrappongono. Va gestita con una maschera nel contenuto "
     "(la parte fuori parete deve essere nera), e si perde risoluzione utile: la parete usa circa il 53% dei pixel."),
    ("0_33_dist_2_0", "0,33:1", "2,00 m", "6,00 × 3,75 m",
     "È l'ottica giusta per la distanza di 2,0 m: l'immagine copre la parete in larghezza, al centimetro. "
     "In altezza avanzano 12,5 cm sopra e 12,5 cm sotto (il 16:10 è più alto della parete): una piccola "
     "abbondanza utile come margine di regolazione, da mascherare nel contenuto."),
    ("0_50_dist_2_0", "0,5:1", "2,00 m", "4,00 × 2,50 m",
     "L'immagine è troppo piccola: a 2,0 m non copre la parete e restano fasce scure su tutti i lati. "
     "Per usarla i proiettori andrebbero a 3,0 m dalla parete, cioè nella metà opposta del cubo, "
     "dove i fasci si incrociano e le persone fanno ombra."),
    ("0_50_dist_3_0_girandola", "0,5:1 a girandola", "3,00 m", "6,00 × 3,75 m",
     "Per coprire la parete con l'ottica 0,5:1 le ottiche dovrebbero stare tutte al centro esatto del cubo. "
     "I proiettori sono quindi spostati di 0,40 m di lato, a girandola, e l'immagine è ricentrata con il "
     "lens shift orizzontale (circa 7%). La copertura è completa, ma ogni fascio parte inclinato verso il "
     "basso e passa vicino ai corpi degli altri proiettori: si vedono le loro ombre nella parte alta delle "
     "pareti. Pianta della disposizione nei disegni tecnici."),
    ("0_80_dist_2_0", "0,8:1", "2,00 m", "2,50 × 1,56 m",
     "Ottica corta classica, con i proiettori fermi al centro: l'immagine è di soli 2,50 × 1,56 m, "
     "meno di un quinto della parete. Questa ottica non è adatta alla disposizione centrale."),
    ("0_80_dist_4_8", "0,8:1", "4,80 m", "6,00 × 3,75 m",
     "Per coprire la parete con l'ottica 0,8:1 il proiettore deve stare a 4,80 m, cioè dalla parte opposta "
     "del cubo (a 1,20 m dalla parete alle sue spalle). I fasci attraversano tutta la sala all'altezza delle "
     "teste e si incrociano al centro: chi è dentro il cubo fa ombra sulle pareti. È il confronto che "
     "spiega perché conviene l'ottica ultra-corta al centro."),
]

def figura(nome, didascalia, classe=""):
    if not esiste(nome):
        return f'<div class="manca">Render mancante: {html.escape(nome)}</div>'
    return (f'<figure class="{classe}"><img src="file://{img(nome)}">'
            f'<figcaption>{didascalia}</figcaption></figure>')

pagine = []

# ---------------------------------------------------------------- copertina
pagine.append(f'''
<section class="copertina">
  <div class="sopra">Futura Network &nbsp;·&nbsp; per Music Box</div>
  <h1>Cubo Immersivo</h1>
  <p class="sotto">Distinta tecnica: struttura, disposizione dei proiettori,<br>vedute di progetto e confronto delle ottiche</p>
  {figura("render_con_porta_Camera_esterna_3-4.png", "", "copfig")}
  <div class="data">29 ottobre 2026 &nbsp;·&nbsp; Adriano Lombardo</div>
</section>''')

# ---------------------------------------------------------------- il progetto
pagine.append('''
<section>
  <h2>1. Il progetto</h2>
  <div class="due">
    <div>
      <p>Un ambiente immersivo a pianta quadrata: le pareti interne sono superfici di proiezione,
      pavimento e soffitto sono specchi affacciati che moltiplicano all'infinito le immagini verso
      l'alto e verso il basso. Il pubblico entra da una porta (o da un lato aperto, nella versione senza porta)
      e si trova dentro il contenuto.</p>
      <table>
        <tr><th>Pianta interna</th><td>6,00 × 6,00 m</td></tr>
        <tr><th>Altezza interna</th><td>3,50 m</td></tr>
        <tr><th>Pareti proiettate</th><td>sinistra, fondo, destra (6,00 × 3,50 m ciascuna)<br>
            + parete d'ingresso nella versione con porta</td></tr>
        <tr><th>Finitura pareti</th><td>pannelli verniciati bianco opaco</td></tr>
        <tr><th>Pavimento</th><td>specchio calpestabile, lastre 1 × 1 m con fuga di 3 mm</td></tr>
        <tr><th>Soffitto</th><td>specchio a lastre 1 × 1 m, montato sotto il pannello di legno del tetto</td></tr>
        <tr><th>Tetto</th><td>pannello in legno multistrato, regge proiettori e staffe</td></tr>
        <tr><th>Porta</th><td>vano 1,00 × 2,20 m al centro della parete d'ingresso, anta apribile verso l'esterno</td></tr>
        <tr><th>Proiettori</th><td>3 (senza porta) o 4 (con porta), ottica ultra-corta, appesi al tetto con staffe;
            nessuna americana</td></tr>
        <tr><th>Riferimento di scala</th><td>manichini alti 1,75 m</td></tr>
      </table>
    </div>
    <div>
      <h3>Due versioni</h3>
      <p><b>Con porta</b> &mdash; il cubo è chiuso su quattro lati. Si entra dalla porta e anche la parete
      d'ingresso è proiettata, con un quarto proiettore: l'immersione è completa a 360°.</p>
      <p><b>Senza porta</b> &mdash; il lato d'ingresso è completamente aperto. Tre pareti proiettate,
      accesso libero, ingresso e uscita più rapidi per il pubblico.</p>
      <h3>Come leggere i render</h3>
      <p>Le <b>vedute realistiche</b> mostrano l'effetto finale con un contenuto di prova, simile a un
      generativo Notch. I render delle <b>zone di proiezione</b> mostrano invece solo la luce dei
      proiettori su superfici neutre, con una griglia di test: servono a capire dove arriva l'immagine,
      quanto deborda e dove cadono le ombre.</p>
    </div>
  </div>
</section>''')

# ---------------------------------------------------------------- proiettori
pagine.append(f'''
<section>
  <h2>2. Disposizione dei proiettori</h2>
  <div class="due">
    <div>
      <p>I proiettori sono raggruppati al centro del cubo, schiena contro schiena, ognuno rivolto verso
      la propria parete e tutti alla <b>stessa distanza di 2,00 m</b> dalla parete che proiettano.
      Ognuno è sull'asse centrale della sua parete: la disposizione è simmetrica e l'immagine arriva
      dritta, senza trapezio (la centratura in altezza si fa con il lens shift dell'ottica).</p>
      <table>
        <tr><th>Proiettore</th><th>Parete</th><th>Posizione dell'ottica</th></tr>
        <tr><td>P3</td><td>sinistra</td><td>1,00 m a sinistra del centro</td></tr>
        <tr><td>P1</td><td>destra</td><td>1,00 m a destra del centro</td></tr>
        <tr><td>P2</td><td>fondo</td><td>1,00 m verso il fondo dal centro</td></tr>
        <tr><td>P4</td><td>ingresso (solo con porta)</td><td>1,00 m verso l'ingresso dal centro</td></tr>
      </table>
      <p>Quota dell'asse ottico: 3,20 m (30 cm sotto il tetto). Staffa verticale con piastra fissata al
      pannello di legno.</p>
      <p><b>Perché al centro.</b> Con i proiettori rivolti verso l'esterno nessun fascio attraversa un altro
      proiettore e il percorso della luce è corto: le persone fanno ombra solo quando si avvicinano molto
      alla parete. Nei riflessi degli specchi proiettori e staffe vanno mascherati (nei render sono nascosti).</p>
    </div>
    <div>{figura("zone_ottica_0_33_dist_2_0_pianta.png", "Pianta dall'alto, ottica 0,33:1: i quattro fasci partono dal centro verso le pareti.")}</div>
  </div>
</section>''')

# ---------------------------------------------------------------- disegni tecnici
def disegno(nome):
    return f'<img class="disegno" src="file://{os.path.join(QUI, "disegni", nome)}">'

pagine.append(f'''
<section>
  <h2>3. Disegni tecnici &mdash; pianta, versione con porta <span class="sub">scala 1:50 circa su A4 · misure in metri</span></h2>
  <div class="dis">
    {disegno("01_pianta_con_porta.svg")}
    <div class="nota">
      <h3>Legenda</h3>
      <p>Pareti in nero, spessore 0,10 m. Le linee colorate sul filo interno delle pareti sono le superfici
      proiettate; i triangoli sono i coni di proiezione in pianta (ottica 0,33:1, immagine larga 6,00 m).</p>
      <p>Il reticolo grigio è la divisione delle lastre a specchio del pavimento (1 × 1 m).</p>
      <p>I proiettori sono a croce al centro: ogni ottica è a 2,00 m dalla propria parete e a 1,00 m dal
      centro del cubo. In rosso la traccia della sezione A-A.</p>
      <p>Porta 1,00 × 2,20 m al centro della parete d'ingresso, anta apribile verso l'esterno.</p>
    </div>
  </div>
</section>
<section>
  <h2>3. Disegni tecnici &mdash; pianta, versione senza porta <span class="sub">scala 1:50 circa su A4 · misure in metri</span></h2>
  <div class="dis">
    {disegno("02_pianta_senza_porta.svg")}
    <div class="nota">
      <h3>Versione senza porta</h3>
      <p>Il lato d'ingresso è aperto per tutti i 6,00 m. Tre proiettori (P1, P2, P3), con la stessa
      disposizione della versione con porta: il quarto proiettore non c'è.</p>
    </div>
  </div>
</section>
<section>
  <h2>3. Disegni tecnici &mdash; sezione A-A <span class="sub">scala 1:50 circa su A4 · misure in metri</span></h2>
  <div class="dis">
    {disegno("03_sezione_AA.svg")}
    <div class="nota">
      <h3>Sezione longitudinale</h3>
      <p>Sezione al centro del cubo, dall'ingresso (a sinistra) al fondo (a destra).</p>
      <p>Altezza interna 3,50 m; base del pavimento 0,10 m, pannello del tetto 0,08 m.
      Specchi in azzurro su pavimento e soffitto.</p>
      <p>Asse ottico a 3,20 m. L'immagine (3,75 m di altezza) è centrata sulla parete con il lens shift:
      supera di 0,125 m il soffitto e il pavimento.</p>
      <p>Il manichino è alto 1,75 m: i fasci passano sopra la testa per buona parte del percorso.</p>
    </div>
  </div>
</section>
<section>
  <h2>3. Disegni tecnici &mdash; prospetti delle pareti <span class="sub">scala 1:100 circa · misure in metri</span></h2>
  <div class="due">
    <div>{disegno("04_prospetto_fondo.svg")}<p class="didas">Parete di fondo (uguale per le pareti laterali):
      la griglia 16 × 10 è l'immagine del proiettore, in rosso l'abbondanza su soffitto e pavimento.</p></div>
    <div>{disegno("05_prospetto_ingresso.svg")}<p class="didas">Parete d'ingresso (solo versione con porta):
      il vano della porta 1,00 × 2,20 m resta all'interno dell'immagine e va mascherato nel contenuto.</p></div>
  </div>
</section>
<section>
  <h2>3. Disegni tecnici &mdash; proiettore e staffa</h2>
  <div class="dis">
    {disegno("06_dettaglio_proiettore.svg")}
    <div class="nota">
      <h3>Coordinate delle ottiche</h3>
      <p>Origine al centro del pavimento, X verso destra, Y verso il fondo, Z verso l'alto.</p>
      <table>
        <tr><th></th><th>X</th><th>Y</th><th>Z</th><th>rivolto verso</th></tr>
        <tr><td>P1</td><td>+1,00</td><td>0,00</td><td>3,20</td><td>destra</td></tr>
        <tr><td>P2</td><td>0,00</td><td>+1,00</td><td>3,20</td><td>fondo</td></tr>
        <tr><td>P3</td><td>&minus;1,00</td><td>0,00</td><td>3,20</td><td>sinistra</td></tr>
        <tr><td>P4</td><td>0,00</td><td>&minus;1,00</td><td>3,20</td><td>ingresso</td></tr>
      </table>
      <p>Piastra della staffa al centro del corpo, 0,255 m dietro l'ottica (per P1: X = +0,745).</p>
    </div>
  </div>
</section>''')

# ---------------------------------------------------------------- vedute realistiche
pagine.append(f'''
<section>
  <h2>4. Vedute realistiche &mdash; versione con porta</h2>
  <div class="griglia2">
    {figura("render_con_porta_Camera_esterna_3-4.png", "Esterno: il cubo chiuso nel padiglione, la luce esce solo dalla porta.")}
    {figura("render_con_porta_Camera_ingresso.png", "Arrivo alla porta.")}
    {figura("render_con_porta_Camera_interna.png", "Interno verso la parete di fondo: pareti proiettate e riflesso infinito tra pavimento e soffitto.")}
    {figura("render_con_porta_Camera_verso_porta.png", "Interno verso l'ingresso: anche la parete con la porta è proiettata (quarto proiettore).")}
  </div>
</section>''')
pagine.append(f'''
<section>
  <h2>5. Vedute realistiche &mdash; versione senza porta</h2>
  <div class="griglia2">
    {figura("render_senza_porta_Camera_esterna_3-4.png", "Esterno: il lato d'ingresso è aperto.")}
    {figura("render_senza_porta_Camera_ingresso.png", "Vista dall'ingresso aperto.")}
    {figura("render_senza_porta_Camera_interna.png", "Interno verso la parete di fondo.")}
    <div class="nota">
      <h3>Differenze rispetto alla versione con porta</h3>
      <p>Tre proiettori invece di quattro. Il lato aperto lascia entrare la luce del padiglione, che
      riduce un po' il contrasto delle proiezioni; dall'esterno si vede l'interno. Il flusso di pubblico è
      più semplice, ma l'immersione non è a 360°.</p>
    </div>
  </div>
</section>''')

# ---------------------------------------------------------------- confronto ottiche
pagine.append('''
<section>
  <h2>6. Confronto delle ottiche</h2>
  <p>Proiettori fermi nella stessa posizione (2,00 m dalla parete) con ottiche diverse; in più, l'ottica
  corta 0,8:1 alla distanza che le serve per coprire la parete (4,80 m).
  La larghezza dell'immagine è <b>distanza ÷ rapporto di tiro</b>; il formato è 16:10 (WUXGA), il più
  comune nei proiettori da installazione. L'immagine <b>non è ritagliata</b>: quello che eccede la parete
  cade su pavimento, soffitto e pareti vicine, come succederebbe davvero.</p>
  <table class="larga">
    <tr><th>Ottica (rapporto di tiro)</th><th>Distanza</th><th>Immagine</th><th>Su parete 6,00 × 3,50 m</th></tr>
    <tr><td>0,25:1</td><td>2,00 m</td><td>8,00 × 5,00 m</td><td>deborda di 1,00 m per lato e 0,75 m sopra e sotto</td></tr>
    <tr class="ok"><td>0,33:1</td><td>2,00 m</td><td>6,00 × 3,75 m</td><td>esatta in larghezza, 12,5 cm sopra e sotto &mdash; <b>consigliata</b></td></tr>
    <tr><td>0,5:1</td><td>2,00 m</td><td>4,00 × 2,50 m</td><td>non copre: mancano 1,00 m per lato e 0,50 m sopra e sotto</td></tr>
    <tr><td>0,5:1 a girandola</td><td>3,00 m</td><td>6,00 × 3,75 m</td><td>copre, ma i proiettori al centro si fanno ombra a vicenda</td></tr>
    <tr><td>0,8:1</td><td>2,00 m</td><td>2,50 × 1,56 m</td><td>copre meno di un quinto della parete</td></tr>
    <tr><td>0,8:1</td><td>4,80 m</td><td>6,00 × 3,75 m</td><td>copre, ma i proiettori vanno dalla parte opposta: fasci incrociati e ombre</td></tr>
  </table>
  <h3>Legenda dei render</h3>
  <p>Ogni proiettore ha un colore: <span class="c ar">arancio</span> = parete sinistra,
  <span class="c ve">verde</span> = fondo, <span class="c az">azzurro</span> = destra,
  <span class="c ma">magenta</span> = ingresso. Ogni fascio proietta una griglia 16 × 10 con cornice e croce
  centrale: dove la griglia si piega su pavimento o soffitto c'è abbondanza; dove due colori si mescolano
  i fasci si sovrappongono; le zone scure sono ombre (persone, porta) o parti non coperte.
  Una leggera foschia rende visibili i fasci nell'aria.</p>
</section>''')

for chiave, rt, dist, dim, testo in OTTICHE:
    if "girandola" in chiave:
        pagine.append(f'''
<section>
  <h2>Variante: ottica 0,5:1 a girandola &mdash; pianta <span class="sub">scala 1:50</span></h2>
  <div class="dis">{disegno("07_pianta_girandola_0_5.svg")}
    <div class="nota"><h3>Disposizione</h3><p>Ottiche a 3,00 m dalla parete, ciascuna spostata di 0,40 m di
    lato rispetto al centro: i corpi non si toccano, ma sono uno accanto all'altro nel percorso dei fasci.</p></div>
  </div>
</section>''')
    pagine.append(f'''
<section>
  <h2>Ottica {rt} &nbsp;<span class="sub">distanza {dist} · immagine {dim}</span></h2>
  <div class="griglia2">
    {figura(f"zone_ottica_{chiave}_interna.png", "Interno verso il fondo.")}
    {figura(f"zone_ottica_{chiave}_verso_porta.png", "Interno verso l'ingresso.")}
    {figura(f"zone_ottica_{chiave}_pianta.png", "Pianta dall'alto.")}
    <div class="nota"><h3>Cosa si vede</h3><p>{testo}</p></div>
  </div>
</section>''')

# ---------------------------------------------------------------- note
pagine.append('''
<section>
  <h2>7. Note e indicazioni</h2>
  <div class="due">
    <div>
      <h3>Scelta dell'ottica</h3>
      <p>Con i proiettori al centro a 2,00 m serve un rapporto di tiro di circa <b>0,33:1</b>.
      In fase di scelta conviene un'ottica ultra-corta con zoom o un piccolo margine (circa 0,30&ndash;0,36:1)
      e un lens shift verticale sufficiente a portare l'immagine da quota 0 a 3,50 m con l'ottica a 3,20 m.
      I valori di questa distinta sono geometrici: vanno verificati sulle schede tecniche del proiettore
      e dell'ottica scelti (rapporto di tiro reale, range di lens shift, distanza minima di messa a fuoco).</p>
      <h3>Abbondanza e mascheratura</h3>
      <p>Una piccola abbondanza è utile per allineare l'immagine; la parte che esce dalla parete va resa
      nera nel contenuto (maschera in Notch o nel media server), altrimenti si vede sugli specchi e si
      moltiplica nei riflessi.</p>
    </div>
    <div>
      <h3>Ombre</h3>
      <p>Con i proiettori al centro, rivolti verso l'esterno, il fascio fa solo 2 m: chi sta nella zona
      centrale non fa ombra. L'ombra compare solo se una persona si avvicina molto alla parete.</p>
      <h3>Angoli e porta</h3>
      <p>Negli angoli i bordi di due immagini si incontrano: va previsto l'allineamento preciso (o un
      leggero edge blending). Nella versione con porta il vano 1,00 × 2,20 m resta senza immagine e
      la luce del quarto proiettore esce dalla porta: si può mascherare il vano nel contenuto.</p>
      <h3>Specchi</h3>
      <p>Proiettori e staffe sono visibili nei riflessi di pavimento e soffitto: vanno verniciati di nero
      opaco o schermati.</p>
    </div>
  </div>
  <p class="piede">Scena 3D e render: Blender (Cycles). File di progetto: cubo_immersivo_con_porta.blend,
  cubo_immersivo_senza_porta.blend &mdash; le misure si modificano in cima allo script cubo_immersivo.py.</p>
</section>''')

CSS = '''
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Helvetica Neue", Arial, sans-serif; color: #1c1c22; font-size: 10.5pt; line-height: 1.45; }
section { width: 297mm; height: 210mm; padding: 14mm 16mm; page-break-after: always; overflow: hidden; position: relative; }
h1 { font-size: 46pt; margin: 6mm 0 2mm; letter-spacing: -0.5pt; }
h2 { font-size: 19pt; margin: 0 0 5mm; border-bottom: 2px solid #6b3fd4; padding-bottom: 2mm; }
h2 .sub { font-size: 12pt; color: #666; font-weight: normal; }
h3 { font-size: 11.5pt; margin: 3mm 0 1.5mm; color: #3a2490; }
p { margin: 0 0 2.5mm; }
.copertina { background: #0d0c14; color: #eee; }
.copertina .sopra { color: #b9a6ff; letter-spacing: 1pt; text-transform: uppercase; font-size: 10pt; }
.copertina .sotto { font-size: 13pt; color: #cfcfe0; margin-bottom: 5mm; }
.copertina .data { position: absolute; bottom: 10mm; left: 16mm; color: #999; }
.copfig img { width: 150mm; position: absolute; right: 16mm; bottom: 18mm; border-radius: 2mm; }
.copfig figcaption { display: none; }
.due { display: grid; grid-template-columns: 1fr 1fr; gap: 9mm; }
.griglia2 { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm 6mm; }
figure { margin: 0; }
figure img { width: 100%; display: block; border-radius: 1.5mm; }
figcaption { font-size: 9pt; color: #555; margin-top: 1mm; }
table { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 2mm 0 3mm; }
th, td { text-align: left; vertical-align: top; padding: 1.4mm 2mm; border-bottom: 1px solid #ddd; }
th { color: #3a2490; font-weight: 600; }
table.larga td, table.larga th { padding: 2mm 3mm; }
tr.ok td { background: #efeaff; }
.nota { background: #f4f2fa; border-radius: 2mm; padding: 4mm 5mm; }
.c { font-weight: 600; padding: 0 1.5mm; border-radius: 1mm; color: #fff; }
.ar { background: #e07a1e; } .ve { background: #3aa64a; } .az { background: #2a78d8; } .ma { background: #d23aa6; }
.dis { display: grid; grid-template-columns: 1fr 62mm; gap: 6mm; align-items: start; }
img.disegno { width: 100%; max-height: 165mm; object-fit: contain; display: block; }
.due img.disegno { max-height: 125mm; }
.didas { font-size: 9pt; color: #555; }
.manca { background: #fdecec; color: #a33; padding: 8mm; border-radius: 2mm; }
.piede { position: absolute; bottom: 9mm; left: 16mm; right: 16mm; font-size: 8.5pt; color: #888; }
'''

with open(os.path.join(QUI, "distinta.html"), "w") as f:
    f.write('<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Cubo Immersivo · Distinta</title>'
            f'<style>{CSS}</style></head><body>' + "".join(pagine) + "</body></html>")
print("Scritto", os.path.join(QUI, "distinta.html"))
