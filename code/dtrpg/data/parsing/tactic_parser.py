from typing import Any, Iterable, TYPE_CHECKING, Tuple, Type
from dtrpg.data.parsing.parser import Parser, ParserError, ParsingErrorUnexpected, ParsingErrorEOF, WS

import re

import lark

if TYPE_CHECKING:
    from dtrpg.core.fighting import Tactic, TacticCondition


class TacticParser(Parser):
    CONDITION = 'condition'
    QUANTIFIER = 'quantifier'
    FLAG = 'flag'
    DESTINATION = 'destination'
    ACTION_ARG = 'action_arg'
    ACTION = 'action'
    ARGUMENT = 'argument'
    ACTION_PREDICATE = 'action_predicate'
    MOVE_PREDICATE = 'move_predicate'

    def __init__(self):
        # to avoid circular imports
        global ActionPredicate, MovePredicate, Tactic, MoveDestination, StatusFlag, FightActions
        global TacticQuantifier, TacticCondition
        from dtrpg.core.fighting import (
            ActionPredicate, MovePredicate, Tactic, MoveDestination, StatusFlag, FightActions,
            TacticQuantifier, TacticCondition
        )
        super().__init__()
        self._types_mapping = {}
        self._parser = None

    def __call__(self, string: str) -> 'Tactic':
        return self._parse_tactic(string)

    def _prepare_type_mapping(self, type: Type, name: str) -> None:
        self._types_mapping[name] = {name + '_' + v.name.lower(): v for v in type}

    def finalize_locale(self) -> None:
        self._prepare_parser()

    def _prepare_parser(self) -> None:
        self._prepare_type_mapping(TacticQuantifier, self.QUANTIFIER)
        self._prepare_type_mapping(StatusFlag, self.FLAG)
        self._prepare_type_mapping(FightActions, self.ACTION)
        self._prepare_type_mapping(MoveDestination, self.DESTINATION)

        grammar = f"""
start: {self._get_parser_string(self.strings, 'TacticParser')}

{self.ACTION_PREDICATE}: {self._get_class_parser_string(ActionPredicate)}
{self.MOVE_PREDICATE}: {self._get_class_parser_string(MovePredicate)}
{self.ACTION_ARG}: {self._get_class_parser_string(FightActions)}

{self._prepare_enum_rules(self.QUANTIFIER)}

{self._prepare_enum_rules(self.FLAG)}

{self._prepare_enum_rules(self.ACTION)}

{self._prepare_enum_rules(self.DESTINATION)}

%import common.WS -> {WS}
%ignore {WS}
        """

        self._parser = lark.Lark(grammar, g_regex_flags=re.IGNORECASE)

    def _prepare_enum_rules(self, enum: str) -> str:
        type_def = ' | '.join(self._types_mapping[enum])
        obj_defs = '\n'.join([
            parser_name + ": " + self._get_parser_string(value.strings, f'{enum}: {value.name.lower()}')
            for parser_name, value in self._types_mapping[enum].items()
        ])

        return f"{enum}: {type_def}\n{obj_defs}\n"

    def _get_class_parser_string(self, clss: type):
        return self._get_parser_string(clss.get_class_strings(), clss.__name__)

    def _get_parser_string(self, strings: str, what: Any):
        if 'PARSER' not in strings:
            raise ParserError('Missing PARSER string for ' + what)
        return strings['PARSER']

    def _parse_tactic(self, value: str) -> 'Tactic':
        try:
            return self._make_tactic(self._parser.parse(value.strip() + " "))
        except lark.exceptions.UnexpectedCharacters as e:
            raise ParsingErrorUnexpected(value, e)
        except lark.exceptions.UnexpectedEOF as e:
            raise ParsingErrorEOF(value, e)

    def _make_tactic(self, tree: lark.Tree) -> 'Tactic':
        move_trees, action_trees = self._get_tree_elements(tree, self.MOVE_PREDICATE, self.ACTION_PREDICATE)
        move_predicates = [self._make_move_predicate(pt) for pt in move_trees]
        action_predicates = [self._make_action_predicate(pt) for pt in action_trees]

        return Tactic(move_predicates, action_predicates)

    def _make_move_predicate(self, tree: lark.Tree) -> 'MovePredicate':
        condition_trees, destination = self._get_tree_elements(tree, self.CONDITION, self.DESTINATION)

        conditions = [self._make_condition(ct) for ct in condition_trees]
        destination = self._types_mapping[self.DESTINATION][destination[0].children[0].data]

        return MovePredicate(conditions, destination)

    def _make_action_predicate(self, tree: lark.Tree) -> 'ActionPredicate':
        condition_trees, action = self._get_tree_elements(tree, self.CONDITION, self.ACTION)

        conditions = [self._make_condition(ct) for ct in condition_trees]
        action, arguments = self._make_action(action[0])

        return ActionPredicate(conditions, action, **arguments)

    def _make_condition(self, tree: lark.Tree) -> 'TacticCondition':
        quantifier_tree, flag_tree = self._get_tree_elements(tree, self.QUANTIFIER, self.FLAG)

        quantifier = self._types_mapping[self.QUANTIFIER][quantifier_tree[0].children[0].data]
        condition = self._types_mapping[self.FLAG][flag_tree[0].children[0].data]

        return TacticCondition(quantifier, condition)

    def _make_action(self, tree: lark.Tree) -> Tuple['FightActions', Iterable[Any]]:
        action = self._types_mapping[self.ACTION][tree.children[0].data]
        arguments = {at.data: self._parse_argument(at) for at in tree.children[0].children}

        return action, arguments

    def _parse_argument(self, tree: lark.Tree):
        typename = tree.children[0].data
        if typename in self._types_mapping:
            return self._types_mapping[typename][tree.children[0].children[0].data]

        raise ParserError(f'Invalid type for argument {tree.data}: {typename}')

    def _get_tree_elements(self, tree: lark.Tree, *ids: Iterable[str]) -> Iterable[lark.Tree]:
        result = {id: [] for id in ids}

        for child in tree.children:
            if child.data in ids:
                result[child.data].append(child)
            else:
                sub = self._get_tree_elements(child, *ids)
                for i, v in zip(ids, sub):
                    result[i].extend(v)

        return [result[id] for id in ids]
