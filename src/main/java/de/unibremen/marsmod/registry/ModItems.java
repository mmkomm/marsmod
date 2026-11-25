package de.unibremen.marsmod.registry;

import de.unibremen.marsmod.MarsMod;
import net.minecraft.world.item.BlockItem;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/** All items of the mod, including the block items. */
public final class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(MarsMod.MODID);

    public static final DeferredItem<BlockItem> REGOLITH_DRY = ITEMS.registerSimpleBlockItem("regolith_dry", ModBlocks.REGOLITH_DRY);
    public static final DeferredItem<BlockItem> REGOLITH_LOOSE = ITEMS.registerSimpleBlockItem("regolith_loose", ModBlocks.REGOLITH_LOOSE);
    public static final DeferredItem<BlockItem> ROCK = ITEMS.registerSimpleBlockItem("rock", ModBlocks.ROCK);
    public static final DeferredItem<BlockItem> ICE = ITEMS.registerSimpleBlockItem("ice", ModBlocks.ICE);

    private ModItems() {
    }
}
