package de.unibremen.marsmod.world;

import de.unibremen.marsmod.MarsMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;

/** Keys of the dimensions defined in data/marsmod/dimension/. */
public final class ModDimensions {
    public static final ResourceKey<Level> MARS = ResourceKey.create(Registries.DIMENSION, Identifier.fromNamespaceAndPath(MarsMod.MODID, "mars"));

    private ModDimensions() {
    }
}
