from abstract_net_model import Device
from wires import Wire, PortIn, PortOut, VectorWire
from instance import Instance
from alias import Alias
from typing import Dict


class Module(Device):
    def __init__(self, name: str):
        super().__init__(name)
        self._interface = list()
        self._netlist = dict()
        self._inputs = list()
        self._outputs = list()
        self._inputs_vectors = list()
        self._output_vectors = list()
        self._wires = set()
        self._instances = dict()
        self._delay_table = dict()
        self._tracker = 0

    def net_renaming(self, start: int = 0, pre_fix: str = 'nn'):
        tracker = start
        for wire in self._wires:
            old_key = str(wire.name)
            wire.name = pre_fix + "_{}_".format(str(tracker))
            tracker = tracker + 1
            self._netlist[wire.name] = self._netlist.pop(old_key)

    def instance_renaming(self, start: int = 0, pre_fix: str = 'gg'):
        tracker = start
        instances = set(self._instances.values())
        for ins in instances:
            old_key = ins.name
            ins.name = pre_fix + "_{}_".format(str(tracker))
            tracker = tracker + 1
            self._instances[ins.name] = self._instances.pop(old_key)

    def add_wire(self, name: str, width: int = None):
        if width is None:
            new_wire = Wire(name, self)
            self._netlist[name] = new_wire
            self._wires.add(new_wire)
        else:
            for num in range(width + 1):
                name_v = name + ("[{}]".format(str(num)))
                new_wire_v = Wire(name_v, self)
                self._netlist[name_v] = new_wire_v
                self._wires.add(new_wire_v)

    def create_wire(self):
        new_name = "new_net_{}".format(self._tracker)
        self.add_wire(new_name)
        self._tracker = self._tracker + 1
        return self.get_net(new_name)

    def add_input(self, name: str, width: int = None):
        if width is None:
            new_input = PortIn(name, self)
            self._netlist[name] = new_input
            self._inputs.append(new_input)
            self._inputs_vectors.append(new_input)
        else:
            for num in range(width + 1):
                name_v = name + ("[{}]".format(str(num)))
                new_input_v = PortIn(name_v, self)
                self._netlist[name_v] = new_input_v
                self._inputs.append(new_input_v)
            self._inputs_vectors.append(VectorWire("input", name, width))

    def add_output(self, name: str, width: int = None):
        if width is None:
            new_output = PortOut(name, self)
            self._netlist[name] = new_output
            self._outputs.append(new_output)
            self._output_vectors.append(new_output)
        else:
            for num in range(width + 1):
                name_v = name + ("[{}]".format(str(num)))
                new_output_v = PortOut(name_v, self)
                self._netlist[name_v] = new_output_v
                self._outputs.append(new_output_v)
            self._output_vectors.append(VectorWire("output", name, width))

    def add_instance(self, name: str, cell: Device, mapping: dict):
        mapping_wires = dict()
        for key in mapping.keys():
            mapping_wires[key] = self.get_net(mapping[key])
        inst = cell.instantiate(name, self, mapping_wires)
        self._instances[name] = inst

    def remove_instance(self, instance_name: str):
        instance = self._instances.get(instance_name)
        if instance is not None:
            del self._instances[instance_name]

    def register_instance(self, instance):
        self._instances[instance.name] = instance

    def add_alias(self, left: str, right: str):
        inst = Alias("{}_{}".format(left, right), self, self.get_net(right), self.get_net(left))
        self._instances["{}_{}".format(left, right)] = inst
        return inst

    def get_net(self, name: str):
        return self._netlist.get(name)

    def remove_net(self, name: str):
        net = self.get_net(name)
        if net is not None:
            self._wires.remove(net)
            del self._netlist[name]

    def reset_delay(self):
        self._delay_table = dict()

    def get_delay(self, other: str):
        if self._delay_table.get(other) is not None:
            return self._delay_table.get(other)
        target_net = self.get_net(other)
        if target_net is None:
            print(other)
        parents = target_net.get_parents()
        if isinstance(target_net, PortIn):
            self._delay_table[other] = 0
            return 0
        self._delay_table[other] = max([self.get_delay(p.name) for p in parents]) + target_net.source.delay
        return self._delay_table[other]

    @property
    def gate_count(self):
        return sum(x.gate_count for x in self._instances.values())

    @property
    def interface(self):
        return self._interface

    @property
    def instances(self):
        return self._instances.values()

    def set_interface(self, interfaces: list):
        self._interface = interfaces

    def outputs_assign(self):
        for out in self._outputs:
            alias = out.alias
            assignment = out.pre_assignment
            if alias is not None:
                self._netlist[alias.name] = alias
                self._instances[assignment.name] = assignment
        self._tracker = len(self._netlist)

    @property
    def delay(self):
        self.reset_delay()
        return max([self.get_delay(x) for x in self.output_labels])

    @property
    def delays(self):
        self.reset_delay()
        return {x: self.get_delay(x) for x in self.output_labels}

    @property
    def input_labels(self):
        return [x.name for x in self._inputs]

    @property
    def output_labels(self):
        return {x.name for x in self._outputs}

    @property
    def outputs(self):
        return self._outputs

    @property
    def inputs(self):
        return self._inputs

    @property
    def nets(self):
        return {net.name for net in self._netlist.values()}

    @property
    def instance_names(self):
        return {instance.name for instance in self._instances.values()}

    def instantiate(self, name: str, parent: Device, mapping: Dict[str, Wire]):
        return Instance(name, parent, self, mapping)

    def to_verilog(self):
        verilog = "module {}({});\n".format(self.name, ','.join(self.interface))
        verilog = verilog + '\n'.join([x.to_verilog() for x in self._wires]) + '\n'
        verilog = verilog + '\n'.join([x.to_verilog() for x in self._inputs_vectors]) + '\n'
        verilog = verilog + '\n'.join([x.to_verilog() for x in self._output_vectors]) + '\n\n'
        verilog = verilog + '\n\n'.join([x.to_verilog() for x in self._instances.values()]) + "\n\nendmodule"
        return verilog


