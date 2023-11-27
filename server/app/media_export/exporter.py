import sys
import os
import json

import zipfile
import io

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.animation import FFMpegWriter

from matplotlib.animation import PillowWriter

from PIL import Image
from io import BytesIO
import base64
import numpy as np
import tempfile

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# A few constants
_STATES_PER_SECOND = 1.5  # Speed
_START_DEFAULT = 0
_END_DEFAULT = sys.maxsize
QUALITY_SETTINGS = {
    "low": {"interp_frames": 2},
    "medium": {"interp_frames": 6},
    "high": {"interp_frames": 10}
}

def export_media(vfg_file, format, parameters):

    if parameters==None:
        raise Exception("Parameters not found")

    # Extract parameters
    startStep = int(parameters.get("startStep", _START_DEFAULT))
    stopStep  = int(parameters.get("stopStep", _END_DEFAULT))
    # speed     = parameters.get("speed", 0)
    quality   = parameters.get("quality", "high")

    # Check validity of parameters received
    # Ensure start and stop are not negative
    startStep = max(0, startStep)
    stopStep = max(startStep, stopStep)
    if quality not in ["low", "medium", "high"]:
        quality = "high"

    if format in ["mp4", "png", "gif"]:
        # Start building file
        return create_media(vfg_file, format, startStep, stopStep, quality)
    elif format == "webm":
        return "error"
    return "error"

def apply_tint(image, color):
    r, g, b, a = np.rollaxis(image, axis=-1)
    r = np.clip(np.uint8(r * color[0]), 0, 255)
    g = np.clip(np.uint8(g * color[1]), 0, 255)
    b = np.clip(np.uint8(b * color[2]), 0, 255)
    tinted_image = np.stack([r, g, b, a], axis=-1)
    return tinted_image

# This class is used due to a bug in PillowWriter where the output gif does not loop
# More info can be found here: https://stackoverflow.com/questions/51512141/how-to-make-matplotlib-saved-gif-looping
class LoopingPillowWriter(PillowWriter):
    def finish(self):
        self._frames[0].save(
            self._outfile, save_all=True, append_images=self._frames[1:],
            duration=int(1000 / self.fps), loop=0)

# Main function to create file for desired media output
def create_media(vfg_file, format, startStep=_START_DEFAULT, stopStep=_END_DEFAULT, quality='high'):

    # Choose the settings based on the quality provided
    chosen_quality = QUALITY_SETTINGS.get(quality, QUALITY_SETTINGS["high"])
    num_interpolation_frames = chosen_quality["interp_frames"]

    with open(vfg_file, 'r') as f:
        data = json.load(f)

    startStep = max(0, min(startStep, len(data['visualStages']) - 1))
    stopStep = max(startStep, min(stopStep, len(data['visualStages']) - 1))
    visual_stages = data['visualStages'][startStep:stopStep+1]

    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.axis('off')

    max_x = max(max(s['x'] + s['width'] for s in stage['visualSprites']) for stage in data['visualStages'])
    max_y = max(max(s['y'] + s['height'] for s in stage['visualSprites']) for stage in data['visualStages'])

    ax.set_xlim([0, max_x])
    ax.set_ylim([0, max_y])

    sprites = {}
    last_positions = {}
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

    if format in ["mp4", "gif"]:
        def update(frame):
            ax.clear()
            ax.axis('equal')
            ax.axis('off')
            ax.set_xlim([0, max_x])
            ax.set_ylim([0, max_y])

            # Determine whether we're in the pause frames
            active_frames = len(visual_stages) * num_interpolation_frames
            if frame >= active_frames:
                stage = visual_stages[-1]  # Use the last visual stage
                interpolation_alpha = 1   # No need to interpolate for the pause frames
            else:
                interpolation_alpha = frame % num_interpolation_frames / (num_interpolation_frames - 1)
                stage_idx = frame // num_interpolation_frames
                stage = visual_stages[stage_idx]

            process_sprites(stage, last_positions, interpolation_alpha, image_table, tint_cache, ax, sprites)

        # add a few frames to ensure we can view the final state
        total_frames = len(visual_stages) * num_interpolation_frames + int(1 * num_interpolation_frames)
        fps = int(num_interpolation_frames * _STATES_PER_SECOND)

        # Create a tempFile, as FunctionAnimation cannot write to a BytesIO object (in-memory) and can only write to disk
        with tempfile.NamedTemporaryFile(delete=False, suffix="."+format) as tmpfile:
            tmpname = tmpfile.name

        if format == "mp4":
            ani = FuncAnimation(fig, update, frames=total_frames, repeat=False)
            writer = FFMpegWriter(fps=fps, bitrate=1800)
            ani.save(tmpname, writer=writer)
        elif format == "gif":
            ani = FuncAnimation(fig, update, frames=total_frames, repeat=True)
            writer = LoopingPillowWriter(fps=fps)
            ani.save(tmpname, writer=writer)
            
        # Read the content of the temporary file into a BytesIO object
        output = BytesIO()
        with open(tmpname, "rb") as f:
            output.write(f.read())
        output.seek(0)

        # Remove the temporary file
        os.remove(tmpname)

        return output


    elif format == "png":
        png_file_objects = []
        for idx, stage in enumerate(visual_stages, start=startStep):
            fig, ax = plt.subplots()
            ax.axis('equal')
            ax.axis('off')
            ax.set_xlim([0, max_x])
            ax.set_ylim([0, max_y])
            process_sprites(stage, last_positions, None, image_table, tint_cache, ax, sprites)

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


    




def process_sprites(stage, last_positions, interpolation_alpha, image_table, tint_cache, ax, sprites):
    for sprite in stage['visualSprites']:
        x, y, w, h = sprite['x'], sprite['y'], sprite['width'], sprite['height']
        color = (sprite['color']['r'], sprite['color']['g'], sprite['color']['b'], sprite['color']['a'])
        name = sprite['name']

        if name in last_positions and interpolation_alpha != None:
            x_last, y_last = last_positions[name]
            x = np.interp(interpolation_alpha, [0, 1], [x_last, x])
            y = np.interp(interpolation_alpha, [0, 1], [y_last, y])

        prefab_image = sprite.get('prefabimage', None)

        if prefab_image in image_table:
            cache_key = (prefab_image, tuple(color))  # Create a unique key for this image and color
            
            # Check if the tinted image is in the cache
            if cache_key not in tint_cache:
                image = np.array(image_table[prefab_image])
                tinted_image = apply_tint(image, color)
                
                # Save the tinted image to the cache
                tint_cache[cache_key] = tinted_image
            
            # Use the tinted image from the cache
            ax.imshow(tint_cache[cache_key], extent=[x, x+w, y, y+h], origin='upper')

        else:
            if name not in sprites:
                sprites[name] = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='none', facecolor=color)
                ax.add_patch(sprites[name])
            else:
                sprites[name].set_xy((x, y))
                sprites[name].set_facecolor(color)
                ax.add_patch(sprites[name])
        
        last_positions[name] = (x, y)

        if sprite['showname']:
            ax.text(x + w/2, y + h/2, name, ha='center', va='center')


