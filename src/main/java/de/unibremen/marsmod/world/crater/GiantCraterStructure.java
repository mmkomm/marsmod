package de.unibremen.marsmod.world.crater;

import java.util.Optional;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import de.unibremen.marsmod.registry.ModStructures;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;

/**
 * A giant impact crater: a round bowl with a raised rim, carved into the terrain.
 * Placed by data/marsmod/worldgen/structure_set/giant_crater.json and found with
 * {@code /locate structure marsmod:giant_crater}.
 */
public class GiantCraterStructure extends Structure {
    public static final MapCodec<GiantCraterStructure> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            settingsCodec(i),
            Codec.intRange(16, 256).fieldOf("min_radius").forGetter(s -> s.minRadius),
            Codec.intRange(16, 256).fieldOf("max_radius").forGetter(s -> s.maxRadius))
            .apply(i, GiantCraterStructure::new));

    private final int minRadius;
    private final int maxRadius;

    public GiantCraterStructure(StructureSettings settings, int minRadius, int maxRadius) {
        super(settings);
        this.minRadius = minRadius;
        this.maxRadius = Math.max(minRadius, maxRadius);
    }

    @Override
    public Optional<GenerationStub> findGenerationPoint(GenerationContext context) {
        ChunkPos chunk = context.chunkPos();
        int x = chunk.getMiddleBlockX();
        int z = chunk.getMiddleBlockZ();
        int y = context.chunkGenerator().getBaseHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, context.heightAccessor(), context.randomState());
        int radius = minRadius + context.random().nextInt(maxRadius - minRadius + 1);
        return Optional.of(new GenerationStub(new BlockPos(x, y, z),
                builder -> builder.addPiece(new GiantCraterPiece(x, y, z, radius, context.heightAccessor()))));
    }

    @Override
    public StructureType<?> type() {
        return ModStructures.GIANT_CRATER.get();
    }
}
