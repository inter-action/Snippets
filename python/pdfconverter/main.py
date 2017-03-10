import urllib.request
import re
import os


#third party
import pdfcrowd

# local
import config_loader
import argument_parser

def get_title(target_url):
    print("try to get target_ur's title: ", target_url)
    try:
        resp = urllib.request.urlopen(target_url)
        lines = resp.readlines()
        for line in lines:
            sline = line.decode().strip()
            if sline == "": continue
            if not isinstance(sline, str):
                raise Exception('not str')
            (error, title) = parse_title(sline)
            if error == None and title != None:
                return title
        return ""
    except urllib.error.HTTPError as e:
        print("skip parsing title")
        print("try to get target_url's title failed, reason: ", e)
        return ""

    

def parse_title(line):
    # line = "<title>Machine Learning :: Text feature extraction (tf-idf) &#8211; Part I | Terra Incognita</title>"
    regex = r"<title>(.*?)</title>"
    matchObj = re.match(regex, line, re.I | re.M)

    if matchObj:
        title = re.sub(r"[^\w@.]", "-", matchObj.group(1))
        title = re.sub(r"-+", "-", title)
        return (None, title)
    else:
        return (Exception("failed to parse title"), None)

def parse_args():
    # args = argument_parser.parse_args(sys.argv) 
    # target_url = args["url"]
    #     if target_url is None or target_url is "":
    #         print("url argment is required")
    #         sys.exit(1)
    #     max_page = args["maxpage"]
    #     if max_page is not None:
    #         max_page = int(max_page)
    #     else
    #         max_page = None
    # print("args is ", args)

    target_url = input("* please enter your target url, required!: \n")
    if target_url == "":
        raise Exception("url is required")
    
    parse_title = input("* parse title?(y/[n])!: \n")
    if parse_title.lower() == "n":
        parse_title = False
    else:
        parse_title = True

    max_page = input("please enter max page to generate, optional: \n")
    if max_page == "":
        max_page = None
    else:
        max_page = int(max_page)

    return {"target_url": target_url, "max_page": max_page, "parse_title": parse_title}

def kick_start(args):
    try:
        # create an API client instance
        configs = config_loader.get_config()
        client = pdfcrowd.Client(configs["username"], configs["apikey"])

        if args["max_page"] is not None:
            client.setMaxPages(args["max_page"])
        
        print("I'am on the mission now, please wait...")

        target_url = args["target_url"]
        # todo: make this concurrent
        if args["parse_title"] is True:
            title = get_title(target_url)
        else:
            title = ""

        if title is "":
            title = "file"

        # convert a web page and store the generated PDF into a pdf variable
        pdf = client.convertURI(target_url)
        
        output_path = configs["output_path"]
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # convert an HTML file
        with open("{}/{}.pdf".format(output_path, title), "wb") as output_file:
            output_file.write(pdf)

        print("convert file sucessfully")
    except pdfcrowd.Error as why:
        print('Failed: {}'.format(why))
        return 1

if __name__ == '__main__':
    import sys
    
    args = parse_args()
    sys.exit(int(kick_start(args) or 0))


