# Art folder

This folder is for the textures, models and sounds of the art team. Nothing here is used by the game directly: each file is checked and then integrated into the mod.

## Folders

| Folder | Content |
|---|---|
| `blocks/` | Block textures (16 × 16; animations as vertical strips) |
| `items/` | Item textures (16 × 16) |
| `models/` | Blockbench models of blocks that are not plain cubes ("Java Block/Item") |
| `entities/<name>/` | Blockbench models of rovers, vehicles and other entities ("Modded Entity"), with their texture |
| `gui/` | Machine screen backgrounds |
| `gui/sprites/` | Shared GUI sprites and HUD icons |
| `armor/` | Space suit textures |
| `sky/` | Sun, Phobos and Deimos |
| `paintings/` | Paintings (16 pixels per block) |
| `sounds/` | Sounds (Ogg Vorbis, mono, 44.1 kHz) |
| `templates/` | Templates and guide images; see `docs/Template_Guide.pdf` |

## How to deliver

1. Save the file in the right folder, with a name in lowercase letters, digits and underscores (for example `solar_panel.png`).
2. To change a file that was already delivered, overwrite it with the new version under the same name.
3. In GitHub Desktop, write a short description of the change (for example "New door textures"), click **Commit to main**, then **Push origin**.

Work in progress is welcome: you can upload files before they are finished.
