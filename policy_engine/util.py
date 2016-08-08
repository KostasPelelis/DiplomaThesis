def format_args(args, namespace):
	ret = []
	for arg in args:
		if arg in namespace:
			ret.append({'type': 'ref', 'value': arg})
		else:
			ret.append({'type': 'val', 'value': arg})
	return ret

def format_kwargs(kwargs, namespace):
	ret = {}
	for arg_key, arg_value in kwargs.items():
		if arg_value in namespace:
			ret[arg_key] = {'type': 'ref', 'value': arg_value}
		else:
			ret[arg_key] = {'type': 'val', 'value': arg_value}
	return ret
