package de.unibremen.marsmod.registry;

import de.unibremen.marsmod.MarsMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** The creative tab with every item of the mod. */
public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MarsMod.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MARS = TABS.register("mars", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.marsmod"))
            .icon(() -> ModItems.REGOLITH_DRY.get().getDefaultInstance())
            .displayItems((parameters, output) -> ModItems.ITEMS.getEntries().forEach(item -> output.accept(item.get())))
            .build());

    private ModCreativeTabs() {
    }
}
