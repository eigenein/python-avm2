from avm2.vm import VirtualMachine, execute_do_abc_tag, execute_tag
from avm2.swf.types import DoABCTag, Tag


def test_execute_tag(raw_do_abc_tag: Tag):
    execute_tag(raw_do_abc_tag)


def test_execute_do_abc_tag(do_abc_tag: DoABCTag):
    execute_do_abc_tag(do_abc_tag)


def test_virtual_machine(machine: VirtualMachine):
    assert 'battle.BattleCore' in machine.classes_by_name
