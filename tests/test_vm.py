from avm2.runtime import undefined
from avm2.swf.types import DoABCTag, Tag
from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag


def test_execute_tag(raw_do_abc_tag: Tag):
    execute_tag(raw_do_abc_tag)


def test_execute_do_abc_tag(do_abc_tag: DoABCTag):
    execute_do_abc_tag(do_abc_tag)


def test_lookup_class(machine: VirtualMachine):
    assert machine.lookup_class('battle.BattleCore') == 2241
    assert machine.lookup_class('game.battle.controller.BattleController') == 989
    assert machine.lookup_class('game.battle.controller.BattleEnemyReward') == 2308


def test_lookup_method(machine: VirtualMachine):
    assert machine.lookup_method('battle.BattleCore.getElementalPenetration') == 24363
    assert machine.lookup_method('battle.BattleCore.hitrateIntensity') == 24360


def test_call_get_elemental_penetration(machine: VirtualMachine):
    assert machine.call_method('battle.BattleCore.getElementalPenetration', undefined, 2, 300000) == 1
    assert machine.call_method('battle.BattleCore.getElementalPenetration', undefined, 42, -100500) == 42


def test_call_hitrate_intensity(machine: VirtualMachine):
    assert machine.call_method('battle.BattleCore.hitrateIntensity', undefined, -100, 0) == 1
    assert machine.call_method('battle.BattleCore.hitrateIntensity', undefined, 100, 0) == 1
    assert machine.call_method('battle.BattleCore.hitrateIntensity', undefined, 0, 100) == 0
    assert machine.call_method('battle.BattleCore.hitrateIntensity', undefined, 4, 8) == 0.5


def test_create_battle_enemy_reward(machine: VirtualMachine):
    machine.create_instance('game.battle.controller.BattleEnemyReward')
