package de.unibremen.marsmod.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;

import de.unibremen.marsmod.world.ModBiomes;
import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.levelgen.SurfaceSystem;

/**
 * Vanilla builds the pillars of the eroded badlands only for the vanilla biome
 * ({@code surfaceBiome.is(Biomes.ERODED_BADLANDS)} in {@link SurfaceSystem#buildSurface}).
 * This makes the Mars eroded badlands get the same pillars.
 */
@Mixin(SurfaceSystem.class)
abstract class SurfaceSystemMixin {
    @WrapOperation(method = "buildSurface",
            at = @At(value = "INVOKE", target = "Lnet/minecraft/core/Holder;is(Lnet/minecraft/resources/ResourceKey;)Z"))
    private boolean marsmod$erodedBadlandsPillars(Holder<Biome> biome, ResourceKey<Biome> key, Operation<Boolean> original) {
        return original.call(biome, key) || key == Biomes.ERODED_BADLANDS && biome.is(ModBiomes.ERODED_BADLANDS);
    }
}
