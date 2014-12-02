"""
Create png image of map given a url containing Layers
"""
import os
import json
from urllib.request import urlopen
import subprocess

def create_map_layer_image(url, layername, output_dir):
    output_filename = "{}.png".format(layername)
    output_filepath = os.path.join(os.path.abspath(output_dir), output_filename)
    cmd = (
           "phantomjs",
           "./makepng.js",
           url,
           output_filepath
            )
    subprocess.check_call(cmd)
    return output_filepath


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-l", "--layersurl",
                        dest="layersurl",
                        default=None,
                        required=True,
                        help="URL of link to JSON map layers list")
    parser.add_argument("-m", "--mapurl",
                        dest="mapurl",
                        default=None,
                        required=True,
                        help="URL of map accepting '?layer=<layername>' querystring")
    parser.add_argument("-o", "--outputdir",
                        dest="outputdir",
                        default=".",
                        )
    args = parser.parse_args()

    # get JSON list from layers
    layers_data = json.loads(urlopen(args.layersurl).read().decode('utf-8'))
    for layer_data in layers_data:
        layer_url = "{}?layer={}".format(args.mapurl, layer_data["layername"])
        result_filepath = create_map_layer_image(layer_url, layer_data["layername"], args.outputdir)
        print(result_filepath)


