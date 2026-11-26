package de.unibremen.marsmod.mixin;

import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;

import de.unibremen.marsmod.registry.ModBlocks;
import de.unibremen.marsmod.world.ModBiomes;
import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.BlockColumn;
import net.minecraft.world.level.levelgen.SurfaceSystem;

/**
 * The pillars of the Mars eroded badlands.
 * <ul>
 * <li>Vanilla builds them only for the vanilla biome ({@code surfaceBiome.is(Biomes.ERODED_BADLANDS)} in
 * {@link SurfaceSystem#buildSurface}); the Mars eroded badlands get them too.</li>
 * <li>A pillar is filled from its top (y 64 to about 163) down to the ground. In the overworld the sea stops it:
 * over ground below sea level it finds water and is not built. Mars has no water, so pillars reached down to the
 * floor of the huge canyon and stood 150 blocks tall. Here they are not built below the vanilla sea level either,
 * which keeps them at most about 100 blocks tall, as in the overworld.</li>
 * </ul>
 */
@Mixin(SurfaceSystem.class)
abstract class SurfaceSystemMixin {
    /** {@code height} is the first air block above the ground: ground at y 62 or higher, as with vanilla sea level 63. */
    private static final int MARS_PILLAR_MIN_HEIGHT = 63;

    @Shadow
    @Final
    private BlockState defaultBlock;

    @WrapOperation(method = "buildSurface",
            at = @At(value = "INVOKE", target = "Lnet/minecraft/core/Holder;is(Lnet/minecraft/resources/ResourceKey;)Z"))
    private boolean marsmod$erodedBadlandsPillars(Holder<Biome> biome, ResourceKey<Biome> key, Operation<Boolean> original) {
        return original.call(biome, key) || key == Biomes.ERODED_BADLANDS && biome.is(ModBiomes.ERODED_BADLANDS);
    }

    /** Only on Mars, whose terrain is made of Mars rock; the overworld is left as it is. */
    @Inject(method = "erodedBadlandsExtension", at = @At("HEAD"), cancellable = true)
    private void marsmod$noPillarsBelowSeaLevel(BlockColumn column, int blockX, int blockZ, int height, LevelHeightAccessor level,
            CallbackInfo ci) {
        if (height < MARS_PILLAR_MIN_HEIGHT && defaultBlock.is(ModBlocks.ROCK.get())) {
            ci.cancel();
        }
    }
}
