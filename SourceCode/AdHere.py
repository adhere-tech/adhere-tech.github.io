# coding=utf-8

from selenium import webdriver
from selenium.common.exceptions import TimeoutException as SeleniumTimeoutException
from selenium.common.exceptions import NoSuchElementException as SeleniumNoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import time
import os
import sys
import wmi
import copy
from lxml import etree

ENABLE_DEBUG = 1
DEBUG_NO_HEADLESS = 0
DEBUG_DETAILED_CHECK_ELEMENT = 0
DEBUG_MORE_TIME_TO_CHECK_SOURCE_CODE = 0
SHOW_FIX_SUGGESTIONS = 0

WEB_DRIVER_PATH = './chromedriver.exe'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 ' \
     'Safari/537.36'

########################################################
# Please fill this variable before running this script.
# Input the user profile location of Google Chrome between the quotation marks.
USRPROFILE = ''
########################################################

# It is official ABP plugin, only works under headless mode.
# You can use https://crx-checker.appspot.com/ to check the signature.
ABP_PATH = 'extension_3_7_0_0.crx'
# this Adblock Plus plugin is repacked using Chrome, because it (Adblock-Plus_v3.7.crx) was CRX2 format, which is no
# longer supported by Chrome after Chrome 78. Repacking it makes it not having a valid signature anymore. If you
# concern about it, I suggest you repacking the plugin by yourself. Through I didn't do anything strange to it,
# I don't guarantee its safety.
# For non-headless mode
ABP_NO_HEADLESS_PATH = 'extension_3_7_0_0_repacked.crx'

DEPTH_LIMIT = 50
# page hunting will stop after this number of seconds
# able to check around 14k-16k elements within 600 seconds limit
TIMEOUT_SECOND = 600
# watchdog timer for ad hunting
watchdog_begin_timestamp = 0
# elements checked in a single web page
watchdog_elements_checked = 0
watchdog_print_timeout_info = 0

# [index, domain, platform, ad type, ad characteristics, target element, element's XPATH, [ad network addresses]]
adHuntingResult = []
potentialAdResult = []
# Mobile resolution  640*360 (Galaxy S5)
MOBILE_HEIGHT = 640
MOBILE_WIDTH = 360
MOBILE_LARGE_THRESHOLD = 192  # 640*0.3=192
# Desktop resolution 1366*768
DESKTOP_HEIGHT = 768
DESKTOP_WIDTH = 1366
DESKTOP_LARGE_THRESHOLD = 231  # 768*0.3=230.4
# DEFINE 'STICK TO A SIDE' AS: DISTANCE TO BORDER IS LESS THAN STICKY_THRESHOLD OF SCREEN SIZE
STICKY_THRESHOLD = 0.05
# add an attribute when the parser meets a iframe
CUSTOMIZED_FRAME_ATTR = 'AdHuntingFrameNumber'
# special split pattern for output file, because Python list contains comma, so split pattern is not comma anymore
OUTPUT_SPLIT_PATTERN = '|'

CUSTOM_KEYWORD_FILTER = []
CUSTOM_DOMAIN_FILTER = []
CUSTOM_HTML_ATTR_FILTER = []
CUSTOM_XPATH_FILTER = []

suggestion_output = []


def currTime():
    return time.strftime("%m-%d %H:%M:%S", time.localtime())


def killChromeAndChromedriver_win32(onlyKillChromedriver=False):
    wmiHandler = wmi.WMI()
    try:
        if not onlyKillChromedriver:
            for process in wmiHandler.Win32_Process(name="chrome.exe"):
                process.Terminate()
                if ENABLE_DEBUG:
                    print('[G]chrome.exe killed')
        for process in wmiHandler.Win32_Process(name="chromedriver.exe"):
            process.Terminate()
            if ENABLE_DEBUG:
                print('[G]chromedriver.exe killed')
    except:
        pass


