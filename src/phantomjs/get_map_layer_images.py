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
    print("command: ", " ".join(cmd))
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
    parser.add_argument("-n", "--name",
                        dest="layername",
                        default=None,
                        help="If given an image will only be generated for the given layername")
    args = parser.parse_args()

    if args.layername:
        layer_url = "{}?layer={}".format(args.mapurl, args.layername)
        result_filepath = create_map_layer_image(layer_url, args.layername, args.outputdir)
        print(result_filepath)
    else:
        # get JSON list from layers
        layers_data = json.loads(urlopen(args.layersurl).read().decode('utf-8'))
        for layer_data in layers_data:
            layer_url = "{}?layer={}".format(args.mapurl, layer_data["layername"])
            result_filepath = create_map_layer_image(layer_url, layer_data["layername"], args.outputdir)
            print(result_filepath)


