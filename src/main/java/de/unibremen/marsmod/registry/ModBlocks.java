package de.unibremen.marsmod.registry;

import de.unibremen.marsmod.MarsMod;
import net.minecraft.util.ColorRGBA;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.ColoredFallingBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.properties.NoteBlockInstrument;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

/** All blocks of the mod. */
public final class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(MarsMod.MODID);

    /** Regolith colour from the item list (c87235), also used for the falling dust. */
    private static final int REGOLITH_COLOR = 0xC87235;

    /** Stays in place like dirt; the top is cracked. Drops loose regolith. */
    public static final DeferredBlock<Block> REGOLITH_DRY = BLOCKS.registerSimpleBlock("regolith_dry",
            p -> p.mapColor(MapColor.COLOR_ORANGE).strength(0.5F).sound(SoundType.SAND));

    /** Falls like sand. */
    public static final DeferredBlock<ColoredFallingBlock> REGOLITH_LOOSE = BLOCKS.registerBlock("regolith_loose",
            p -> new ColoredFallingBlock(new ColorRGBA(REGOLITH_COLOR), p),
            p -> p.mapColor(MapColor.COLOR_ORANGE).instrument(NoteBlockInstrument.SNARE).strength(0.5F).sound(SoundType.SAND));

    /** Like vanilla stone, but drops itself. */
    public static final DeferredBlock<Block> ROCK = BLOCKS.registerSimpleBlock("rock",
            p -> p.mapColor(MapColor.TERRACOTTA_LIGHT_GRAY).instrument(NoteBlockInstrument.BASEDRUM)
                    .requiresCorrectToolForDrops().strength(1.5F, 6.0F).sound(SoundType.STONE));

    /** Slippery like vanilla ice, but a plain block: no random ticks, so it never melts, and it drops itself. */
    public static final DeferredBlock<Block> ICE = BLOCKS.registerSimpleBlock("ice",
            p -> p.mapColor(MapColor.ICE).friction(0.98F).strength(0.5F).sound(SoundType.GLASS));

    private ModBlocks() {
    }
}
