"""Generates the world generation files of the Mars dimension.

The terrain shape and the biome placement are taken from vanilla Minecraft 26.2, so that every
Mars biome sits on the kind of terrain it is named after (peaks on the mountains, plains on flat
land). Only the blocks, the biomes and the fluids are changed.

Inputs (from Minecraft 26.2, not stored in the repository):
  VANILLA_DATA  folder with data/minecraft/... extracted from the Minecraft jar
                (dimension_type/overworld.json, worldgen/noise_settings/overworld.json)
  BIOME_REPORT  reports/biome_parameters/minecraft/overworld.json, made with
                java -DbundlerMainClass=net.minecraft.data.Main -jar server.jar --reports

Usage:
  python generate_mars_worldgen.py VANILLA_DATA BIOME_REPORT
Writes into src/main/resources/data/marsmod/.
"""
import json
import os
import sys

M = "marsmod"
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.path.join(ROOT, "src", "main", "resources", "data", M)
SKY = "#c99656"   # Mars day sky from the item list; placeholder until the sky of Work Package 2

# Vanilla biome -> Mars biome. Vanilla cave biomes are left out (the caves follow in step 4).
BIOME_MAP = {
    "plains": [
        "plains", "sunflower_plains", "mushroom_fields",
        "ocean", "cold_ocean", "lukewarm_ocean", "warm_ocean", "swamp", "mangrove_swamp",
    ],
    # the deep vanilla oceans too, so that the dry ocean basins are not all plains
    "cracked_plains": ["desert", "savanna", "savanna_plateau", "deep_ocean", "deep_cold_ocean", "deep_lukewarm_ocean"],
    # the whole cold zone, so that it is not dotted with hills
    "ice_plains": ["snowy_plains", "ice_spikes", "snowy_taiga", "frozen_ocean", "deep_frozen_ocean"],
    "hills": [
        "forest", "flower_forest", "birch_forest", "old_growth_birch_forest", "dark_forest", "pale_garden",
        "taiga", "old_growth_pine_taiga", "old_growth_spruce_taiga",
        "jungle", "sparse_jungle", "bamboo_jungle", "meadow", "cherry_grove",
    ],
    "jagged_peaks": ["jagged_peaks", "stony_peaks"],
    "frozen_peaks": ["frozen_peaks", "snowy_slopes", "grove"],
    "windswept_hills": ["windswept_hills", "windswept_gravelly_hills", "windswept_forest", "windswept_savanna"],
    # all three vanilla badlands, as they are rare
    "eroded_badlands": ["eroded_badlands", "badlands", "wooded_badlands"],
}
CAVE_BIOMES = {"dripstone_caves", "lush_caves", "deep_dark", "sulfur_caves"}
# Thin strips in vanilla (rivers along the valleys, beaches and shores along the coast). They are left out,
# so that these places take the biome around them instead of crossing it as a narrow line.
STRIP_BIOMES = {"river", "frozen_river", "beach", "snowy_beach", "stony_shore"}


def write(rel, obj, indent=2):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=indent)
        f.write("\n")


# ---------- surface rule helpers ----------
def block(name):
    return {"type": "minecraft:block", "result_state": {"Name": f"{M}:{name}"}}


def cond(test, then):
    return {"type": "minecraft:condition", "if_true": test, "then_run": then}


def seq(*rules):
    return {"type": "minecraft:sequence", "sequence": list(rules)}


def depth(surface="floor", offset=0, add_surface_depth=False):
    return {"type": "minecraft:stone_depth", "offset": offset, "surface_type": surface,
            "add_surface_depth": add_surface_depth, "secondary_depth_range": 0}


def noise(lo, hi):
    return {"type": "minecraft:noise_threshold", "noise": "minecraft:surface", "min_threshold": lo, "max_threshold": hi}


def biome_is(name):
    return {"type": "minecraft:biome", "biome_is": [f"{M}:{name}"]}


def y_above(y):
    return {"type": "minecraft:y_above", "anchor": {"absolute": y}, "surface_depth_multiplier": 0, "add_stone_depth": False}


STEEP = {"type": "minecraft:steep"}
# no ice above this height (uneven line). In the 3.2 km test, 90 % of the ice plains were below y 69.
ICE_LINE = {"type": "minecraft:y_above", "anchor": {"absolute": 75}, "surface_depth_multiplier": 2, "add_stone_depth": False}
# height of the dust cap on the frozen peaks; uneven line. To be adjusted with the huge mountains of step 3.
DUST_LINE = {"type": "minecraft:y_above", "anchor": {"absolute": 120}, "surface_depth_multiplier": 4, "add_stone_depth": False}
TOP = depth()                                    # the top block
UNDER = depth(add_surface_depth=True)            # the top 3 to 6 blocks
CEILING = depth("ceiling")                       # the block above a cave or overhang


def badlands_bands():
    """Layers of rock and dry regolith, like the coloured bands of vanilla badlands."""
    pattern = [("rock", 4), ("regolith_dry", 2), ("rock", 3), ("regolith_dry", 1),
               ("rock", 5), ("regolith_dry", 2), ("rock", 2), ("regolith_dry", 3)]
    bands, y, i = [], 50, 0
    while y < 420:
        name, thickness = pattern[i % len(pattern)]
        bands.append((y, name))
        y += thickness
        i += 1
    # the first rule that matches wins, so start with the highest band
    return seq(*[cond(y_above(y), block(name)) for y, name in reversed(bands)])


