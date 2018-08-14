from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
from avm2.swf.types import DoABCTag, Tag
from avm2.abc.types import ABCMethodIndex, ABCClassIndex
from avm2.runtime import undefined


def test_execute_tag(raw_do_abc_tag: Tag):
    execute_tag(raw_do_abc_tag)


def test_execute_do_abc_tag(do_abc_tag: DoABCTag):
    execute_do_abc_tag(do_abc_tag)


def test_lookup_class(machine: VirtualMachine, battle_enemy_reward_class_index: ABCClassIndex):
    assert machine.lookup_class('battle.BattleCore') == 2241
    assert machine.lookup_class('game.battle.controller.BattleController') == 989
    assert battle_enemy_reward_class_index == 2308


def test_lookup_method(
    get_elemental_penetration_method_index: ABCMethodIndex,
    hitrate_intensity_method_index: ABCMethodIndex,
):
    assert get_elemental_penetration_method_index == 24363
    assert hitrate_intensity_method_index == 24360


def test_call_get_elemental_penetration(machine: VirtualMachine, get_elemental_penetration_method_index: ABCMethodIndex):
    assert machine.call_method(get_elemental_penetration_method_index, undefined, 2, 300000) == 1
    assert machine.call_method(get_elemental_penetration_method_index, undefined, 42, -100500) == 42


def test_call_hitrate_intensity(machine: VirtualMachine, hitrate_intensity_method_index: ABCMethodIndex):
    assert machine.call_method(hitrate_intensity_method_index, undefined, -100, 0) == 1
    assert machine.call_method(hitrate_intensity_method_index, undefined, 100, 0) == 1
    assert machine.call_method(hitrate_intensity_method_index, undefined, 0, 100) == 0
    assert machine.call_method(hitrate_intensity_method_index, undefined, 4, 8) == 0.5


def test_create_battle_enemy_reward(machine: VirtualMachine, battle_enemy_reward_class_index: ABCClassIndex):
    machine.create_instance(battle_enemy_reward_class_index)
