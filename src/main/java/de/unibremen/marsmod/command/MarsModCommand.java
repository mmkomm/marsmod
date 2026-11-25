package de.unibremen.marsmod.command;

import java.util.Set;

import com.mojang.brigadier.exceptions.CommandSyntaxException;

import de.unibremen.marsmod.MarsMod;
import de.unibremen.marsmod.world.ModDimensions;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/**
 * Provisional access to Mars until the rockets exist (Work Package 3):
 * {@code /marsmod mars} and {@code /marsmod earth}, for operators only.
 */
@EventBusSubscriber(modid = MarsMod.MODID)
public final class MarsModCommand {
    private MarsModCommand() {
    }

    @SubscribeEvent
    static void onRegisterCommands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("marsmod")
                .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                .then(Commands.literal("mars").executes(c -> travel(c.getSource(), ModDimensions.MARS, "mars")))
                .then(Commands.literal("earth").executes(c -> travel(c.getSource(), Level.OVERWORLD, "earth"))));
    }

    /** Teleports the player to the same x/z in the target dimension, on top of the highest block. */
    private static int travel(CommandSourceStack source, ResourceKey<Level> target, String name) throws CommandSyntaxException {
        ServerPlayer player = source.getPlayerOrException();
        ServerLevel level = source.getServer().getLevel(target);
        if (level == null) {
            source.sendFailure(Component.translatable("commands.marsmod.missing_dimension", target.identifier().toString()));
            return 0;
        }
        int x = player.getBlockX();
        int z = player.getBlockZ();
        level.getChunk(x >> 4, z >> 4); // generate the chunk so that the height map is filled
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        player.teleportTo(level, x + 0.5, y, z + 0.5, Set.of(), player.getYRot(), player.getXRot(), true);
        source.sendSuccess(() -> Component.translatable("commands.marsmod." + name, x, y, z), true);
        return 1;
    }
}
