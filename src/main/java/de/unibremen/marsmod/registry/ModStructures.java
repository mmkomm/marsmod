package de.unibremen.marsmod.registry;

import de.unibremen.marsmod.MarsMod;
import de.unibremen.marsmod.world.crater.GiantCraterPiece;
import de.unibremen.marsmod.world.crater.GiantCraterStructure;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Structure types and structure pieces of the mod. */
public final class ModStructures {
    public static final DeferredRegister<StructureType<?>> TYPES = DeferredRegister.create(Registries.STRUCTURE_TYPE, MarsMod.MODID);
    public static final DeferredRegister<StructurePieceType> PIECES = DeferredRegister.create(Registries.STRUCTURE_PIECE, MarsMod.MODID);

    public static final DeferredHolder<StructureType<?>, StructureType<GiantCraterStructure>> GIANT_CRATER =
            TYPES.register("giant_crater", () -> () -> GiantCraterStructure.CODEC);
    public static final DeferredHolder<StructurePieceType, StructurePieceType> GIANT_CRATER_PIECE =
            PIECES.register("giant_crater", () -> (StructurePieceType.ContextlessType) GiantCraterPiece::new);

    private ModStructures() {
    }
}
