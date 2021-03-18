# FOSS .devcontainer

A support framework for using `.devcontainer` on Linux desktops. Let's start
with Buildah + Podman + Builder, but the project is open to contributions for
other IDE integrations.

## On Fedora Silverblue

### Setup

1. Install GNOME Builder:

       flatpak install flathub org.gnome.Builder

### Usage

1. In the CLI, change to the parent directory of `.devcontainer`.
1. Run the utility (which will *delete* any container with the same name as your project directory):

       python /path/to/here/makeitso.py

1. Restart GNOME Builder, if already open. (It doesn't seem to pick up on new
   Podman containers otherwise.)
1. Open the "Switch Surface" menu (top left).
1. "Build Preferences"
1. Application Runtime > All Runtimes > Containers > Podman > $YourProject

