from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
from avm2.swf.types import DoABCTag, Tag


def test_execute_tag(raw_do_abc_tag: Tag):
    execute_tag(raw_do_abc_tag)


def test_execute_do_abc_tag(do_abc_tag: DoABCTag):
    execute_do_abc_tag(do_abc_tag)


def test_lookup_class(machine: VirtualMachine):
    assert machine.lookup_class('battle.BattleCore') == 2241
    assert machine.lookup_class('game.battle.controller.BattleController') == 989


def test_lookup_method(machine: VirtualMachine):
    assert machine.lookup_method('battle.BattleCore.getElementalPenetration') == 24363
