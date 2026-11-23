# Mars Mod

A Minecraft mod developed for **The Martian Mindset**, Cluster of Excellence at the University of Bremen. It adds a Mars dimension with its own terrain, resources, machines and survival mechanics, to communicate the Cluster's research to a young audience.

- **Minecraft:** Java Edition 26.2
- **Mod loader:** NeoForge

## Repository structure

| Folder | Content | Who works here |
|---|---|---|
| `src/` | Source code and the integrated game assets | Programming |
| `art/` | Textures, models and sounds as delivered by the art team | Art |
| `art/templates/` | Templates for the art team | — |
| `docs/` | Project documentation | Both |

The art team only works in `art/`. Files there are reviewed and then integrated into `src/main/resources/`, so the art team never has to change anything in `src/`.

## Building

Requirements: a JDK to run Gradle (17 or newer). The mod itself targets **Java 25**; Gradle downloads it automatically if it is not installed.

| Command | What it does |
|---|---|
| `gradlew build` | Builds the mod; the jar is in `build/libs/` |
| `gradlew runClient` | Starts Minecraft with the mod |
| `gradlew runServer` | Starts a dedicated server with the mod |
| `gradlew runData` | Generates data files into `src/generated/resources/` |

On Linux and macOS, use `./gradlew`. The versions of Minecraft, NeoForge and the mod are set in `gradle.properties`.

## License

The code is released under the MIT License (see `LICENSE`). The build files are based on the NeoForge MDK (see `TEMPLATE_LICENSE.txt`).
