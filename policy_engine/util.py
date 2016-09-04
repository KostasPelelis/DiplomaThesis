def format_args(args):
    ret = []
    for arg in args:
        if isinstance(arg, str) and arg[0] == '$':
            ret.append({'type': 'ref', 'value': arg[2:-1] if arg[1] == '(' else arg[1:]})
        else:
            ret.append({'type': 'val', 'value': arg})
    return ret


def format_kwargs(kwargs):
    ret = {}
    for arg_key, arg_value in kwargs.items():
        if isinstance(arg_value, str) and arg_value[0] == '$':
            ret[arg_key] = {'type': 'ref', 'value': arg_value[2:-1] if arg_value[1] == '(' else arg_value[1:]}
            print(ret[arg_key])
        else:
            ret[arg_key] = {'type': 'val', 'value': arg_value}
    return ret


def format_arg(arg):
    if isinstance(arg, str) and arg[0] == '$':
        return ({'type': 'ref', 'value': arg[2:-1] if arg[1] == '(' else arg[1:]})
    else:
        return ({'type': 'val', 'value': arg})


def format_event_data(args, event_data):
    final_args = {}
    for key, val in args.items():
        if val['type'] == 'ref':
            final_args[key] = event_data[val['value']]
        else:
            final_args[key] = val['value']
    return final_args


def format_event_value(arg, event_val):
    if arg['type'] == 'ref':
        return event_val[arg['value']]
    else:
        return arg['value']
