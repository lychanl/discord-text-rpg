import os
from typing import Any
from dtrpg.core.game import Game
from dtrpg.core.creature import Player, CreatureSkill
from dtrpg.core.item import ItemStack

from datetime import datetime
import yaml


class Persistency:
    def __init__(self, game: 'Game') -> None:
        self._game = game
        self._objects = {obj.id: obj for obj in game.global_objects}

    def _get_subobject(self, obj: Any, id: str):
        if not id:
            return obj

        if id.startswith('['):
            key = id[1:].split(']')[0]
            if key.isdigit:
                keyobj = int(key)
            else:
                keyobj = self._objects[key]
            return self._get_subobject(obj[keyobj], id[len(key) + 2:])

        assert id.startswith('.')
        top = id[1:].split('.')[0].split['['][0]
        subobj = getattr(obj, top)

        return self._get_subobject(subobj, id[len(top):])

    def _get_by_id(self, id: str) -> Any:
        top = id.split('.')[0].split('[')[0]
        obj = self._objects[top]
        return self._get_subobject(obj, id[len(top):])

    def _serialize_skill(self, skill: 'CreatureSkill') -> dict:
        return {
            'skill': skill.skill.id,
            'value': skill.value,
            'experience': skill.experience,
        }

    def _serialize_player(self, player: 'Player') -> dict:
        return {
            'factory': player.factory_id,
            'resources': {resource.id: value.state for resource, value in player.resources.items()},
            'skills': {skill.id: self._serialize_skill(value) for skill, value in player.skills.items()},
            'items': [(stack.item.id, stack.stack) for stack in player.items.items],
            'item_slots': {slot.id: item.id for slot, item in player.item_slots.items() if item},
            'timed_bonuses': {bonus.id: time.timestamp() for bonus, time in player.timed_bonuses.items()},
            'tactic': player.tactic.id,
            'location': player.location.id,
            'active_states': [(state.id, machine.id) for state, machine in player.active_states],
            'passive_states': {machine.id: state.id for machine, state in player.passive_states.items()},
        }

    def serialize(self) -> dict:
        return {
            id: self._serialize_player(player) for id, player in self._game.players.items()
        }

    def _deserialize_player(self, state: dict) -> 'Player':
        player = self._get_by_id(state['factory']).create()

        for res_id, res_state in state['resources'].items():
            player.resources[self._get_by_id(res_id)].state = res_state

        for skill_id, skill_value in state['skills'].items():
            player.skills[self._get_by_id(skill_id)].value = skill_value['value']
            player.skills[self._get_by_id(skill_id)].experience = skill_value['experience']

        for item_id, stack in state['items']:
            player.items.add(ItemStack(self._get_by_id(item_id), stack))

        for slot, item in state['item_slots'].items():
            player.item_slots[self._get_by_id(slot)] = self._get_by_id(item)

        for bonus, expiration in state['timed_bonuses'].items():
            player.timed_bonuses[self._get_by_id(bonus)] = datetime.fromtimestamp(expiration)

        player.tactic = self._get_by_id(state['tactic'])
        player.location = self._get_by_id(state['location'])

        player.active_states = [(self._get_by_id(s), self._get_by_id(m)) for s, m in state['active_states']]
        player.passive_states = {self._get_by_id(s): self._get_by_id(m) for s, m in state['passive_states'].items()}

        return player

    def deserialize(self, state: dict) -> None:
        self._game.players = {
            id: self._deserialize_player(player) for id, player in state.items()
        }

    def load(self, filename) -> None:
        with open(filename, 'r') as file:
            serialized = yaml.safe_load(file)

        self.deserialize(serialized)

    def save(self, filename) -> None:
        serialized = self.serialize()

        dirname = os.path.dirname(filename)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(filename + '.tmp', 'w') as file:
            yaml.safe_dump(serialized, file)

        os.replace(filename + '.tmp', filename)
