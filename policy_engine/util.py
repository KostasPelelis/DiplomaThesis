def format_args(args, namespace):
	ret = []
	for arg in args:
		if arg in event_namespace:
			ret.append({'type': 'ref', 'value': arg})
		else:
			ret.append({'type': 'val', 'value': arg})
	return ret

def format_kwargs(args, namespace):
	ret = {}
	for arg_key, arg_value in data['arguments'].items():
		if arg in event_namespace:
			args[arg_key] = {'type': 'ref', 'value': arg_value}
		else:
			args[arg_key] = {'type': 'val', 'value': arg_value}
	return ret
