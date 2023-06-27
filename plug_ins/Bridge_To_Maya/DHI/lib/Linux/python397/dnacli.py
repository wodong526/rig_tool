import argparse
import inspect

import dna


def index_of_next_word(char2):
    if char2[0].islower() and char2[1].isupper():
        return int(char2[1].isupper())
    return -1


def get_cli_name(field_name):
    rets = field_name[0]
    i = 1
    while i < len(field_name)-1:
        char2 = field_name[i:i+2]
        split_index = index_of_next_word(char2)
        if split_index == -1:
            rets += char2[0]
            i += 1
        else:
            rets += char2[0:split_index] + "-" + char2[split_index:]
            i += 2
    # add reminder of word
    while i < len(field_name):
        rets += field_name[i]
        i += 1
    return rets.lower()


def add_method(parser, subparsers, argument_name, method):
    method_args = map(lambda arg: get_cli_name(arg),
                      inspect.getargspec(method).args[1:])
    usage = "dna_path {} {}".format(argument_name, " ".join(method_args))
    method_parser = subparsers.add_parser(argument_name, usage=usage)
    method_parser.set_defaults(method=method)
    method_parser.set_defaults(var_arg_names=method_args)
    for var in method_args:
        method_parser.add_argument(
            dest="var_args", metavar=var, action='append')


def collect_methods():
    def isproperty(object):
        if not inspect.ismethod(object):
            return False
        is_getter = object.__name__.startswith("get")
        is_setter = object.__name__.startswith("set")
        return is_getter or is_setter

    def map_method(method, result):
        cli_name = get_cli_name(method.__name__)
        result[cli_name] = method

    methods = {}
    properties = inspect.getmembers(dna.StreamReader, isproperty)
    properties.extend(inspect.getmembers(dna.StreamWriter, isproperty))
    for _, method in properties:
        map_method(method, methods)
    return methods


def get_arg_parse():
    parser = argparse.ArgumentParser(description='DNA CLI',
                                     add_help=False,
                                     usage="")
    parser.add_argument(dest="dna_path")
    parser.set_defaults(var_args=[])
    subparsers = parser.add_subparsers()  # izbrisao dest="command"
    named_methods = collect_methods()
    for argument_name, methods in named_methods.iteritems():
        add_method(parser, subparsers, argument_name, methods)
    return parser


def excute_api_calls(dna_reader, method, var_arg_names, var_args):
    dna_rw = dna_reader
    is_write = args.method.im_class == dna.StreamWriter
    if is_write:
        stream = dna.FileStream(args.dna_path,
                                dna.FileStream.AccessMode_Write,
                                dna.FileStream.OpenMode_Binary)
        dna_writer = dna.StreamWriter(stream)
        dna_writer.setFrom(dna_reader)
        dna_rw = dna_writer

    arg_generators = get_arg_generators(var_args, var_arg_names)
    for method_params in get_method_calls(arg_generators):
        call_method_and_print_result(dna_rw, method, method_params)

    if is_write:
        dna_rw.write()


def get_arg_generators(var_args, var_arg_names):
    arg_generators = []
    for i in range(len(var_args)):
        arg_generators.append(
            make_arg_generator(var_args[i], var_arg_names[i]))
    return arg_generators


def make_arg_generator(arg, name):
    if "index" in name.lower() and type(arg) is list:
        for el in arg:
            yield el
    else:
        yield arg


def get_method_calls(generators):
    argument_count = len(generators)
    params = [0] * argument_count
    while True:
        end_count = 0
        i = None
        for i in range(argument_count):
            try:
                params[i] = next(generators[i])
            except StopIteration:
                end_count += 1
        if i is None:
            yield []
        if end_count is argument_count:
            break
        yield params


def call_method_and_print_result(dna, method, params=None):
    if params is not None:
        return_val = method(dna, *params)
    else:
        return_val = method(dna)

    if return_val:
        if params is not None:
            print " ,".join([str(param) for param in params])
        print "    " + str(return_val)


if __name__ == '__main__':
    parser = get_arg_parse()
    args = parser.parse_args()
    stream = dna.FileStream(args.dna_path,
                            dna.FileStream.AccessMode_Read,
                            dna.FileStream.OpenMode_Binary)
    dna_reader = dna.StreamReader(stream, dna.DataLayer_All)
    dna_reader.read()
    stream.close()

    args.var_args = [eval(arg) for arg in args.var_args]
    if not dna.Status_isOk:
        print dna.Status_get().message
    else:
        excute_api_calls(dna_reader, args.method,
                         args.var_arg_names, args.var_args)
