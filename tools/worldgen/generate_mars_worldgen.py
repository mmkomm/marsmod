"""Generates the world generation files of the Mars dimension.

The terrain shape and the biome placement are taken from vanilla Minecraft 26.2, so that every
Mars biome sits on the kind of terrain it is named after (peaks on the mountains, plains on flat
land). Only the blocks, the biomes and the fluids are changed.

Inputs (from Minecraft 26.2, not stored in the repository), made with the vanilla server jar:
  VANILLA_DATA  output folder of  java -DbundlerMainClass=net.minecraft.data.Main -jar server.jar --server --output OUT
                (contains data/minecraft/dimension_type and data/minecraft/worldgen, with the density functions)
  BIOME_REPORT  OUT/reports/biome_parameters/minecraft/overworld.json, from the same command with --reports

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

# ---------- huge mountains ----------
# Vanilla terrain: the surface is where depth = 0, with depth = gradient(y) + offset(x, z). The gradient falls
# by 3 / 384 per block, so the surface is at y = 128 + 128 * offset. Above the base height, the offset is
# stretched by MOUNTAIN_SCALE, so mountains are 2.5 times higher above it; lower land is unchanged.
MOUNTAIN_SCALE = 2.5
MOUNTAIN_BASE_Y = 96                      # terrain below this height keeps its vanilla shape
MIN_Y, HEIGHT = -64, 640                  # world height: vanilla -64..319, Mars -64..575
TOP_Y = MIN_Y + HEIGHT - 1
GRADIENT_PER_BLOCK = -3.0 / 384.0
VANILLA_TOP_SLIDE = (240, 256)            # vanilla fades the terrain out 80..64 blocks below its top (320)

# ---------- huge canyon ----------
# Part of the terrain (not a carver), so that it can be much wider and deeper than a vanilla canyon.
# Along the zero line of a large, slow noise the land is lowered by CANYON_DEPTH blocks (not below
# CANYON_FLOOR_Y); a second noise switches the canyons on in some regions only.
CANYON_DEPTH = 150                        # vanilla canyons are about 40 to 50 blocks deep
CANYON_FLOOR_Y = -30                       # lower than the vanilla canyons (y 10 and up), so that it is about 3 times deeper
CANYON_HALF_WIDTH = 0.05                  # in noise units: about 25 blocks to each side of the centre line
CANYON_REGION_THRESHOLD = 0.2             # higher: fewer canyons
CANYON_MEANDER_BLOCKS = 40.0              # how far the centre line is bent sideways
CANYON_ROUGHNESS = 0.012                  # irregular edges (in noise units, compare with the half width)
CANYON_WIDTH_VARIATION = 0.45             # the width changes by up to +-45 % along the canyon
CANYON_FLOOR_VARIATION = 8.0              # blocks up and down on the floor

# ---------- giant crater ----------
# spacing in chunks: one crater in each square of 150 x 150 chunks (2.4 x 2.4 km), on flat land only
CRATER = {"min_radius": 70, "max_radius": 120, "spacing": 150, "separation": 60}

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
    # see HOT_ZONE below
    "eroded_badlands": ["eroded_badlands", "badlands", "wooded_badlands"],
}
# Vanilla places the badlands as islands on the high ground of the desert zone, which looked like small
# circles. Instead, the whole hot zone is split by humidity, a noise that changes slowly: the drier part
# becomes eroded badlands, the rest cracked plains. Both are then large regions.
HOT_ZONE = {"desert", "badlands", "eroded_badlands", "wooded_badlands"}
HOT_ZONE_DRY = -0.1                       # vanilla humidity index 0 and 1
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
# height of the dust cap on the frozen peaks (uneven line): vanilla-like 120, stretched like the mountains
DUST_LINE = {"type": "minecraft:y_above", "anchor": {"absolute": 156}, "surface_depth_multiplier": 4, "add_stone_depth": False}
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


def vanilla_gradient():
    return {"type": "minecraft:y_clamped_gradient", "from_value": 1.5, "from_y": -64, "to_value": -1.5, "to_y": 320}


def mars_gradient():
    """The same slope as vanilla, over the whole height of the Mars world."""
    return {"type": "minecraft:y_clamped_gradient", "from_value": 1.5, "from_y": MIN_Y,
            "to_value": 1.5 + GRADIENT_PER_BLOCK * (TOP_Y + 1 - MIN_Y), "to_y": TOP_Y + 1}


def noise(name, scale=1.0):
    return {"type": "minecraft:noise", "noise": f"{M}:{name}", "xz_scale": scale, "y_scale": 0.0}


def clamp01(x):
    return {"type": "minecraft:clamp", "min": 0.0, "max": 1.0, "input": x}


def add(*args):
    out = args[0]
    for a in args[1:]:
        out = {"type": "minecraft:add", "argument1": out, "argument2": a}
    return out


def mul(a, b):
    return {"type": "minecraft:mul", "argument1": a, "argument2": b}


def huge_canyon_mask():
    """1 on the canyon floor, 0 outside; the walls are in between.

    The centre line is the zero line of a large noise. To look natural, the line is bent by a second
    noise (meanders), its edge is roughened by a small noise, its width changes along the canyon,
    and the walls have a ledge halfway down.
    """
    bent = {"type": "minecraft:shifted_noise", "noise": f"{M}:huge_canyon", "xz_scale": 1.0, "y_scale": 0.0,
            "shift_x": mul(CANYON_MEANDER_BLOCKS, noise("huge_canyon_warp_x")), "shift_y": 0.0,
            "shift_z": mul(CANYON_MEANDER_BLOCKS, noise("huge_canyon_warp_z"))}
    line = add({"type": "minecraft:abs", "argument": bent}, mul(CANYON_ROUGHNESS, noise("huge_canyon_rough")))
    width = {"type": "minecraft:clamp", "min": 0.5 * CANYON_HALF_WIDTH, "max": 2.0 * CANYON_HALF_WIDTH,
             "input": add(CANYON_HALF_WIDTH, mul(CANYON_HALF_WIDTH * CANYON_WIDTH_VARIATION, noise("huge_canyon_width")))}
    q = mul(line, {"type": "minecraft:invert", "argument": width})        # 0 on the centre line, 1 at the edge
    # outer wall down to 55 % of the depth, a ledge, then the inner wall down to the floor
    profile = add(mul(0.55, clamp01(add(4.0, mul(-4.0, q)))), mul(0.45, clamp01(add(2.0, mul(-4.0, q)))))
    region = clamp01(add(-CANYON_REGION_THRESHOLD * 10.0, mul(10.0, noise("huge_canyon_region"))))
    return mul(profile, region)


def write_mountain_functions(vanilla):
    df = os.path.join(vanilla, "data/minecraft/worldgen/density_function/overworld")
    base_offset = (MOUNTAIN_BASE_Y - 128) / 128.0
    # offset + (scale - 1) * max(0, offset - base): stretches only the land above the base height
    write("worldgen/density_function/mars/mountain_offset.json", {
        "type": "minecraft:flat_cache", "argument": {"type": "minecraft:cache_2d", "argument": {
            "type": "minecraft:add", "argument1": "minecraft:overworld/offset",
            "argument2": {"type": "minecraft:mul", "argument1": MOUNTAIN_SCALE - 1.0,
                          "argument2": {"type": "minecraft:max", "argument1": 0.0,
                                        "argument2": {"type": "minecraft:add", "argument1": "minecraft:overworld/offset",
                                                      "argument2": -base_offset}}}}}})
    # huge canyon: offset + mask * (max(offset - depth, floor) - offset)
    land = f"{M}:mars/mountain_offset"
    noises = {"huge_canyon": (-10, [1.0, 0.4]), "huge_canyon_region": (-11, [1.0]),
              "huge_canyon_warp_x": (-7, [1.0, 0.5]), "huge_canyon_warp_z": (-7, [1.0, 0.5]),
              "huge_canyon_rough": (-5, [1.0, 0.5]), "huge_canyon_width": (-8, [1.0]), "huge_canyon_floor": (-6, [1.0, 0.5])}
    for name, (octave, amplitudes) in noises.items():
        write(f"worldgen/noise/{name}.json", {"firstOctave": octave, "amplitudes": amplitudes})
    # uneven floor: the depth and the lowest height both change a little along the canyon
    floor_noise = noise("huge_canyon_floor")
    lowered = {"type": "minecraft:max",
               "argument1": add((CANYON_FLOOR_Y - 128) / 128.0, mul(CANYON_FLOOR_VARIATION / 128.0, floor_noise)),
               "argument2": add(land, -CANYON_DEPTH / 128.0, mul(-0.2 * CANYON_DEPTH / 128.0, floor_noise))}
    write("worldgen/density_function/mars/offset.json", {
        "type": "minecraft:flat_cache", "argument": {"type": "minecraft:cache_2d", "argument": {
            "type": "minecraft:add", "argument1": land,
            "argument2": {"type": "minecraft:mul", "argument1": huge_canyon_mask(),
                          "argument2": {"type": "minecraft:add", "argument1": lowered,
                                        "argument2": {"type": "minecraft:mul", "argument1": -1.0, "argument2": land}}}}}})
    write("worldgen/density_function/mars/depth.json",
          {"type": "minecraft:add", "argument1": mars_gradient(), "argument2": f"{M}:mars/offset"})
    cheese = open(os.path.join(df, "sloped_cheese.json")).read()
    assert '"minecraft:overworld/depth"' in cheese
    write("worldgen/density_function/mars/sloped_cheese.json",
          json.loads(cheese.replace('"minecraft:overworld/depth"', f'"{M}:mars/depth"')))


def main():
    vanilla, report = sys.argv[1], sys.argv[2]

    # dimension type: vanilla overworld (day cycle) with the Mars sky and the higher world
    dt = json.load(open(os.path.join(vanilla, "data/minecraft/dimension_type/overworld.json")))
    dt["min_y"], dt["height"], dt["logical_height"] = MIN_Y, HEIGHT, HEIGHT
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
    ns["noise"]["min_y"], ns["noise"]["height"] = MIN_Y, HEIGHT
    write_mountain_functions(vanilla)
    router = json.dumps(ns["noise_router"])
    for name in ("offset", "depth", "sloped_cheese"):
        router = router.replace(f'"minecraft:overworld/{name}"', f'"{M}:mars/{name}"')
    # the depth gradient written out in the router, and the top of the world
    router = router.replace(json.dumps(vanilla_gradient()), json.dumps(mars_gradient()))
    slide = TOP_Y + 1 - (320 - VANILLA_TOP_SLIDE[0]), TOP_Y + 1 - (320 - VANILLA_TOP_SLIDE[1])
    old_slide = f'"from_y": {VANILLA_TOP_SLIDE[0]}, "to_value": 0.0, "to_y": {VANILLA_TOP_SLIDE[1]}'
    assert old_slide in router, "top slide not found"
    router = router.replace(old_slide, f'"from_y": {slide[0]}, "to_value": 0.0, "to_y": {slide[1]}')
    assert '"max": 320.0, "min": -40.0' in router, "surface bound not found"
    router = router.replace('"max": 320.0, "min": -40.0', f'"max": {float(TOP_Y + 1)}, "min": -40.0')
    assert "minecraft:overworld/depth" not in router and json.dumps(vanilla_gradient()) not in router
    ns["noise_router"] = json.loads(router)

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

    # vanilla-sized canyons: the vanilla canyon carver, carving the Mars blocks, without lava at the bottom
    canyon = json.load(open(os.path.join(vanilla, "data/minecraft/worldgen/configured_carver/canyon.json")))
    canyon["config"]["replaceable"] = f"#{M}:carver_replaceables"
    canyon["config"]["lava_level"] = {"absolute": -2000}
    write("worldgen/configured_carver/canyon.json", canyon)
    write("tags/block/carver_replaceables.json",
          {"values": [f"{M}:rock", f"{M}:regolith_dry", f"{M}:regolith_loose", f"{M}:ice"]})

    # giant crater
    write("worldgen/structure/giant_crater.json", {
        "type": f"{M}:giant_crater", "biomes": f"#{M}:has_structure/giant_crater", "spawn_overrides": {},
        "step": "surface_structures", "terrain_adaptation": "none",
        "min_radius": CRATER["min_radius"], "max_radius": CRATER["max_radius"]})
    write("worldgen/structure_set/giant_crater.json", {
        "placement": {"type": "minecraft:random_spread", "salt": 1823467611,
                      "spacing": CRATER["spacing"], "separation": CRATER["separation"]},
        "structures": [{"structure": f"{M}:giant_crater", "weight": 1}]})
    write("tags/worldgen/biome/has_structure/giant_crater.json",
          {"values": [f"{M}:{b}" for b in ("plains", "cracked_plains", "ice_plains")]})

    # biomes
    for b in BIOME_MAP:
        write(f"worldgen/biome/{b}.json", {
            "attributes": {"minecraft:visual/sky_color": SKY},
            "carvers": [f"{M}:canyon"], "downfall": 0.0, "effects": {"water_color": "#3f76e4"}, "features": [],
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
        biome = lookup[name]
        if name.removeprefix("minecraft:") in HOT_ZONE:
            humidity = e["parameters"]["humidity"]
            top = humidity[1] if isinstance(humidity, list) else humidity
            biome = f"{M}:eroded_badlands" if top <= HOT_ZONE_DRY else f"{M}:cracked_plains"
        entries.append({"biome": biome, "parameters": e["parameters"]})
    write("dimension/mars.json", {
        "type": f"{M}:mars",
        "generator": {"type": "minecraft:noise", "settings": f"{M}:mars",
                      "biome_source": {"type": "minecraft:multi_noise", "biomes": entries}},
    }, indent=None)
    print(f"{len(entries)} biome entries, {len(BIOME_MAP)} biomes")


if __name__ == "__main__":
    main()
