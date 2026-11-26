package de.unibremen.marsmod.world.crater;

import de.unibremen.marsmod.registry.ModBlocks;
import de.unibremen.marsmod.registry.ModStructures;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.synth.SimplexNoise;

/**
 * Shapes the terrain of a giant crater, one chunk at a time.
 * <p>
 * Profile, with r = distance from the centre / local radius:
 * <ul>
 * <li>r &lt; 0.8: a bowl below the original centre height, deepest in the middle, with a central peak in large craters;</li>
 * <li>0.8 to 1: the inner wall rises to the rim;</li>
 * <li>1 to 1.5: the rim, raised above the surrounding terrain and fading out.</li>
 * </ul>
 * So that no two craters look alike and none is a perfect circle, the radius and the rim height change
 * with the direction (a few random waves around the crater), and a small noise roughens the surface.
 * All of it is derived from the centre position, so every chunk of the crater computes the same shape.
 */
public class GiantCraterPiece extends StructurePiece {
    /** Depth of the bowl, as a fraction of the radius. */
    private static final double DEPTH_RATIO = 0.3;
    /** Height of the rim above the terrain, as a fraction of the radius. */
    private static final double RIM_RATIO = 0.08;
    /** Craters with at least this radius get a central peak. */
    private static final int CENTRAL_PEAK_RADIUS = 95;
    /** How far the outline can bulge in or out, as a fraction of the radius. */
    private static final double OUTLINE_VARIATION = 0.18;
    /** Blocks of roughness on the surface of the crater. */
    private static final double ROUGHNESS = 2.5;
    private static final double OUTER_EDGE = 1.5;
    private static final double MAX_OUTLINE = 1.0 + OUTLINE_VARIATION;

    private final int centerX;
    private final int centerY;
    private final int centerZ;
    private final int radius;

    public GiantCraterPiece(int centerX, int centerY, int centerZ, int radius, LevelHeightAccessor height) {
        super(ModStructures.GIANT_CRATER_PIECE.get(), 0, box(centerX, centerZ, radius, height.getMinY(), height.getMaxY()));
        this.centerX = centerX;
        this.centerY = centerY;
        this.centerZ = centerZ;
        this.radius = radius;
    }

    public GiantCraterPiece(CompoundTag tag) {
        super(ModStructures.GIANT_CRATER_PIECE.get(), tag);
        this.centerX = tag.getIntOr("CX", 0);
        this.centerY = tag.getIntOr("CY", 64);
        this.centerZ = tag.getIntOr("CZ", 0);
        this.radius = tag.getIntOr("R", 64);
    }

    private static BoundingBox box(int x, int z, int radius, int minY, int maxY) {
        int reach = (int) Math.ceil(radius * OUTER_EDGE * MAX_OUTLINE);
        return new BoundingBox(x - reach, minY, z - reach, x + reach, maxY, z + reach);
    }

    @Override
    protected void addAdditionalSaveData(StructurePieceSerializationContext context, CompoundTag tag) {
        tag.putInt("CX", centerX);
        tag.putInt("CY", centerY);
        tag.putInt("CZ", centerZ);
        tag.putInt("R", radius);
    }

    /** Waves around the crater: sum of a few sines of the angle, with random amplitudes and phases. */
    private static final class Waves {
        private final double[] amplitude = new double[4];
        private final double[] phase = new double[4];

        /** 1 + 1/2 + 1/3 + 1/4: keeps the sum of all waves within +-strength. */
        private static final double HARMONIC_SUM = 25.0 / 12.0;

        Waves(RandomSource random, double strength) {
            for (int k = 0; k < amplitude.length; k++) {
                amplitude[k] = strength * random.nextDouble() / (k + 1) / HARMONIC_SUM;
                phase[k] = random.nextDouble() * Math.PI * 2.0;
            }
        }

        /** Roughly between -strength and +strength. */
        double at(double angle) {
            double sum = 0.0;
            for (int k = 0; k < amplitude.length; k++) {
                sum += amplitude[k] * Math.sin((k + 2) * angle + phase[k]);
            }
            return sum;
        }
    }

    @Override
    public void postProcess(WorldGenLevel level, StructureManager structureManager, ChunkGenerator generator, RandomSource random,
            BoundingBox chunkBB, ChunkPos chunkPos, BlockPos referencePos) {
        RandomSource shape = RandomSource.create(centerX * 341873128712L + centerZ * 132897987541L);
        Waves outline = new Waves(shape, OUTLINE_VARIATION);
        Waves rimWaves = new Waves(shape, 0.6);
        SimplexNoise rough = new SimplexNoise(shape);

        double depth = radius * DEPTH_RATIO;
        double rimBase = radius * RIM_RATIO;
        boolean centralPeak = radius >= CENTRAL_PEAK_RADIUS;
        BlockState air = Blocks.AIR.defaultBlockState();
        BlockState floor = ModBlocks.REGOLITH_LOOSE.get().defaultBlockState();
        BlockState rimTop = ModBlocks.REGOLITH_DRY.get().defaultBlockState();
        BlockState wall = ModBlocks.ROCK.get().defaultBlockState();
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        int minY = level.getMinY() + 1;
        int maxY = level.getMaxY();

        for (int x = Math.max(chunkBB.minX(), boundingBox.minX()); x <= Math.min(chunkBB.maxX(), boundingBox.maxX()); x++) {
            for (int z = Math.max(chunkBB.minZ(), boundingBox.minZ()); z <= Math.min(chunkBB.maxZ(), boundingBox.maxZ()); z++) {
                double dx = x - centerX;
                double dz = z - centerZ;
                double angle = Math.atan2(dz, dx);
                double localRadius = radius * (1.0 + outline.at(angle));
                double r = Math.sqrt(dx * dx + dz * dz) / localRadius;
                if (r >= OUTER_EDGE) {
                    continue;
                }
                double rim = rimBase * (1.0 + rimWaves.at(angle));
                double bumps = ROUGHNESS * rough.getValue(x * 0.06, z * 0.06);
                int surface = level.getHeight(Heightmap.Types.WORLD_SURFACE_WG, x, z) - 1;
                double target;
                if (r < 1.0) {
                    double bowl = centerY - depth * (1.0 - r * r);
                    if (centralPeak && r < 0.2) {
                        double s = 1.0 - r / 0.2;
                        bowl += depth * 0.45 * s * s;
                    }
                    if (r < 0.8) {
                        target = bowl;
                    } else {
                        double s = (r - 0.8) / 0.2;
                        target = bowl + (surface + rim - bowl) * s * s;
                    }
                    target += bumps;
                } else {
                    double s = 1.0 - (r - 1.0) / (OUTER_EDGE - 1.0);
                    target = surface + (rim + bumps) * s * s;
                }
                int top = Math.clamp(Math.round((float) target), minY, maxY - 1);
                boolean steep = r > 0.82 && r < 1.0;
                if (top < surface) {
                    for (int y = surface; y > top; y--) {
                        level.setBlock(pos.set(x, y, z), air, 2);
                    }
                    level.setBlock(pos.set(x, top, z), steep ? wall : floor, 2);
                } else if (top > surface) {
                    for (int y = surface + 1; y < top; y++) {
                        level.setBlock(pos.set(x, y, z), wall, 2);
                    }
                    level.setBlock(pos.set(x, top, z), steep ? wall : rimTop, 2);
                }
            }
        }
    }
}
