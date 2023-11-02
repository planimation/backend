import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO
import base64
import numpy as np
import zipfile
import os
import io
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

_START_DEFAULT = 0
_END_DEFAULT = 9999999

def apply_tint(image, color):
    r, g, b, a = np.rollaxis(image, axis=-1)
    r = np.clip(np.uint8(r * color[0]), 0, 255)
    g = np.clip(np.uint8(g * color[1]), 0, 255)
    b = np.clip(np.uint8(b * color[2]), 0, 255)
    tinted_image = np.stack([r, g, b, a], axis=-1)
    return tinted_image

def create_PNGs(vfg_file, startStep=_START_DEFAULT, stopStep=_END_DEFAULT):
    with open(vfg_file, 'r') as f:
        data = json.load(f)

    startStep = max(0, min(startStep, len(data['visualStages']) - 1))
    stopStep = max(startStep, min(stopStep, len(data['visualStages']) - 1))
    visual_stages = data['visualStages'][startStep:stopStep+1]

    max_x = max(max(s['x'] + s['width'] for s in stage['visualSprites']) for stage in data['visualStages'])
    max_y = max(max(s['y'] + s['height'] for s in stage['visualSprites']) for stage in data['visualStages'])

    image_table = {}
    tint_cache = {}

    image_keys = data.get("imageTable", {}).get("m_keys", [])
    image_values = data.get("imageTable", {}).get("m_values", [])
    
    for key, base64_str in zip(image_keys, image_values):
        try:
            image_data = base64.b64decode(base64_str)
            image = Image.open(BytesIO(image_data))
            image = image.convert("RGBA")
            image_table[key] = np.array(image)
        except:
            print(f"Warning: Skipping '{key}' because its base64 value could not be decoded.")
            continue

    png_file_objects = []

    for idx, stage in enumerate(visual_stages, start=startStep):
        fig, ax = plt.subplots()
        ax.axis('equal')
        ax.axis('off')
        ax.set_xlim([0, max_x])
        ax.set_ylim([0, max_y])
        
        for sprite in stage['visualSprites']:
            x, y, w, h = sprite['x'], sprite['y'], sprite['width'], sprite['height']
            color = (sprite['color']['r'], sprite['color']['g'], sprite['color']['b'], sprite['color']['a'])
            name = sprite['name']

            prefab_image = sprite.get('prefabimage', None)

            if prefab_image in image_table:
                cache_key = (prefab_image, tuple(color))
                
                if cache_key not in tint_cache:
                    image = np.array(image_table[prefab_image])
                    tinted_image = apply_tint(image, color)
                    tint_cache[cache_key] = tinted_image
                
                ax.imshow(tint_cache[cache_key], extent=[x, x+w, y, y+h], origin='upper')

            else:
                rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='none', facecolor=color)
                ax.add_patch(rect)
            
            if sprite['showname']:
                ax.text(x + w/2, y + h/2, name, ha='center', va='center')

        # Write images to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)

        buf.seek(0)
        png_file_objects.append(("state_{}.png".format(idx), buf))

    # Zip the generated PNG files
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zipf:
        for png_filename, png_file in png_file_objects:
            zipf.writestr(png_filename, png_file.getvalue())

    zip_buffer.seek(0)
    return zip_buffer