def AdHuntingInit():
    caps = DesiredCapabilities().CHROME
    # caps["pageLoadStrategy"] = "normal"       # complete
    caps["pageLoadStrategy"] = "eager"  # interactive
    # caps["pageLoadStrategy"] = "none"         # never waits

    mobile_emulation = {'deviceName': 'Galaxy S5'}
    mobileOptions = webdriver.ChromeOptions()
    if ENABLE_DEBUG and DEBUG_NO_HEADLESS:
        pass
    else:
        mobileOptions.add_argument("--headless")
    mobileOptions.add_argument('--no-sandbox')
    mobileOptions.add_argument('--disable-gpu')
    mobileOptions.add_argument('--ignore-certificate-errors')
    mobileOptions.add_experimental_option("mobileEmulation", mobile_emulation)
    mobileOptions.add_argument('--user-data-dir=' + USRPROFILE)
    mobileOptions.add_argument('--user-agent=' + UA)
    mobileOptions.add_argument('--disable-popup-blocking')

    desktopOptions = webdriver.ChromeOptions()
    if ENABLE_DEBUG and DEBUG_NO_HEADLESS:
        pass
    else:
        desktopOptions.add_argument("--headless")
    desktopOptions.add_argument('--no-sandbox')
    desktopOptions.add_argument('--disable-gpu')
    desktopOptions.add_argument('--ignore-certificate-errors')
    desktopOptions.add_argument('--user-data-dir=' + USRPROFILE)
    desktopOptions.add_argument('--user-agent=' + UA)
    desktopOptions.add_argument('--disable-popup-blocking')

    mobileOptions_WithPlugin = copy.deepcopy(mobileOptions)
    if DEBUG_NO_HEADLESS:
        mobileOptions_WithPlugin.add_extension(ABP_NO_HEADLESS_PATH)
    else:
        mobileOptions_WithPlugin.add_argument("load-extension=" + ABP_PATH)
    desktopOptions_WithPlugin = copy.deepcopy(desktopOptions)
    if DEBUG_NO_HEADLESS:
        desktopOptions_WithPlugin.add_extension(ABP_NO_HEADLESS_PATH)
    else:
        desktopOptions_WithPlugin.add_argument("load-extension=" + ABP_PATH)
    return mobileOptions, desktopOptions, caps, mobileOptions_WithPlugin, desktopOptions_WithPlugin


# based on https://stackoverflow.com/questions/47069382/want-to-retrieve-xpath-of-given-webelement/47088726#47088726
# slightly modified to suit Python syntax
def getXPATH(driver, element, prefix=''):
    return (prefix + driver.execute_script(
        "function absoluteXPath(element) {" +
        "var comp, comps = [];" +
        "var parent = null;" +
        "var xpath = '';" +
        "var getPos = function(element) {" +
        "var position = 1, curNode;" +
        "if (element.nodeType == Node.ATTRIBUTE_NODE) {" +
        "return null;" +
        "}" +
        "for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {" +
        "if (curNode.nodeName == element.nodeName) {" +
        "++position;" +
        "}" +
        "}" +
        "return position;" +
        "};" +
        "if (element instanceof Document) {" +
        "return '/';" +
        "}" +
        "for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? " +
        "element.ownerElement : element.parentNode) {" +
        "comp = comps[comps.length] = {};" +
        "switch (element.nodeType) {" +
        "case Node.TEXT_NODE:" +
        "comp.name = 'text()';" +
        "break;" +
        "case Node.ATTRIBUTE_NODE:" +
        "comp.name = '@' + element.nodeName;" +
        "break;" +
        "case Node.PROCESSING_INSTRUCTION_NODE:" +
        "comp.name = 'processing-instruction()';" +
        "break;" +
        "case Node.COMMENT_NODE:" +
        "comp.name = 'comment()';" +
        "break;" +
        "case Node.ELEMENT_NODE:" +
        "comp.name = element.nodeName;" +
        "break;" +
        "}" +
        "comp.position = getPos(element);" +
        "}" +
        "for (var i = comps.length - 1; i >= 0; i--) {" +
        "comp = comps[i];" +
        "xpath += '/' + comp.name.toLowerCase();" +
        "if (comp.position !== null) {" +
        "xpath += '[' + comp.position + ']';" +
        "}" +
        "}" +
        "return xpath;" +
        "} return absoluteXPath(arguments[0]);", element))


