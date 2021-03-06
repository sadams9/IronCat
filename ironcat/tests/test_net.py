from ironcat.models import Wire, Node, Function
from django.test import TestCase
from ironcat.function_engine import evaluate_function
from ironcat.photon import Photon
from ironcat.photon_types import PhotonTypes
import math
import json


def get_fn(name):
    try:
        return Function.objects.get(name=name)
    except Function.DoesNotExist:
        fn = Function(name=name, description='', input_types_json='', output_types_json='', primitive=True)
        fn.save()
        return fn


class TestNet(TestCase):

    def test_net(self):

        rect_to_polar = Function(name='rect to polar', description='', input_types_json='', output_types_json='',
                                 primitive=False)
        rect_to_polar.save()

        nd1a = Node(containing_function=rect_to_polar, inner_function=get_fn('*'))
        nd1b = Node(containing_function=rect_to_polar, inner_function=get_fn('*'))
        nd2a = Node(containing_function=rect_to_polar, inner_function=get_fn('+'))
        nd3a = Node(containing_function=rect_to_polar,
                    inner_function=get_fn('^'),
                    input_values_json=json.dumps([
                        {'value': '0', 'type': PhotonTypes.number},
                        {'value': '0.5', 'type': PhotonTypes.number}
                    ]))
        nd4a = Node(containing_function=rect_to_polar, inner_function=get_fn('atan2'))

        nodes = (
            nd1a,
            nd1b,
            nd2a,
            nd3a,
            nd4a
        )

        [node.save() for node in nodes]

        wire_in0_1a0 = Wire(source_node=None, source_pin=0, target_node=nd1a, target_pin=0)
        wire_in0_1a1 = Wire(source_node=None, source_pin=0, target_node=nd1a, target_pin=1)
        wire_in1_1b0 = Wire(source_node=None, source_pin=1, target_node=nd1b, target_pin=0)
        wire_in1_1b1 = Wire(source_node=None, source_pin=1, target_node=nd1b, target_pin=1)
        wire_1a0_2a0 = Wire(source_node=nd1a, source_pin=0, target_node=nd2a, target_pin=0)
        wire_1b0_2a1 = Wire(source_node=nd1b, source_pin=0, target_node=nd2a, target_pin=1)
        wire_2a0_3a0 = Wire(source_node=nd2a, source_pin=0, target_node=nd3a, target_pin=0)
        wire_in0_4a1 = Wire(source_node=None, source_pin=0, target_node=nd4a, target_pin=1)
        wire_in1_4a0 = Wire(source_node=None, source_pin=1, target_node=nd4a, target_pin=0)
        wire_3a0_ou0 = Wire(source_node=nd3a, source_pin=0, target_node=None, target_pin=0)
        wire_4a0_ou1 = Wire(source_node=nd4a, source_pin=0, target_node=None, target_pin=1)

        wires = (
            wire_in0_1a0,
            wire_in0_1a1,
            wire_in1_1b0,
            wire_in1_1b1,
            wire_1a0_2a0,
            wire_1b0_2a1,
            wire_2a0_3a0,
            wire_in0_4a1,
            wire_in1_4a0,
            wire_3a0_ou0,
            wire_4a0_ou1,
        )

        [wire.save() for wire in wires]

        # rect_to_polar = Function(net=rect_to_polar_net)

        rect = [1, 1]

        ph_rect = [Photon(x) for x in rect]

        ph_polar = evaluate_function(rect_to_polar, ph_rect)

        polar = [x.raw for x in ph_polar]

        self.assertAlmostEqual(polar[0], math.sqrt(2))
        self.assertAlmostEqual(polar[1], math.pi / 4)
