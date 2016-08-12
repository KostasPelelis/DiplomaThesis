def format_args(args):
	ret = []
	for arg in args:
		if isinstance(arg, str) and arg[0] == '$':
			ret.append({'type': 'ref', 'value': arg[1:]})
		else:
			ret.append({'type': 'val', 'value': arg})
	return ret

def format_kwargs(kwargs):
	ret = {}
	for arg_key, arg_value in kwargs.items():
		if isinstance(arg_value, str) and arg_value[0] == '$':
			ret[arg_key] = {'type': 'ref', 'value': arg_value[1:]}
		else:
			ret[arg_key] = {'type': 'val', 'value': arg_value}
	return ret
