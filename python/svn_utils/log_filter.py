"""
requires: python3, svn command line client: Slik-Subversion-1.8.10-win32.msi is recommanded

#References:
    http://svnbook.red-bean.com/en/1.1/re15.html
    http://www.vandyke.com/support/tips/scripting/index.html
    http://www.vandyke.com/support/securecrt/python_examples.html

    https://pypi.python.org/pypi/paramiko/1.15.1 | 下载想办法先做一个依赖secureFX的python脚本，下一次迭代再做一个独立的版本
"""
import datetime
from subprocess import Popen, PIPE

class Entry(object):
    """docstring for Entry"""
    def __init__(self, revision, author, date, paths):
        super(Entry, self).__init__()

        self.revision = revision
        self.author = author
        self.date = date
        self.paths = paths

    def __str__(self):
        return 'revision: %s, author: %s, date: %s, paths: %s' % (self.revision, self.author, self.date, '\n\t' + '\n\t'.join(self.paths))


def request(cmd):
    print('issue request: ' + cmd)
    popen = Popen(cmd, shell=True, stdout=PIPE)
    with open('out.xml', mode='bw+') as optfile:
        optfile.write(popen.communicate()[0])

def to_cmd_revision(url, revision_number):
    return 'svn log -v --xml -r %s %s' % (revision_number, url)

def to_cmd_date(url, date_from, date_to):
    """
    :param date_from: 2014-09-18
    :param date_to[optional]: 2014-09-19, if omited, it is the date been called
    """
    date_to = date_to if date_to else datetime.datetime.now().strftime('%Y-%m-%d')
    cmd = 'svn log -v --xml -r {%s}:{%s} %s' % (date_from, date_to, url)
    return cmd

def parse_entries():
    import xml.etree.ElementTree as ET

    tree = ET.parse('out.xml')
    root = tree.getroot()

    entries = []
    for logentry in root.iter('logentry'):
        revision = logentry.get('revision')
        """
        <logentry revision="9888">
          <author>miujing</author>
          <date>2014-09-18T02:11:43.232285Z</date>
          <paths>
             <path action="M" kind="file">/cpcai6.0/WebRoot/js/lottery/lottery_common.js
             </path>
          </paths>
          <msg>FIX: IE下彩种无法提交的bug</msg>
        </logentry>
        """
        author = logentry.find('author').text
        date = logentry.find('date').text

        paths = []
        for path in logentry.find('paths'):
            paths.append(path.text.strip())

        entry = Entry(revision, author, date, paths)
        entries.append(entry)

    return entries

def filter(f, entries):
    return [entry for entry in entries if f(entry)]

def filter_by_author(author, entries):
    return filter(lambda entry: author in entry.author, entries)

def get_changed_files(entries):
    result = []
    for entry in entries:
        result += entry.paths
    return sorted(list(set(result)))

if __name__ == '__main__':
    # entries = parse_entries()
    # entries = filter_by_author('miujing', entries)
    # https://docs.python.org/3.4/howto/argparse.html
    #
    """
    <url> -a <author> -d <date_from> [date_to] -ac <action>

    examples:
        py log_filter.py http://218.249.108.181:8000/svn/cp/cpcai6.0 -a miujing  [-re 4223 | -d 2014-09-18 2014-09-19 ] -ac list_changed_files
    """
    import argparse
    
    #------------------------ START: set up params --------------------------------------
    parser = argparse.ArgumentParser(description='SVN 工具包')
    #parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument('url', help='SVN 路径地址, 只指定此参数会生成xml svn记录文件')
    parser.add_argument('-a', '--author', help="Filter: 作者名称")
    
    parser.add_argument('-ac', '--action', help='动作: *list_changed_files:罗列改动过的文件 ')
    group = parser.add_mutually_exclusive_group(required=True) # at least of one in the group is specified
    group.add_argument('-re', '--revision', help='对应的版本号', type=int)
    # nargs 指定参数的个数, 如果值为2参数值就必须是2个, + 号代表1到多个
    group.add_argument('-d', '--date', help='Filter: 日期 <date_from> [date_to], 格式:yyyy-MM-dd', nargs='+')
    args = parser.parse_args()
    print('url: %s, author: %s, date: %s' % (args.url, args.author, args.date))
    #------------------------ START: set up params --------------------------------------
    
    if args.revision:
        cmd = to_cmd_revision(args.url, args.revision)
    if args.date:
        cmd = to_cmd_date(args.url, args.date[0], args.date[1])

    request(cmd)

    if args.action == 'list_changed_files':
        entries = parse_entries()
        if args.author is not None:
            entries = filter_by_author(args.author, entries)
        files = get_changed_files(entries)
        with open('result.txt', mode='w+') as outf:
            outf.write('\n'.join(files))
        print('list_changed_files succeed!')

"""
todo:
    optionally we can parse date from text string use time module's strptime method

    print out the result file abs path
"""