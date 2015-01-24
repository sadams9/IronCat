from ironcat.photon_types import PhotonTypes
from ironcat.photon import Photon, deserialize
from ironcat.models import *
import json
import math
from functools import reduce


_primitives = {
    '+',
    '-',
    '*',
    '/',
    '^',
    'sin',
    'cos',
    'tan',
    'asin',
    'acos',
    'atan',
    'atan2',
    'get',
    'set',
    'to list',
    'concatenate',
    'map',
    'reduce',
    'evaluate'
}


def evaluate_function(function, inputs):

    error = [Photon.error]

    if isinstance(function, Function) and function.name in _primitives:
        function = function.name

    if type(function) is str:

        if function in _primitives:
            try:
                Function.objects.get(name=function)
            except Function.DoesNotExist:
                fn = Function(name=function, input_types_json='', output_types_json='', primitive=True)
                fn.save()

        if function == '+':
            if any(not ph.is_number for ph in inputs):
                return error
            input_values = [ph.raw for ph in inputs]
            result = sum(input_values)
            if all(ph.type == PhotonTypes.int for ph in inputs):
                result = int(result)
            return [Photon(result)]
        elif function == '-':
            if len(inputs) != 2:
                return error
            sx = inputs[0]
            sy = inputs[1]
            if not sx.is_number or not sy.is_number:
                return error
            x = float(sx.value)
            y = float(sy.value)
            result = x - y
            if sx.type == PhotonTypes.int and sy.type == PhotonTypes.int:
                result = int(result)
            return [Photon(result)]
        elif function == '*':
            if any(not ph.is_number for ph in inputs):
                return error
            values = [ph.raw for ph in inputs]
            result = reduce(lambda a, b: a * b, values, 1)
            if all(ph.type == PhotonTypes.int for ph in inputs):
                result = int(result)
            return [Photon(result)]
        elif function == '/':
            if len(inputs) != 2:
                return error
            sx = inputs[0]
            sy = inputs[1]
            if not sx.is_number or not sy.is_number:
                return error
            x = float(sx.value)
            y = float(sy.value)
            result = x / y
            if sx.type == PhotonTypes.int and sy.type == PhotonTypes.int:
                result = int(result)
            return [Photon(result)]
        elif function == '^':
            if len(inputs) != 2:
                return error
            sx = inputs[0]
            sy = inputs[1]
            if not sx.is_number or not sy.is_number:
                return error
            x = float(sx.value)
            y = float(sy.value)
            result = x ** y
            if sx.type == PhotonTypes.int and sy.type == PhotonTypes.int:
                result = int(result)
            return [Photon(result)]
        elif function == 'sin':
            if len(inputs) != 1:
                return error
            sx = inputs[0]
            if not sx.is_number:
                return error
            x = float(sx.value)
            result = math.sin(x)
            return [Photon(result)]
        elif function == 'cos':
            if len(inputs) != 1:
                return error
            sx = inputs[0]
            if not sx.is_number:
                return error
            x = float(sx.value)
            result = math.cos(x)
            return [Photon(result)]
        elif function == 'tan':
            if len(inputs) != 1:
                return error
            sx = inputs[0]
            if not sx.is_number:
                return error
            x = float(sx.value)
            result = math.tan(x)
            return [Photon(result)]
        elif function == 'asin':
            if len(inputs) != 1:
                return error
            sx = inputs[0]
            if not sx.is_number:
                return error
            x = float(sx.value)
            result = math.asin(x)
            return [Photon(result)]
        elif function == 'acos':
            if len(inputs) != 1:
                return error
            sx = inputs[0]
            if not sx.is_number:
                return error
            x = float(sx.value)
            result = math.acos(x)
            return [Photon(result)]
        elif function == 'atan':
            if len(inputs) != 1:
                return error
            ph_x = inputs[0]
            if not ph_x.is_number:
                return error
            x = ph_x.raw
            result = math.atan(x)
            return [Photon(result)]
        elif function == 'atan2':
            if len(inputs) != 2:
                return error
            ph_y = inputs[0]
            ph_x = inputs[1]
            if not ph_x.is_number or not ph_y.is_number:
                return error
            x = ph_x.raw
            y = ph_y.raw
            result = math.atan2(y, x)
            return [Photon(result)]
        elif function == 'get':
            if len(inputs) != 2:
                return error
            ph_col = inputs[0]
            ph_key = inputs[1]
            if ph_key.type == PhotonTypes.int:
                if not ph_col.is_indexable:
                    return error
            elif ph_key.type == PhotonTypes.string:
                if not ph_col.is_keyable:
                    return error
            else:
                return error
            result = ph_col.raw[ph_key.raw]
            return [Photon(result)]
        elif function == 'set':
            if len(inputs) != 3:
                return error
            ph_col = inputs[0]
            ph_key = inputs[1]
            ph_value = inputs[2]
            if ph_key.type == PhotonTypes.int:
                if not ph_col.is_indexable:
                    return error
            elif ph_key.type == PhotonTypes.string:
                if not ph_col.is_keyable:
                    return error
            else:
                return error
            col = ph_col.raw
            col[ph_key.raw] = ph_value
            col = Photon(col).raw
            return [Photon(col)]
        elif function == 'to list':
            if len(inputs) != 1:
                return error
            ph_col = inputs[0]
            if not ph_col.is_collection:
                return error
            if ph_col.type == PhotonTypes.set:
                result = list(ph_col.raw)
            elif ph_col.type == PhotonTypes.list:
                result = ph_col.raw
            elif ph_col.type == PhotonTypes.string:
                result = list(ph_col.raw)
            elif ph_col.type == PhotonTypes.object:
                result = list(ph_col.raw.values())
            else:
                return error
            return [Photon(result)]
        elif function == 'concatenate':
            if any(ph.type != PhotonTypes.string for ph in inputs):
                return error
            strs = [ph.raw for ph in inputs]
            result = ''.join(strs)
            return [Photon(result)]
        elif function == 'map':
            if len(inputs) != 2:
                return error
            ph_fn = inputs[0]
            ph_col = inputs[1]
            if ph_fn.type != PhotonTypes.function:
                return error
            if not ph_col.is_collection:
                return error
            fn = ph_fn.raw
            if ph_col.type == PhotonTypes.list:
                lst = ph_col.raw
                result = [evaluate_function(fn, [x])[0] for x in lst]
                return [Photon(result)]
            elif ph_col.type == PhotonTypes.set:
                st = ph_col.raw
                result = {evaluate_function(fn, [x])[0] for x in st}
                return [Photon(result)]
            elif ph_col.type == PhotonTypes.object:
                dct = ph_col.raw
                result = {key: evaluate_function(fn, [val])[0] for key, val in dct.items()}
                return [Photon(result)]
            elif ph_col.type == PhotonTypes.string:
                string = ph_col.raw
                result = [evaluate_function(fn, [c])[0] for c in string]
                return [Photon(result)]
            else:
                return error
        elif function == 'reduce':
            if len(inputs) != 3:
                return error
            ph_fn = inputs[0]
            ph_col = inputs[1]
            ph_init = inputs[2]
            if ph_fn.type != PhotonTypes.function:
                return error
            if not ph_col.is_collection:
                return error
            fn = ph_fn.raw
            col = ph_col.raw
            ph_cumulative = ph_init
            for ph in col:
                ph_cumulative = evaluate_function(fn, [ph_cumulative, ph])[0]
            return [ph_cumulative]
        elif function == 'evaluate':
            if len(inputs) < 1:
                return error
            ph_fn = inputs[0]
            ph_params = inputs[1:]
            if ph_fn.type != PhotonTypes.function:
                return error
            fn = ph_fn.raw
            result = evaluate_function(fn, ph_params)
            return result
        else:
            try:
                fn = Function.objects.get(name=function)
            except Function.DoesNotExist:
                return error

    elif type(function) is Function:
        fn = function

    else:
        return

    # evaluate net

    wire_photons = {}

    nodes = set(fn.nodes.all())

    input_connected_wires = Wire.objects.filter(source_node_id=None)
    output_connected_wires = Wire.objects.filter(target_node_id=None)

    for wire in input_connected_wires:
        wire_photons[wire.id] = inputs[wire.source_pin]

    while any(nodes):
        completed_nodes = set()
        for node in nodes:
            if any(wire.id not in wire_photons.keys() for wire in node.in_wires.all()):
                continue
            node_input_photons = []
            for wire in node.in_wires.all():
                if len(node_input_photons) <= wire.target_pin:
                    node_input_photons += [Photon()] * (wire.target_pin + 1 - len(node_input_photons))
                node_input_photons[wire.target_pin] = wire_photons[wire.id]
            node_output_photons = evaluate_node(node, node_input_photons)
            for wire in node.out_wires.all():
                wire_photons[wire.id] = node_output_photons[wire.source_pin]
            completed_nodes.add(node)
        for node in completed_nodes:
            nodes.remove(node)

    output_photons = []

    for wire in output_connected_wires:
        while len(output_photons) <= wire.target_pin:
            output_photons.append(None)
        output_photons[wire.target_pin] = wire_photons[wire.id]

    return output_photons


class IO:
    def __init__(self, input_types=None, output_types=None):
        self.input_types = input_types or []
        self.output_types = output_types or []


def get_node_io(node):
    return get_function_io(node.inner_function)


def get_function_io(fn):
    input_types = json.loads(fn.input_types_json or '[]')
    output_types = json.loads(fn.output_types_json or '[]')
    return IO(input_types, output_types)


def evaluate_node(node, inputs):
    default_inputs = deserialize(node.default_inputs_json or '[]')
    inputs = [x for x in inputs]
    for i in range(len(default_inputs)):
        if len(inputs) <= i:
            inputs.append(None)
        if not inputs[i] or (isinstance(inputs[i], Photon) and inputs[i].type == PhotonTypes.none):
            inputs[i] = Photon(default_inputs[i])
    return evaluate_function(node.inner_function, inputs)