BIOME_RULES = {
    # loose regolith, like sand
    "plains": seq(cond(TOP, block("regolith_loose")), cond(CEILING, block("rock")), cond(UNDER, block("regolith_loose"))),
    # dry regolith with the cracked top
    "cracked_plains": seq(cond(TOP, block("regolith_dry")), cond(CEILING, block("rock")), cond(UNDER, block("regolith_loose"))),
    # mostly ice, with a few patches of dry regolith. Ice only on low, flat ground: the vanilla snowy plains
    # also climb the flanks of mountains, where ice looked like snow. Steep slopes: rock; higher up: dry regolith.
    "ice_plains": seq(cond(STEEP, cond(UNDER, block("rock"))),
                      cond(TOP, seq(cond(ICE_LINE, block("regolith_dry")),
                                    cond(noise(-0.55, 10.0), block("ice")),
                                    block("regolith_dry"))),
                      cond(CEILING, block("rock")), cond(UNDER, block("regolith_loose"))),
    # cracked regolith with patches of loose regolith and rock outcrops; bare rock on steep slopes
    "hills": seq(cond(STEEP, cond(UNDER, block("rock"))),
                 cond(TOP, seq(cond(noise(0.45, 10.0), block("rock")),
                               cond(noise(-10.0, -0.25), block("regolith_loose")),
                               block("regolith_dry"))),
                 cond(CEILING, block("rock")), cond(UNDER, block("regolith_loose"))),
    # bare rock, a little loose regolith on the flatter parts
    "jagged_peaks": seq(cond(STEEP, cond(UNDER, block("rock"))), cond(TOP, cond(noise(0.3, 10.0), block("regolith_loose")))),
    # no ice (as in the item list): rock, with a cap of dust (dry regolith) on the high parts, where vanilla has snow
    "frozen_peaks": seq(cond(STEEP, cond(UNDER, block("rock"))),
                        cond(DUST_LINE, seq(cond(TOP, block("regolith_dry")), cond(UNDER, block("regolith_dry"))))),
    # patches of rock, dry and loose regolith
    "windswept_hills": seq(cond(UNDER, seq(cond(noise(0.25, 10.0), block("rock")),
                                           cond(TOP, seq(cond(noise(-10.0, -0.25), block("regolith_dry")), block("regolith_loose"))),
                                           cond(CEILING, block("rock")), block("regolith_loose")))),
    # bands of rock and regolith, also on the pillars
    "eroded_badlands": seq(cond(TOP, block("regolith_dry")), badlands_bands()),
}


def main():
    vanilla, report = sys.argv[1], sys.argv[2]

    # dimension type: vanilla overworld (day cycle, height) with the Mars sky
    dt = json.load(open(os.path.join(vanilla, "data/minecraft/dimension_type/overworld.json")))
    dt["attributes"].pop("minecraft:gameplay/nether_portal_spawns_piglin", None)
    dt["attributes"]["minecraft:visual/sky_color"] = SKY
    dt["attributes"]["minecraft:visual/fog_color"] = SKY
    write("dimension_type/mars.json", dt)

    # noise settings: vanilla terrain shape, Mars blocks, no water, no lava, no ores, no mobs
    ns = json.load(open(os.path.join(vanilla, "data/minecraft/worldgen/noise_settings/overworld.json")))
    ns["default_block"] = {"Name": f"{M}:rock"}
    ns["default_fluid"] = {"Name": "minecraft:air"}
    ns["aquifers_enabled"] = False
    ns["ore_veins_enabled"] = False
    ns["disable_mob_generation"] = True
    # vanilla fills every cave below min(-54, sea_level) with lava; sea level at the bottom: no lava
    ns["sea_level"] = -64

    def find_bedrock(o):
        if isinstance(o, dict):
            if o.get("type") == "minecraft:condition" and isinstance(o.get("if_true"), dict) \
                    and o["if_true"].get("random_name") == "minecraft:bedrock_floor":
                return o
            o = list(o.values())
        if isinstance(o, list):
            for v in o:
                r = find_bedrock(v)
                if r:
                    return r
        return None

    bedrock = find_bedrock(ns["surface_rule"])
    assert bedrock, "bedrock rule not found"
    ns["surface_rule"] = seq(
        bedrock,
        # only near the real surface, not on cave floors
        cond({"type": "minecraft:above_preliminary_surface"},
             seq(*[cond(biome_is(b), rule) for b, rule in BIOME_RULES.items()])),
    )
    write("worldgen/noise_settings/mars.json", ns)

    # biomes
    for b in BIOME_MAP:
        write(f"worldgen/biome/{b}.json", {
            "attributes": {"minecraft:visual/sky_color": SKY},
            "carvers": [], "downfall": 0.0, "effects": {"water_color": "#3f76e4"}, "features": [],
            "has_precipitation": False, "spawn_costs": {}, "spawners": {}, "temperature": 2.0,
        })

    # biome placement: the vanilla overworld parameters, with the Mars biomes
    lookup = {f"minecraft:{v}": f"{M}:{b}" for b, vs in BIOME_MAP.items() for v in vs}
    entries = []
    for e in json.load(open(report))["biomes"]:
        name = e["biome"]
        if name.removeprefix("minecraft:") in CAVE_BIOMES | STRIP_BIOMES:
            continue
        if name not in lookup:
            raise SystemExit(f"vanilla biome without a Mars biome: {name}")
        entries.append({"biome": lookup[name], "parameters": e["parameters"]})
    write("dimension/mars.json", {
        "type": f"{M}:mars",
        "generator": {"type": "minecraft:noise", "settings": f"{M}:mars",
                      "biome_source": {"type": "minecraft:multi_noise", "biomes": entries}},
    }, indent=None)
    print(f"{len(entries)} biome entries, {len(BIOME_MAP)} biomes")


if __name__ == "__main__":
    main()
