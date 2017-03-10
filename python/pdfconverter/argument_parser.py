def parse_args(args):
    """
    parse sys.argv
    python main.py -url www.baidu.com -maxpage 30
    @return
        {url: "www.baidu.com", maxpage: 30}
    """
    result = {}
    args = args[1:]

    s = " ".join(args)
    sa = s.split("-")
    for item in  filter(lambda w: w is not "", sa):
        key = item.split(" ", 1)[0]
        value = item.split(" ", 1)[1]
        result[key] = value
    return result
            