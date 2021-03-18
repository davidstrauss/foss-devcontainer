import pathlib
import string
import json
import os
import subprocess
import logging
import sys
import configparser

base_path = os.path.dirname(os.path.realpath(__file__))
buildconfig_tpl_path = os.path.join(base_path, "buildconfig.template")
buildconfig_tpl_str = pathlib.Path(buildconfig_tpl_path).read_text()
buildconfig_tpl = string.Template(buildconfig_tpl_str)

project_path = os.getcwd()  # Make configurable?
project_name = pathlib.Path(project_path).name.strip()


def init_logger():
    # From https://stackoverflow.com/a/46065766
    logger = logging.getLogger()
    h = logging.StreamHandler(sys.stdout)
    h.flush = sys.stdout.flush
    logger.addHandler(h)
    logger.setLevel(logging.DEBUG)
    return logger


logger = init_logger()


def run(cmd, buildah_unshare=False):
    if buildah_unshare:
        cmd = ["buildah", "unshare"] + cmd
    logger.info("Command: {}".format(cmd))
    cproc = subprocess.run(cmd, check=True, capture_output=True)
    output = cproc.stdout.strip()
    logger.info("Output: {}".format(output))
    return output


contained_id = run(["buildah", "from", "scratch"])
scratch_mnt = run(["buildah", "mount", contained_id], True)

devc_dir = os.path.join(os.getcwd(), ".devcontainer")
devc_config_path = os.path.join(devc_dir, "devcontainer.json")

devc_config_json = ""
with open(devc_config_path, "r") as devc_config_fp:
    for line in devc_config_fp.readlines():
        if not line.strip().startswith("//"):
            devc_config_json += line + "\n"
devc_config = json.loads(devc_config_json)

container_build_filename = devc_config["build"]["dockerfile"]
container_build_path = os.path.join(devc_dir, container_build_filename)

pb_output = run(
    ["podman", "build", "-t", project_name, "-f", container_build_path, "."]
)  # --build-arg
image_id = pb_output.splitlines()[-1].decode("utf-8").strip()

run(["podman", "stop", "--ignore", project_name])
run(["podman", "rm", "--ignore", project_name])
run(["podman", "run", "-P", "-d", "--name={}".format(project_name), image_id])

bldcfg = buildconfig_tpl.substitute(
    containerid=project_name, homedir=pathlib.Path.home(), project=project_name
)
config = configparser.ConfigParser()
config.read_string(bldcfg)
with open(".buildconfig", "w") as configfile:
    config.write(configfile)
    

ports = run(["podman", "port", project_name]).decode("utf-8").strip()

if len(ports) > 0:
    print("If there are any ports here, they're services from the container:")
    print(ports)
