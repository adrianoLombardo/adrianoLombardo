import bpy, os

scena = bpy.context.scene
cartella = os.path.dirname(bpy.data.filepath)

# GPU se disponibile (RTX 4090)
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for tipo in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            for d in prefs.devices:
                d.use = True
            scena.cycles.device = "GPU"
            print("Render su GPU:", tipo)
            break
        except Exception:
            continue
except Exception as e:
    print("GPU non attivata, uso CPU:", e)

scena.cycles.samples = 1024
for nome in ("Camera_ingresso", "Camera_interna", "Camera_esterna_3-4"):
    cam = bpy.data.objects.get(nome)
    if cam is None:
        print("Camera mancante:", nome)
        continue
    scena.camera = cam
    scena.render.filepath = os.path.join(cartella, f"render_{nome}.png")
    bpy.ops.render.render(write_still=True)
    print("Render salvato:", scena.render.filepath)
