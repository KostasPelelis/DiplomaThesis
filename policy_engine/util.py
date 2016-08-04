def format_args(args):
	ret = {}
	for arg in args:
		ret[arg["key"]] = arg["val"]
	return ret