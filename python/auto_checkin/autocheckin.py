import urllib.request
import http.cookiejar
import json
import logutil


POST_DATA = {'username':'x', 'password': 'y', 'login.x':'-382', 'login.y':'-416', 'loginSignal':'0'}
URL_CONTEXT # eg. URL_CONTEXT = 'http://123.207.8.234:8887'
# remove me if neccessary
if not URL_CONTEXT:
    print('you need set URL_CONTEXT variable before use this module')
    return

REQUEST_HEADER = {
    'Host': '124.207.8.234:8887',
    'Accept':' text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'
}
# 北京， 东城区
LOCATION_DATA = 'cnwsignoutVO.province=%B1%B1%BE%A9%CA%D0&cnwsignoutVO.city=%CA%D0%CF%BD%C7%F8&cnwsignoutVO.county=%B6%AB%B3%C7%C7%F8'
log = logutil.get_logger()

class LoginFailureException(Exception):pass

class AutoCheckin:
    def __init__(self):
        self._set_up_cookiejar()

    def _get_header_meta(self):
        return REQUEST_HEADER.copy()

    def _get_json_header(self):
        header = self._get_header_meta()
        header['x-requested-with'] = 'XMLHttpRequest'
        header['Accept'] = 'application/json, text/javascript, */*'
        return header

    def save_file(self, filename, contents):
        log.info('save file' + filename)

    def _add_cookie_header(self, cookiejar, req):
        list = []
        for cookie in cookiejar:
            list.append('%s=%s' % (cookie.name, cookie.value))
        req.add_header('Cookie', ';'.join(list))
    
    def _set_up_cookiejar(self):
        policy = http.cookiejar.DefaultCookiePolicy(rfc2965=True, hide_cookie2=False)
        self._cookiejar = http.cookiejar.CookieJar(policy)

    def _request(self, path, headers=None, method='GET', data=None, extract_cookies=False, set_cookie_to_header=True):
        req = urllib.request.Request(URL_CONTEXT + path, headers=headers, method=method)

        if set_cookie_to_header:
            self._add_cookie_header(self._cookiejar, req)

        if data:
            req.data = data

        resp = urllib.request.urlopen(req)

        if extract_cookies:
            self._cookiejar.extract_cookies(resp, req)

        content = resp.read().decode('GBK')
        return content.strip()

    def login(self):
        '''
        Returns:
            LoginFailureException if login failed
        '''
        if not self._is_login_success(self._do_login()):
            raise LoginFailureException('Failed to login user#%s, invalid username or password' % self.get_user()['username'])

    def _do_login(self):
        result = self._request('/ltrc/login.do?method=login', self._get_header_meta(), 
            extract_cookies=True, data=urllib.parse.urlencode(self.get_user()).encode('ISO-8859-1'), method='POST')
        return result

    def _is_login_success(self, resp_content):
        '''
        check user had successfully logined, or not

        :param resp_content: _do_login method's returned result
        ''' 
        return False if '登录失败' in resp_content else True

    def _checkin(self):
        if not self._is_checkin_alreay():
            self._do_checkin()

    def _is_checkin_alreay(self):
        """
        Returns:
            True: already checked in 
            False: Otherwise
        """
        content = self._request('/ltrc/dailyAction.do?method=checkDoneSignAndBack&flag=sign', self._get_json_header())
        # result = True if 'error' in content else False
        result = self._is_poke_error(content)
        log.info('checkin content for user #%s: %s' % (self.get_user()['username'], content))
        log.info('user #%s checkin status: %s' % (self.get_user()['username'], str(result)))
        return result

    def _do_checkin(self):
        content = self._request('/ltrc/dailyAction.do?method=sign', self._get_header_meta(), 
            method='POST', 
            data=LOCATION_DATA.encode('ISO-8859-1'))
        log.info('do _do_checkin for user #%s' % self.get_user()['username'])

    def _checkout(self):
        if not self._is_checkout_already():
            self._do_checkout()

    def _is_checkout_already(self):
        """
        Returns:
            True: already checked out
            False: Otherwise
        """
        content = self._request('/ltrc/dailyAction.do?method=checkDoneSignAndBack&flag=signback', self._get_json_header())
        is_checked_out = self._is_poke_error(content) # todo: test it, and replace it
        log.info('user #%s checkout status: %s' % (self.get_user()['username'], str(is_checked_out)))
        return is_checked_out

    def _do_checkout(self):
        content = self._request('/ltrc/dailyAction.do?method=signback', self._get_header_meta(),
            method='POST',
            data=LOCATION_DATA.encode('ISO-8859-1'))
        log.info('_do_checkout #%s' % self.get_user()['username'])

    # UTILITY FUNCTIONS --------------------------------------------
    def _is_poke_error(self, result):
        '''
        Returns:
            True: if does match - error: '<err msgs>' -  pattern
            False: Otherwise
        '''
        # regx = re.compile(r'error[\s|\'|\"]*:[\s|\'|\"]*\w[\s|\'|\"]*')
        # return True if regx.search(result) else False
        _j = json.loads(result.replace('\'', '\"'))
        return True if _j['error'] else False

    # ----- PUBLIC METHODS ------------------------------------------
    def get_user(self):
        if not self.user:
            raise Exception('user not been set')
        return self.user

    def set_user(self, _user):
        meta = POST_DATA.copy()
        meta['username'] = _user['username']
        meta['password'] = _user['password']
        self.user = meta
    
    def checkout_user(self, user):
        log.info('start checkout for user: %s' % user.__repr__())
        self.set_user(user)
        self._set_up_cookiejar()
        self.login()
        self._checkout()

    def checkin_user(self, user):
        log.info('start checkin for user: %s' % user.__repr__())
        self.set_user(user)
        self._set_up_cookiejar()
        self.login()
        self._checkin()


