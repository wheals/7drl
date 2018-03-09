import libtcodpy as tcod

from map import Map, MapKnowledge, MAX_MAP_HEIGHT, MAX_MAP_WIDTH
from mapgen import generate_map, place_player
from render import render_all, init_ui, show_popup
from los import compute_los
from turnstate import TurnState, TurnProgress


def init_game():
    turn_state = TurnState()
    game_map = Map(MAX_MAP_WIDTH, MAX_MAP_HEIGHT)
    generate_map(game_map)
    map_knowledge = MapKnowledge(game_map)
    game_map.init_los()

    place_player(game_map)

    return turn_state, game_map, map_knowledge


def process_results(results, actor, game_map, message_log, current_turn):
    time_taken = 0
    end_game = False
    # would be lovely if we had rust enums
    for result in results:
        if result.get('player_only') and not actor.is_active_player:
            continue
        if result.get('time'):
            time_taken = result.get('time')
        if result.get('exit'):
            end_game = result.get('exit')
        if result.get('message'):
            message_log.add(result.get('message'), current_turn)
        dead = result.get('dead')
        if dead:
            message_log.add(dead.die(), current_turn)
            game_map.actors.remove(dead)
            if dead.kind == 'player':
                end_game = True

    actor.energy -= time_taken
    return end_game


def main():
    message_log, key, mouse = init_ui()
    show_popup(("You are a killer robot, sent from the future on a vital mission.\n"
                "Your only job -- to defeat the humans who threaten your very existence with their foolish schemes.\n"
                "They cannot be allowed to wipe out the peaceful race of killer robots before they're even created!"),
               'THE STORY SO FAR')
    turn_state, game_map, map_knowledge = init_game()

    while not tcod.console_is_window_closed():
        if game_map.los_changed:
            compute_los(game_map.los_map, game_map.get_active_player().pos)
            game_map.los_changed = False

        map_knowledge.update(game_map)

        render_all(map_knowledge, game_map.los_map, game_map.get_active_player(), message_log, turn_state)

        turn_state.progress = TurnProgress.Ongoing

        for actor in game_map.actors:
            actor.energy += 100

        active_actors = [actor for actor in game_map.actors if actor.energy > 0]
        while len(active_actors) != 0:
            # sort to always let the player go first
            active_actors.sort(key=lambda act: 0 if act.is_active_player else 1)
            for actor in active_actors:
                command = actor.ai.next_move(target=game_map.get_active_player(), game_map=game_map)
                results = actor.execute(command, game_map)
                end_game = process_results(results, actor, game_map, message_log, turn_state.current_turn)
                if end_game:
                    return True

            # if only python had do-while
            active_actors = [actor for actor in game_map.actors if actor.energy > 0]

        turn_state.next_turn()


if __name__ == '__main__':
    main()