# JS function called in fullAttr is from
# stackoverflow.com/questions/32537339/getting-the-values-of-all-the-css-properties-of-a-selected-element-in-selenium
# With slight modification
def getCompleteCSSAttribute(driver, element):
    fullAttr = driver.execute_script('var items = {};' +
                                     'var c = getComputedStyle(arguments[0]);' +
                                     'var len = c.length;' +
                                     'for (index = 0; index < len; index++)' +
                                     '{items [c[index]] = c.getPropertyValue(c[index])};' +
                                     'return items;', element)

    # getBoundingClientRect() returns offsetWidth, offsetHeight, and so on
    altAttr = driver.execute_script('return arguments[0].getBoundingClientRect();', element)

    attr = [fullAttr['visibility'], fullAttr['display'],  # decide if element is visible
            fullAttr['height'], fullAttr['width'],  # 30%
            fullAttr['position'], fullAttr['z-index'],  # pop-up, sticky
            fullAttr['bottom'], fullAttr['top'], fullAttr['left'], fullAttr['right']]  # sticky

    # overlap imprecise attributes from getBoundingClientRect()
    attr[2] = int(altAttr['height'])
    attr[3] = int(altAttr['width'])
    attr[6] = int(altAttr['bottom'])
    attr[7] = int(altAttr['top'])
    attr[8] = int(altAttr['left'])
    attr[9] = int(altAttr['right'])

    return attr


def is_displayed_using_attr(attr):
    # visible
    if attr[0] == 'hidden' or attr[0] == 'collapse' or attr[1] == 'none':
        return False
    # size X*Y (X, Y > 0)
    if attr[2] == 0 or attr[3] == 0:
        return False
    return True


# recursive DFS implementation
# using is_displayed_using_attr() instead of element.is_displayed()
def checkElement(driver, adInfo, element, platform, iframeXPATHPrefix='', depth=0):
    # introduce a simple watchdog timer to check timeout
    global watchdog_begin_timestamp
    global watchdog_elements_checked
    global watchdog_print_timeout_info
    if int(time.time()) - watchdog_begin_timestamp >= TIMEOUT_SECOND:
        if ENABLE_DEBUG and watchdog_print_timeout_info:  # debug
            print('[Watchdog]TIMEOUT @ check elements! Elements checked: '
                  + str(watchdog_elements_checked))  # debug
            watchdog_print_timeout_info = 0
        return
    watchdog_elements_checked += 1

    # obtain related CSS attributes of the element
    attr = getCompleteCSSAttribute(driver, element)
    currXPATH = iframeXPATHPrefix + getXPATH(driver, element)

    # video
    if (element.tag_name == 'video' or element.tag_name == 'amp-video') and is_displayed_using_attr(attr):
        if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
            print(element.tag_name, currXPATH, element.get_attribute('autoplay'),
                  element.get_attribute('muted'), attr)  # debug
        if element.get_attribute('autoplay') == 'autoplay' and \
                not element.get_attribute('muted'):
            if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
                print('Auto Ad Confirmed:', element.tag_name, currXPATH)
            adInfo.append(['auto', [], element.tag_name, currXPATH])
            # treat it as a leaf node, ignore any children of it
            return

    iframeProcess = 0
    children = element.find_elements(By.XPATH, 'child::*')

    # iframe
    if element.tag_name == 'iframe' and is_displayed_using_attr(attr):
        if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
            print(element.tag_name, currXPATH, attr)  # debug
        if element.get_attribute('innerHTML').isspace() or \
                element.get_attribute('innerHTML').rstrip(" \n\r\t").lstrip('\n\r\t') == '#document':
            if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
                print('Empty visible iframe: id=', element.get_attribute('id'), element.get_attribute('src'))
            pass
        else:
            # non-empty iframe
            if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
                print('Find visible iframe: id=', element.get_attribute('id'), element.get_attribute('src'))
            # normal iframe
            iframeProcess = 1
            iframeXPATHPrefix = currXPATH  # should support multilayer iframe
            driver.switch_to.frame(element)  # dive into iframe
            if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
                print('DIVE INTO IFRAME')
            children = [driver.find_element(By.XPATH, '/html')]  # relocate root to html tag in iframe
    # other elements (except iframe and video)
    elif is_displayed_using_attr(attr):  # non-visible node is ignored
        if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
            print(element.tag_name, currXPATH, attr, end='')  # debug
        # detect pop-up and large sticky: locate at detailed element
        if (attr[4] == 'fixed' or attr[4] == 'absolute') and attr[5] != 'auto' and int(attr[5]) > 0:
            # judge if current element is sticking to a side of page
            # 6:bottom 7:top 8:left 9:right. All in pixel, distance from left above
            if platform == 'desktop' and (
                    attr[6] > (DESKTOP_HEIGHT * (1 - STICKY_THRESHOLD)) or
                    attr[7] < (DESKTOP_HEIGHT * STICKY_THRESHOLD) or
                    attr[8] < (DESKTOP_WIDTH * STICKY_THRESHOLD) or
                    attr[9] > (DESKTOP_WIDTH * (1 - STICKY_THRESHOLD))):
                if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
                    print('Large Sticky Ad? :', element.tag_name, currXPATH)
                adInfo.append(['sticky', [attr[4], attr[5], attr[6], attr[7], attr[8], attr[9]],
                               element.tag_name, currXPATH])
                return  # treat it as leaf node, ignore any children of it
            elif platform == 'mobile' and (attr[6] > (MOBILE_HEIGHT * (1 - STICKY_THRESHOLD)) or
                                           attr[7] < (MOBILE_HEIGHT * STICKY_THRESHOLD) or
                                           attr[8] < (MOBILE_WIDTH * STICKY_THRESHOLD) or
                                           attr[9] > (MOBILE_WIDTH * (1 - STICKY_THRESHOLD))):
                if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
                    print('Large Sticky Ad? :', element.tag_name, currXPATH)
                adInfo.append(['sticky', [attr[4], attr[5], attr[6], attr[7], attr[8], attr[9]],
                               element.tag_name, currXPATH])
                return  # treat it as leaf node, ignore any children of it
            else:  # element stay in the center of screen
                if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
                    print('Pop Up Ad? :', [attr[4], attr[5]],
                          element.tag_name, currXPATH)
                adInfo.append(['pop', [attr[4], attr[5]],
                               element.tag_name, currXPATH])
                return  # treat it as leaf node, ignore any children of it
        elif not children:
            if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:  # debug
                print(' <- LEAF')  # debug
        else:
            if is_displayed_using_attr(attr) and ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:  # debug
                print('')  # debug
        if element.tag_name == 'amp-ad' or element.tag_name == 'amp-auto-ads' or element.tag_name == 'amp-sticky-ad':
            try:
                if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:
                    print('----------> AMP Ad found! <-----------')
                    print(element.tag_name, element.get_attribute('outerHTML'))
            except Exception as e:
                print(e)
    # leaf node
    if not children:
        pass
    else:
        # found some huge websites contains more than 1,000 layers of elements, so make an limitation
        # to avoid stack overflow and accelerate the calculation
        if depth < DEPTH_LIMIT - 1:
            # recursively visit children
            for i in children:
                try:
                    checkElement(driver, adInfo, i, platform, iframeXPATHPrefix, depth=depth + 1)
                except Exception as e:
                    print(i.tag_name, iframeXPATHPrefix + getXPATH(driver, i), e)

    # escape from iframe
    if iframeProcess:
        driver.switch_to.parent_frame()
        if ENABLE_DEBUG and DEBUG_DETAILED_CHECK_ELEMENT:  # debug
            print('ESCAPE FROM IFRAME')