def checkin(user):
    try:
        AutoCheckin().checkin_user(user)
    except Exception as e:
        log.exception(e)

def checkout(user):
    try:
        AutoCheckin().checkout_user(user)
    except Exception as e:
        log.exception(e)


# --------------------------------------------------------------------------------------------------
# def get_header_meta():
#     return REQUEST_HEADER.copy()

# def get_json_header():
#     header = get_header_meta()
#     header['x-requested-with'] = 'XMLHttpRequest'
#     header['Accept'] = 'application/json, text/javascript, */*'
#     return header

# def save_file(filename, contents):
#     with open(filename, 'w+') as f:
#         f.write(contents)

# def add_cookie_header(cookiejar, req):
#     list = []
#     for cookie in cookiejar:
#         list.append('%s=%s' % (cookie.name, cookie.value))
#     req.add_header('Cookie', ';'.join(list))

# try:
#     # first visit inorder to get JSESSIONID

#     policy = http.cookiejar.DefaultCookiePolicy(rfc2965=True, hide_cookie2=False)
#     _cookiejar = http.cookiejar.CookieJar(policy)
#     # req_header = get_header_meta()
#     # first_visit_req = urllib.request.Request(URL_CONTEXT + '/ltrc/login.jsp', headers=get_header_meta(), method='GET')
#     # first_visit_resp = urllib.request.urlopen(first_visit_req)
#     # fisrt_visit_content = first_visit_resp.read().decode('gbk')
#     # save_file('first_visite.html', fisrt_visit_content)
#     # _cookiejar.extract_cookies(first_visit_resp, first_visit_req)
#     # print(_cookiejar)
#     # print('\n----------------------------\n')

#     # login request
#     login_req = urllib.request.Request(URL_CONTEXT+'/ltrc/login.do?method=login', headers=get_header_meta(), method='POST')
#     add_cookie_header(_cookiejar, login_req)
#     login_req.data = urllib.parse.urlencode(POST_DATA).encode('ISO-8859-1')
#     login_resp = urllib.request.urlopen(login_req)
#     _cookiejar.extract_cookies(login_resp, login_req)
#     save_file('login_resp.html', login_resp.read().decode('gbk'))


#     # poke signin action
#     poke_signin_req = urllib.request.Request(URL_CONTEXT+'/ltrc/dailyAction.do?method=checkDoneSignAndBack&flag=sign', headers=get_json_header(), method='GET')
#     add_cookie_header(_cookiejar, poke_signin_req)
#     poke_signin_resp = urllib.request.urlopen(poke_signin_req)
#     poke_singin_result = poke_signin_resp.read().decode('GBK')
#     poke_signin_json_result = json.loads(poke_singin_result.replace('\'', '\"'))
#     print('\n------------------------\n' + poke_signin_json_result['error'])
#     save_file('poke_singin.json', poke_singin_result)

# except Exception as e:
#     print('exception raised')
#     raise e
