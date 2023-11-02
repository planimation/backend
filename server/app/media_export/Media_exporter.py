
import sys
import os
import json


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import mp4_exporter
import png_exporter
import gif_exporter

def export_media(vfg_file, format, parameters):

    if parameters==None:
        raise Exception("Parameters not found")

    # Extract parameters
    startStep = int(parameters.get("startStep", 0))
    stopStep  = int(parameters.get("stopStep", 999999))
    # speed     = parameters.get("speed", 0)
    quality   = parameters.get("quality", "high")

    # Ensure start and stop are not negative
    startStep = max(0, startStep)
    stopStep = max(startStep, stopStep)
    if quality not in ["low", "medium", "high"]:
        quality = "high"

    if format == "mp4":
        return mp4_exporter.create_MP4(vfg_file, startStep, stopStep, quality)
    elif format == "png":
        return png_exporter.create_PNGs(vfg_file, startStep, stopStep)
    elif format == "gif":
        return gif_exporter.create_GIF(vfg_file, startStep, stopStep, quality)
    elif format == "webm":
        return "error"
    return "error"

