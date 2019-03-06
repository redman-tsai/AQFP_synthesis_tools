from verilog_parser import VerilogParser
from data_levelers import DataLeveler, flow_checker, float_net_checker, missing_instance_test, splitter_checker
from default_cell_library import Library
import sys


def main(argv):
    lib = Library()
    VP = VerilogParser(lib)
    if len(argv) < 2:
        print("Please enter input file")
        return
    file_name = argv[1]
    if not VP.read_file(file_name):
        print("File not found")
        return
    module = VP.parse()
    print("\nBefore inserting buffers and splitters: Gate count: {} Delay: {}".format(module.gate_count, module.delay))
    module.reset_delay()
    dataleveller = DataLeveler(module, lib)
    dataleveller.process()
    print("\nAfter inserting buffers and splitters: Gate count: {} Delay: {}".format(module.gate_count, module.delay))
    float_net_checker(module)
    flow_checker(module)
    missing_instance_test(module)
    splitter_checker(module)
    module.net_renaming()
    module.instance_renaming()
    if len(argv) == 3:
        out_file = argv[2]
    else:
        out_file = file_name[:-2] + "_balanced.v"
    with open(out_file, 'w+') as f:
        f.write(module.to_verilog())

main(sys.argv)