# lxml will remove 'useless' <html><body> tag in iframe, so this function will also removes these two tags from xpath
# it will NOT remove <html><body> at main document since lxml will not remove them either
def lxmlSpecificXPATHProcessor(xpath):
    return xpath.replace('/iframe[1]/html[1]/body[1]', '/iframe[1]')


# collect all ad network information from ad element to root
def getAllAddresses(website, target_xpath, inputType='file'):
    if inputType == 'file':
        tree = etree.parse(website, etree.HTMLParser())
    elif inputType == 'text':
        tree = etree.HTML(website).getroottree()
    else:
        raise Exception('Invalid inputType')
    target_element = tree.xpath(target_xpath)
    if len(target_element) != 1:
        raise Exception('Multi/None element(s) found @ ' + str(target_xpath) + '. exiting...')
    target_element = target_element[0]
    # print(etree.tostring(target_element, pretty_print='True', method='html').decode('utf-8'))
    parent = target_element.getparent()
    ret = []
    # check current element
    if target_element.get('src') is not None:
        ret.append(target_element.get('src'))
    elif target_element.get('href') is not None:
        ret.append(target_element.get('href'))
    # current -> root
    while parent != tree.getroot():
        if parent.get('src') is not None:
            ret.append(parent.get('src'))
        elif parent.get('href') is not None:
            ret.append(parent.get('href'))
        parent = parent.getparent()
    # root
    if parent.get('src') is not None:
        ret.append(parent.get('src'))
    elif parent.get('href') is not None:
        ret.append(parent.get('href'))
    return ret


