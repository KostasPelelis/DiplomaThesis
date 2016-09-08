def format_arg(arg):
    if isinstance(arg, str) and arg[0] == '$':
        arg = arg.replace(' ', '')
        return ({'type': 'ref', 'value': arg[2:-1] if arg[1] == '(' else arg[1:]})
    else:
        return ({'type': 'val', 'value': arg})

def format_args(args, filter_methods):
    ret = []
    for arg in args:
        ret.append(format_arg(arg))
    return ret

def format_kwargs(kwargs):
    ret = {}
    for arg_key, arg_value in kwargs.items():
        if isinstance(arg_value, str) and arg_value[0] == '$':
            arg_value = arg_value.replace(' ', '')
            ret[arg_key] = {'type': 'ref', 'value': arg_value[2:-1] if arg_value[1] == '(' else arg_value[1:]}
        else:
            ret[arg_key] = {'type': 'val', 'value': arg_value}
    return ret


def format_event_value(arg, event_val, filter_methods):
    if not isinstance(arg['value'], str):
        return arg['value']
    filter_parts = [p for p in arg['value'].split('|')] 
    val = filter_parts[0]
    if arg['type'] == 'ref':
        val = event_val[val]
    if len(filter_parts) > 1:
        filters = filter_parts[1:]
        for filter_name in filters:
            filter_func = filter_methods.get(filter_name) 
            if filter_func is not None:
                val = filter_func(val)
            else:
                print('Unknown filter name {0}'.format(filter))            
    return val

def format_event_data(args, event_data, filter_methods):
    final_args = {}
    for key, arg in args.items():
        final_args[key] = format_event_value(arg, event_data, filter_methods)
    return final_args


