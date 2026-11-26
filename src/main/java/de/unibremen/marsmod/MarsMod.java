package de.unibremen.marsmod;

import org.slf4j.Logger;

import com.mojang.logging.LogUtils;

import de.unibremen.marsmod.registry.ModBlocks;
import de.unibremen.marsmod.registry.ModCreativeTabs;
import de.unibremen.marsmod.registry.ModItems;
import de.unibremen.marsmod.registry.ModStructures;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;

@Mod(MarsMod.MODID)
public class MarsMod {
    public static final String MODID = "marsmod";
    public static final Logger LOGGER = LogUtils.getLogger();

    public MarsMod(IEventBus modEventBus, ModContainer modContainer) {
        ModBlocks.BLOCKS.register(modEventBus);
        ModItems.ITEMS.register(modEventBus);
        ModCreativeTabs.TABS.register(modEventBus);
        ModStructures.TYPES.register(modEventBus);
        ModStructures.PIECES.register(modEventBus);
    }
}