def subGetAllAddr_extended(element):
    addrs = []
    children = element.getchildren()
    if not children:
        if element.get('src') is not None:
            return [element.tag, element.get('src')]
        elif element.get('href') is not None:
            return [element.tag, element.get('href')]
        else:
            # return [element.tag]
            pass
    else:
        if element.get('src') is not None:
            addrs.append([element.tag, element.get('src')])
        elif element.get('href') is not None:
            addrs.append([element.tag, element.get('href')])
        else:
            # addrs.append([element.tag])
            pass
        for i in children:
            addrs.append(subGetAllAddr_extended(i))
    return addrs


def getAllAddr_extended(website, target_xpath, inputType='file'):
    if website == '' or target_xpath == '':
        return []
    if inputType == 'file':
        tree = etree.parse(website, etree.HTMLParser())
        # raise Exception('Not implemented! getAllAddr_iframe only accept \'text\' as inputType, but receive ', inputType)
    elif inputType == 'text':
        tree = etree.HTML(website).getroottree()
    else:
        raise Exception('Invalid inputType: ', inputType)
    target_element = tree.xpath(target_xpath)
    if len(target_element) != 1:
        raise Exception('Multi/None element(s) found @ ' + str(target_xpath) + '. exiting...')
    target_element = target_element[0]
    links = []
    # find all links in element, using BFS. Result: everything -> element
    for i in target_element.getchildren():
        links.append(subGetAllAddr_extended(i))
    # all links in element -> root: use existing logic
    remaining = getAllAddresses(website, target_xpath, inputType)
    # merge everything -> element -> root
    remaining.append(links)
    return remaining


def subFindCompletePage(driver, depth):
    global watchdog_begin_timestamp
    global watchdog_elements_checked
    global watchdog_print_timeout_info
    if int(time.time()) - watchdog_begin_timestamp >= TIMEOUT_SECOND:
        if ENABLE_DEBUG and watchdog_print_timeout_info:  # debug
            print('[Watchdog]TIMEOUT @ find complete page! Elements checked: '
                  + str(watchdog_elements_checked))
            watchdog_print_timeout_info = 0
        return

    if depth >= DEPTH_LIMIT:
        # print('[F]Reach maximum depth limit!')
        return '<ERROR id="MAX_DEPTH_LIMIT"></ERROR>'
    try:
        frames = driver.find_elements_by_tag_name('iframe')
        index = 0
        for eachFrame in frames:
            driver.execute_script("arguments[0].setAttribute(arguments[1],arguments[2])", eachFrame,
                                  CUSTOMIZED_FRAME_ATTR, str(depth) + '_' + str(index))
            driver.switch_to.frame(eachFrame)
            framePageSource = subFindCompletePage(driver, depth + 1)
            driver.switch_to.parent_frame()
            driver.execute_script("arguments[0].innerHTML = arguments[1];", eachFrame, str(framePageSource))
            index += 1
        completePage = driver.page_source
    except Exception as e:
        print('[F]find complete page error:', e)
        return '<ERROR id="SUBFRAME_FAIL"></ERROR>'
    return completePage


# attach all iframe page into currentPage
def findCompletePage(driver):
    try:
        driver.switch_to.default_content()
        completePage = driver.page_source
    except Exception as e:
        print('[F]find complete page init error:', e)
        return ''
    try:
        driver.switch_to.default_content()
        frames = driver.find_elements_by_tag_name('iframe')
        index = 0
        for eachFrame in frames:
            driver.execute_script("arguments[0].setAttribute(arguments[1],arguments[2])", eachFrame,
                                  CUSTOMIZED_FRAME_ATTR, '0_' + str(index))
            driver.switch_to.frame(eachFrame)
            framePageSource = subFindCompletePage(driver, 1)
            driver.switch_to.parent_frame()
            driver.execute_script("arguments[0].innerHTML = arguments[1];", eachFrame, str(framePageSource))
            index += 1
        completePage = driver.page_source
    except Exception as e:
        print('[F]find complete page error:', e)
        return completePage
    return completePage


def SinglePageAdHunting(options, options_wP, caps, addr, domain, index, platform):
    ret = []
    if platform == 'mobile':
        ret = [0, 0, 0, 0, 0, 0, 0, 0]  # pop/auto/sticky/pre/30%/flashing/pos_cd/scroll
    elif platform == 'desktop':
        ret = [0, 0, 0, 0]  # pop/auto/sticky/pre_cd

    adInfo = []

    if ENABLE_DEBUG:
        print(time.strftime("[SA]%m-%d %H:%M:%S", time.localtime())
              + '[' + addr + ']Ad hunting starts')

    browser = webdriver.Chrome(executable_path=WEB_DRIVER_PATH, options=options, desired_capabilities=caps)
    if platform == 'desktop':
        browser.set_window_size(1366, 768)
    try:
        browser.delete_all_cookies()
        browser.set_page_load_timeout(15)
        browser.set_script_timeout(15)

        browser.get('https://www.' + domain)  # directly grab from online websites
        # wait for fully (resource and structure) loaded
        WebDriverWait(browser, 10).until(lambda br: br.execute_script('return document.readyState') == 'complete')
    except SeleniumTimeoutException:
        browser.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')

    # introduce similar process in step 1)
    # slowly scroll down
    browser.execute_script('window.scrollTo(0,document.body.scrollHeight/4)')
    time.sleep(0.2)
    browser.execute_script('window.scrollTo(0,document.body.scrollHeight*2/4)')
    time.sleep(0.2)
    browser.execute_script('window.scrollTo(0,document.body.scrollHeight*3/4)')
    time.sleep(0.2)
    browser.execute_script('window.scrollTo(0,document.body.scrollHeight)')
    time.sleep(0.2)

    # slowly scroll up
    browser.execute_script('window.scrollTo(0,0)')
    time.sleep(0.2)

    time.sleep(15)
    # =======================
    try:
        browser.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')
        global watchdog_begin_timestamp
        global watchdog_elements_checked
        global watchdog_print_timeout_info
        watchdog_begin_timestamp = int(time.time())
        watchdog_elements_checked = 0
        watchdog_print_timeout_info = 1
        root = browser.find_element(By.XPATH, "/html")
        checkElement(browser, adInfo, root, platform, depth=0)
    except Exception as e:
        print(e)

    # current adInfo: [ad type, ad chars, target element, element's XPATH]

    # get complete page source file, including HTML content in iframe
    completePage = findCompletePage(browser)

    # adding ad network info into adInfo
    for i in range(len(adInfo)):
        adNetworks = []
        try:
            # adInfo[i][3] is XPATH
            # for ad elements that may contain children:
            if adInfo[i][0] == 'sticky' or adInfo[i][0] == 'pop':
                adNetworks = getAllAddr_extended(completePage, lxmlSpecificXPATHProcessor(adInfo[i][3]), 'text')
            # for ad elements that are leaf nodes:
            else:
                adNetworks = getAllAddresses(completePage, lxmlSpecificXPATHProcessor(adInfo[i][3]), 'text')
        except Exception as e:
            print(e)
        adInfo[i].append(adNetworks)
    # current adInfo: [ad type, ad chars, target element, element's XPATH, [ad network addresses]]

    if ENABLE_DEBUG and DEBUG_NO_HEADLESS:
        sleepTime = 1
        if DEBUG_MORE_TIME_TO_CHECK_SOURCE_CODE:
            sleepTime = 60
        time.sleep(sleepTime)

    # close the browser
    browser.quit()

    # =====================================================================================
    # verify the ad using ad-blocker-loaded browser, check the same website, online
    if adInfo:
        browser_wP = webdriver.Chrome(executable_path=WEB_DRIVER_PATH, options=options_wP, desired_capabilities=caps)
        try:
            browser_wP.set_page_load_timeout(15)
            browser_wP.set_script_timeout(15)

            browser_wP.get('https://www.' + domain)  # directly grab from online websites
            WebDriverWait(browser_wP, 10).until(
                lambda br: br.execute_script('return document.readyState') == 'complete')
        except SeleniumTimeoutException:
            browser_wP.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')
        # check if potential violating ads still exist and visible in current web page,
        # kick out visible candidates
        # stored info: [index, domain, platform,
        #               ad type, ad chars, target element, element's XPATH, [ad network addresses]]
        browser_wP.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')
        # current adInfo: [ad type, ad chars, target element, element's XPATH, [ad network addresses]]
        for i in adInfo:
            adConfirmed = 0
            # =============
            if i[0] == 'auto':  # auto doesn't need double confirmation
                if SHOW_FIX_SUGGESTIONS:
                    print('====\n', 'An', 'Auto-playing Video Ad with Sound', 'on', platform, 'is found!')
                    print('DOM element\'s id:', i[2])
                    print('DOM element\'s xpath:', i[3])
                    print('Violating attributes:', '\'autoplay=autoplay\' and no \'muted\'')
                    print('--\n', 'fix suggestions:')
                    print('1. Add \'muted\' attribute, or remove \'autoplay\' attribute. OR,')
                    print('2. Completely remove the entire ad element.')
                    print('====')
                suggestion_output.append(' '.join(['====']))
                suggestion_output.append(
                    ' '.join(['An', 'Auto-playing Video Ad with Sound', 'on', platform, 'is found!']))
                suggestion_output.append(' '.join(['DOM element\'s id:', i[2]]))
                suggestion_output.append(' '.join(['DOM element\'s xpath:', i[3]]))
                suggestion_output.append(' '.join(['Violating attributes:', '\'autoplay=autoplay\' and no \'muted\'']))
                suggestion_output.append(' '.join(['--']))
                suggestion_output.append(' '.join(['fix suggestions:']))
                suggestion_output.append(
                    ' '.join(['1. Add \'muted\' attribute, or remove \'autoplay\' attribute. OR,']))
                suggestion_output.append(' '.join(['2. Completely remove the entire ad element.']))
                suggestion_output.append(' '.join(['====']))
                adHuntingResult.append([index, domain, platform, i[0], i[1], i[2], i[3], i[4]])
                ret[1] += 1
                continue
            try:
                element = browser_wP.find_element(By.XPATH, i[2])  # is this element existing? N -> Ad confirmed
                if not is_displayed_using_attr(
                        getCompleteCSSAttribute(browser_wP, element)):  # is this element blocked? Y -> Ad confirmed
                    adConfirmed = 1
            except SeleniumNoSuchElementException:  # missing, Ad confirmed
                adConfirmed = 1
            # =============
            if adConfirmed:
                #if ENABLE_DEBUG and not SHOW_FIX_SUGGESTIONS:
                    #print('AD Confirmed', i)
                adHuntingResult.append([index, domain, platform, i[0], i[1], i[2], i[3], i[4]])
                if i[0] == 'sticky':
                    ret[2] += 1
                    if SHOW_FIX_SUGGESTIONS:
                        print('====\n', 'A', 'Large Sticky Ad', 'on', platform, 'is found!')
                        print('DOM element\'s id:', i[2])
                        print('DOM element\'s xpath:', i[3])
                        print('Violating attributes:', '\'position\':', i[1][0], '\'z-index\':', i[1][1],
                              '\'bottom\':', i[1][0], '\'top\':', i[1][0], '\'left\':', i[1][0], '\'right\':', i[1][0])
                        print('--\n', 'fix suggestions:')
                        print('1. Set \'position\' attribute to \'relative\' or \'static\'. OR,')
                        print('2. Set \'z-index\' attribute to 0 or lower. OR,')
                        print('3. Completely remove the entire ad element.')
                        print('====')
                    suggestion_output.append(' '.join(['====']))
                    suggestion_output.append(' '.join(['A', 'Large Sticky Ad', 'on', platform, 'is found!']))
                    suggestion_output.append(' '.join(['DOM element\'s id:', i[2]]))
                    suggestion_output.append(' '.join(['DOM element\'s xpath:', i[3]]))
                    suggestion_output.append(
                        ' '.join(['Violating attributes:', '\'position\':', i[1][0], '\'z-index\':', i[1][1],
                                  '\'bottom\':', i[1][0], '\'top\':', i[1][0], '\'left\':', i[1][0], '\'right\':',
                                  i[1][0]]))
                    suggestion_output.append(' '.join(['--']))
                    suggestion_output.append(' '.join(['fix suggestions:']))
                    suggestion_output.append(
                        ' '.join(['1. Set \'position\' attribute to \'relative\' or \'static\'. OR,']))
                    suggestion_output.append(' '.join(['2. Set \'z-index\' attribute to 0 or lower. OR,']))
                    suggestion_output.append(' '.join(['3. Completely remove the entire ad element.']))
                    suggestion_output.append(' '.join(['====']))
                elif i[0] == 'pop':
                    ret[0] += 1
                    if SHOW_FIX_SUGGESTIONS:
                        print('====\n', 'A', 'Pop-up Ad', 'on', platform, 'is found!')
                        print('DOM element\'s id:', i[2])
                        print('DOM element\'s xpath:', i[3])
                        print('Violating attributes:', '\'position\':', i[1][0], '\'z-index\':', i[1][1])
                        print('--\n', 'fix suggestions:')
                        print('1. Set \'position\' attribute to \'relative\' or \'static\'. OR,')
                        print('2. Set \'z-index\' attribute to 0 or lower. OR,')
                        print('3. Completely remove the entire ad element.')
                        print('====')
                    suggestion_output.append(' '.join(['====']))
                    suggestion_output.append(' '.join(['A', 'Pop-up Ad', 'on', platform, 'is found!']))
                    suggestion_output.append(' '.join(['DOM element\'s id:', i[2]]))
                    suggestion_output.append(' '.join(['DOM element\'s xpath:', i[3]]))
                    suggestion_output.append(' '.join(['Violating attributes:', '\'position\':', i[1][0], '\'z-index\':', i[1][1]]))
                    suggestion_output.append(' '.join(['--']))
                    suggestion_output.append(' '.join(['fix suggestions:']))
                    suggestion_output.append(' '.join(['1. Set \'position\' attribute to \'relative\' or \'static\'. OR,']))
                    suggestion_output.append(' '.join(['2. Set \'z-index\' attribute to 0 or lower. OR,']))
                    suggestion_output.append(' '.join(['3. Completely remove the entire ad element.']))
                    suggestion_output.append(' '.join(['====']))
                else:
                    pass

        if DEBUG_NO_HEADLESS and ENABLE_DEBUG:
            time.sleep(1)
        browser_wP.quit()
        # for debug: store ad info
        for i in adInfo:
            potentialAdResult.append([index, domain, platform, i[0], i[1], i[2], i[3], i[4]])
    else:
        pass
    if ENABLE_DEBUG:
        print('[SA]' + currTime() + '[' + addr + ']Ad hunting finished')
    return ret


def AdHuntingOnce(url):
    # _wP = withPlugin
    mO, dO, caps, mO_wP, dO_wP = AdHuntingInit()
    websiteCounter = [0, 0, 0]
    dAdCounter = [0, 0, 0, 0]
    mAdCounter = [0, 0, 0, 0, 0, 0, 0, 0]
    startTime = time.strftime("[%m_%d]%H_%M_%S", time.localtime())
    if ENABLE_DEBUG:
        print(time.strftime("[A] %m-%d %H:%M:%S", time.localtime())
              + ' General initialization finished')

    killChromeAndChromedriver_win32()

    if ENABLE_DEBUG:
        print(time.strftime("[A] %m-%d %H:%M:%S", time.localtime())
              + ' MOBILE AdHere initialization finished')
    try:
        ret = SinglePageAdHunting(mO, mO_wP, caps, url, url, 0, 'mobile')
    except Exception as e:
        print(e)
        ret = []
    websiteCounter[1] += 1
    for i in range(len(ret)):
        mAdCounter[i] += ret[i]
    if ENABLE_DEBUG:
        print(time.strftime("[A] %m-%d %H:%M:%S", time.localtime())
              + ' DESKTOP AdHere initialization finished')
    try:
        ret = SinglePageAdHunting(dO, dO_wP, caps, url, url, url, 'desktop')
    except Exception as e:
        print(e)
        ret = []
    websiteCounter[2] += 1
    for i in range(len(ret)):
        dAdCounter[i] += ret[i]

    websiteCounter[0] += 1

    killChromeAndChromedriver_win32()

    if ENABLE_DEBUG:
        print('[A]', 'AdHere successfully completes the execution.')

    if ENABLE_DEBUG:
        # print(currTime() + ' AdHuntingResult\n' + str(adHuntingResult))
        pass

    try:
        f = open('violations.txt', mode='w', encoding='utf-8')
        if len(suggestion_output):
            f.write('Following are violations and fix suggestions found by AdHere on ' + url + '\n')
        else:
            f.write('It seems like AdHere doesn\'t find violating ads on ' + url + ' this time. \n')
        for i in suggestion_output:
            f.write(i)
            f.write('\n')
        f.close()
        print('Violations and fix suggestions have been saved to violations.txt')
    except:
        raise Exception('Unable to write the result to violations.txt!')


def SanityCheck(paras):
    try:
        if USRPROFILE == '':
            raise Exception('Please fill Google Chrome\'s user profile location')
    except:
        raise Exception('Please fill Google Chrome\'s user profile location in USRPROFILE global variable')

    if not os.path.exists(WEB_DRIVER_PATH):
        raise Exception('Unable to find Chromedriver')

    if len(sys.argv) < 2:
        targetURL = 'cnet.com'
        print('No input domain given, will perform ad hunting on ' + targetURL)
    else:
        targetURL = sys.argv[1]
        print('Input domain found, will perform ad hunting on ' + targetURL)
    return targetURL


if __name__ == '__main__':
    url = SanityCheck(sys.argv)
    AdHuntingOnce(url)
