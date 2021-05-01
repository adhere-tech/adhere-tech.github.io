# coding=utf-8

import requests
import threading
import time
import os


# Increase the number if you find many errors occur
ERROR_DELAY = 3  # first is DELAY, then DELAY*4, finally DELAY*9
_429_DELAY = 20  # keep constant,stop when Google deny the request
REQUEST_TIMEOUT = 5  # how long a request will time out

TARGET_LIST = 'top-1m.csv'

# =================================
# Please fill these variables before running this script.
# Your API key pool including all keys for the Googel Ad Experience Report API.
API_KEY_LIST = []

# Larger THREAD_COUNT means faster speed, higher load to computer and network. Vice Versa.
# Recommended number: (API keys you have) multiply    1 (poor network or computer performance)
#                                                  to 5 (excellent network AND high computer performance, close to API limitation)
# Lower this number if you find Google APIs are exceeding the use limit or lots of 429 error occurs
# only works for firstScan, not for reScan
THREAD_COUNT = 16
# =================================

PREFIX = 'https://adexperiencereport.googleapis.com/v1/sites/'
SUFFIX = '?fields=desktopSummary(betterAdsStatus%2CenforcementTime%2CfilterStatus%2ClastChangeTime%2CunderReview)' \
         '%2CmobileSummary(betterAdsStatus%2CenforcementTime%2CfilterStatus%2ClastChangeTime%2CunderReview)' \
         '%2CreviewedSite&key= '


def Pattern_Today():
    return time.strftime("[%m_%d", time.localtime())


# find newest created file containing target pattern and without banned pattern
def FindNewestCsvFile(path, pattern, banned_pattern='[R]'):
    possibleFiles = []
    for fileName in os.listdir(path):
        if (str(pattern) in fileName) and \
                (str(banned_pattern) not in fileName) and \
                fileName.endswith('.csv'):
            possibleFiles.append(fileName)
    if not possibleFiles:
        return ''
        # raise Exception("No file containing target pattern " + str(pattern) +
        #                " in path: " + path)
    if len(possibleFiles) == 1:
        return possibleFiles[0]
    else:
        newestFile = possibleFiles[0]
        newestFileCreateTime = os.stat(newestFile).st_ctime
        print(newestFile, newestFileCreateTime)
        for i in range(len(possibleFiles) - 1):
            if newestFileCreateTime < os.stat(possibleFiles[i + 1]).st_ctime:
                newestFile = possibleFiles[i + 1]
                newestFileCreateTime = os.stat(possibleFiles[i + 1]).st_ctime
                print(newestFile, newestFileCreateTime)
        return newestFile


def WEB_GET(serial, startIndex, endIndex, key, lis):  # [start,stop)
    print('==' + str(serial) + '== start: ' + str(startIndex) + ' -> '
          + str(endIndex))
    errorCount = 0
    for i in range(startIndex, endIndex):
        lis[i] = lis[i][:-1]
        mainUrl = lis[i].split(',')[1]
        Url = PREFIX + mainUrl + SUFFIX + key
        try:
            r = requests.get(url=Url, timeout=REQUEST_TIMEOUT)  # GET
            json = r.json()
            if 'error' in json:  # Google error
                print(time.strftime("%m-%d %H:%M:%S", time.localtime())
                      + " Google error on thread " + str(serial) + ' @ '
                      + str(i) + ' with code ' + str(r.status_code))
                lis[i] += ',ERROR,ERROR,' + str(r.status_code) + ',,,,,,,,\n'
                if str(r.status_code) == str(429):
                    time.sleep(_429_DELAY)  # relax
                errorCount = 0
                continue
            mobileSummary = ''
            mChangedTime = ''
            mEnforcementTime = ''
            mFilterStatus = ''
            mUnderReview = ''
            if json['mobileSummary'] == {}:
                mobileSummary = 'UNKNOWN'
            else:
                mobileSummary = json['mobileSummary']['betterAdsStatus']
                mChangedTime = json['mobileSummary']['lastChangeTime']
                mFilterStatus = json['mobileSummary']['filterStatus']
                if mFilterStatus == 'ON':
                    mEnforcementTime = json['mobileSummary']['enforcementTime']
                try:
                    mUnderReview = json['mobileSummary']['underReview']
                except Exception:
                    pass
            desktopSummary = ''
            dChangedTime = ''
            dEnforcementTime = ''
            dFilterStatus = ''
            dUnderReview = ''
            if json['desktopSummary'] == {}:
                desktopSummary = 'UNKNOWN'
            else:
                desktopSummary = json['desktopSummary']['betterAdsStatus']
                dChangedTime = json['desktopSummary']['lastChangeTime']
                dFilterStatus = json['desktopSummary']['filterStatus']
                if dFilterStatus == 'ON':
                    dEnforcementTime = json['desktopSummary']['enforcementTime']
                try:
                    dUnderReview = json['desktopSummary']['underReview']
                except Exception:
                    pass
            errorCount = 0
        except Exception as e:
            print(time.strftime("%m-%d %H:%M:%S", time.localtime())
                  + " Error on thread " + str(serial) + ' @ '
                  + str(i) + '\n' + str(e))
            lis[i] += ',ERROR,ERROR,' + str(-1) + ',,,,,,,,\n'
            if errorCount <= 3:
                errorCount += 1
            time.sleep(ERROR_DELAY * errorCount * errorCount)  # stable improvement
            continue

        # normal response
        lis[i] += (',' + mobileSummary + ',' + desktopSummary + ',' + str(r.status_code) +
                   ',' + mChangedTime + ',' + dChangedTime +
                   ',' + mFilterStatus + ',' + mEnforcementTime + ',' + mUnderReview +
                   ',' + dFilterStatus + ',' + dEnforcementTime + ',' + dUnderReview +
                   '\n')

        # console output
        if (i - startIndex) % 1000 == 0:
            print(time.strftime("%m-%d %H:%M:%S", time.localtime())
                  + ' [' + str(serial) + '] #' + str(i + 1)
                  + ' ({:.2%})'.format((i + 1 - startIndex) / (endIndex - startIndex))
                  + ' completed!')

    # thread end console announce
    print('=-=' + str(serial) + ' finished! =-=')


def reScan(fileName, defaultInput=''):
    if defaultInput == '':
        print('[R]Find corresponding file: ' + fileName)
        print('[R]type \'y\' to continue, \'t\' to test error number')
        userInput = input('>> ')
    else:
        print('[R][AUTO]Find corresponding file: ' + fileName)
        userInput = defaultInput
    if userInput == 'y' or userInput == 't':
        print('[R] ' + time.strftime("%m-%d %H:%M:%S", time.localtime())
              + ' Start rescan!')
        startTiming = time.time()
        if userInput == 'y':
            try:
                r = requests.get(url=(PREFIX + 'google.com' + SUFFIX + API_KEY_LIST[0]),
                                 timeout=REQUEST_TIMEOUT)
                json = r.json()
            except Exception as e:
                print(time.strftime("[R]%m-%d %H:%M:%S", time.localtime())
                      + ' Google API may not reachable, check Internet connection!\n'
                      + str(repr(e)))
                exit()
        f = open(fileName, 'r', encoding='utf-8')
        lis = f.readlines()
        f.close()
        fixCount = 0
        recheckCount = 0
        skipCount = 0
        print('[R] ' + time.strftime("%m-%d %H:%M:%S", time.localtime())
              + ' Reading section finished!')
        inc = 0
        for i in range(len(lis)):
            temp = lis[i][:-1]
            num = temp.split(',')[0]
            mainUrl = temp.split(',')[1]
            try:
                statusCode = temp.split(',')[4]
                dUnderReview = temp.split(',')[12]  # last data available
            except Exception as e:
                print('[R]>Incomplete data found at: ', end=' ')
                print(lis[i], end='')
                statusCode = '-1'
            if (statusCode != str(-1) and       # network error
                    statusCode != str(429)):    # Google API DoS error
                skipCount += 1
                continue                        # will be rechecked, others ignored
            recheckCount += 1
            print(time.strftime("[R]%m-%d %H:%M:%S", time.localtime())
                  + ' Re-checking ' + str(num) + ' ' + mainUrl)
            if userInput == 't':
                continue
            Url = PREFIX + mainUrl + SUFFIX + API_KEY_LIST[inc]
            inc += 1
            if inc >= len(API_KEY_LIST):
                inc = 0
            try:  # GET
                r = requests.get(url=Url, timeout=REQUEST_TIMEOUT * 2)
                json = r.json()
                if 'error' in json:
                    print(time.strftime("[R]%m-%d %H:%M:%S", time.localtime())
                          + ' Google error when rescanning  @ ' + str(num)
                          + ' with code ' + str(r.status_code))
                    lis[i] = (num + ',' + mainUrl + ',ERROR,ERROR,'
                              + str(r.status_code) + ',,,,,,,,\n')
                    time.sleep(_429_DELAY)
                    continue
                mobileSummary = ''
                mChangedTime = ''
                mEnforcementTime = ''
                mFilterStatus = ''
                mUnderReview = ''
                if json['mobileSummary'] == {}:
                    mobileSummary = 'UNKNOWN'
                else:
                    mobileSummary = json['mobileSummary']['betterAdsStatus']
                    mChangedTime = json['mobileSummary']['lastChangeTime']
                    mFilterStatus = json['mobileSummary']['filterStatus']
                    if mFilterStatus == 'ON':
                        mEnforcementTime = json['mobileSummary']['enforcementTime']
                    try:
                        mUnderReview = json['mobileSummary']['underReview']
                    except Exception:
                        pass
                desktopSummary = ''
                dChangedTime = ''
                dEnforcementTime = ''
                dFilterStatus = ''
                dUnderReview = ''
                if json['desktopSummary'] == {}:
                    desktopSummary = 'UNKNOWN'
                else:
                    desktopSummary = json['desktopSummary']['betterAdsStatus']
                    dChangedTime = json['desktopSummary']['lastChangeTime']
                    dFilterStatus = json['desktopSummary']['filterStatus']
                    if dFilterStatus == 'ON':
                        dEnforcementTime = json['desktopSummary']['enforcementTime']
                    try:
                        dUnderReview = json['desktopSummary']['underReview']
                    except Exception:
                        pass
                fixCount += 1
            except Exception as e:
                print(time.strftime("[R]%m-%d %H:%M:%S", time.localtime())
                      + ' Error when rescan  @ ' + str(num) + '\n'
                      + str(e))
                lis[i] = (num + ',' + mainUrl + ',ERROR,ERROR,'
                          + str(-1) + ',,,,,,,,\n')
                time.sleep(ERROR_DELAY)
                continue

            lis[i] = (num + ',' + mainUrl +
                      ',' + mobileSummary + ',' + desktopSummary + ',' + str(r.status_code) +
                      ',' + mChangedTime + ',' + dChangedTime +
                      ',' + mFilterStatus + ',' + mEnforcementTime + ',' + mUnderReview +
                      ',' + dFilterStatus + ',' + dEnforcementTime + ',' + dUnderReview +
                      '\n')

        print('\n[R]' + time.strftime("%m-%d %H:%M:%S", time.localtime())
              + ' API Request section finished!')

        if userInput == 't':
            endTiming = time.time()
            print('---\n[t]Using time (s):' + str(endTiming - startTiming)
                  + '\n> recheck ' + str(recheckCount) + '\n> (in recheck) add '
                  + str(skipCount))
            exit()
        else:
            f1 = open(('[R]' + fileName + '.log'), mode='w', encoding='utf-8')
            f1.write('\n[R]' + time.strftime("%m-%d %H:%M:%S", time.localtime())
                     + ' API Request section finished!\n')
            f = open(('[R]' + fileName), mode='w', encoding='utf-8')
            for i in lis:
                f.write(i)
            f.close()
            endTiming = time.time()
            print('Start at ' + str(time.strftime("%m-%d %H:%M:%S", time.localtime(startTiming))))
            print('---\nUsing time (s):' + str(endTiming - startTiming)
                  + '\n> recheck ' + str(recheckCount) + '\n> (in recheck) add '
                  + str(skipCount) + '\n> fix ' + str(fixCount))
            f1.write('Start at ' + str(time.strftime("%m-%d %H:%M:%S", time.localtime(startTiming))))
            f1.write('---\nUsing time (s):' + str(endTiming - startTiming)
                     + '\n> recheck ' + str(recheckCount) + '\n> (in recheck) add '
                     + str(skipCount) + '\n> fix ' + str(fixCount))
            f1.close()
    print('Bye Bye!')


def firstScan():
    print(time.strftime("%m-%d %H:%M:%S", time.localtime())
          + ' First-time scan start!')
    startTiming = time.time()
    f = open(TARGET_LIST, mode='r', encoding='utf-8')
    lis = f.readlines()
    f.close()
    print(time.strftime("%m-%d %H:%M:%S", time.localtime())
          + ' Reading section complete!')
    try:
        r = requests.get(url=(PREFIX + 'google.com' + SUFFIX
                              + API_KEY_LIST[0]), timeout=REQUEST_TIMEOUT)
        json = r.json()
    except Exception as e:
        print(time.strftime("%m-%d %H:%M:%S", time.localtime())
              + ' [Network Failure]Google API may not reachable, check Internet connection\n'
              + str(repr(e)))
        exit()

    # separate lis and allocate API key
    process_length = len(lis) // THREAD_COUNT + 1
    j = 0
    threadPool = []
    for i in range(THREAD_COUNT):
        if i == THREAD_COUNT - 1:
            endIndex = len(lis)
        else:
            endIndex = (i + 1) * process_length
        t = threading.Thread(target=WEB_GET,
                             args=(i,
                                   min(i * process_length, len(lis)),
                                   min(endIndex, len(lis)),
                                   API_KEY_LIST[j],
                                   lis)
                             )
        # print('Allocating API key No. ' + str(j) + ' to thread #' + str(i))
        threadPool.append(t)
        j += 1
        if j >= len(API_KEY_LIST):
            j = 0
    for i in threadPool:
        i.start()
    for i in threadPool:
        i.join()

    f1 = open('Alexa_done [' + time.strftime("%m_%d %H_%M_%S", time.localtime())
              + '].log', mode='w+', encoding='utf-8')
    f1.write('\n----\n' + time.strftime("%m-%d %H:%M:%S", time.localtime())
             + ' API Request section finished!\n')

    print('\n----\n' + time.strftime("%m-%d %H:%M:%S", time.localtime())
          + ' API Request section finished!\n')

    f = open('Alexa_done [' + time.strftime("%m_%d %H_%M_%S", time.localtime())
             + '].csv', mode='w+', encoding='utf-8')
    for i in lis:
        f.write(i)
    f.close()

    endTiming = time.time()
    f1.write('Start at ' + str(time.strftime("%m-%d %H:%M:%S", time.localtime(startTiming))))
    f1.write('----\nUsing time (s):' + str(endTiming - startTiming)
             + '\nPer website (s) :' + str((endTiming - startTiming) / len(lis)))
    f1.close()

    print('Start at ' + str(time.strftime("%m-%d %H:%M:%S", time.localtime(startTiming))))
    print('----\nUsing time (s):' + str(endTiming - startTiming)
          + '\nPer website (s) :' + str((endTiming - startTiming) / len(lis)))


def runALL():
    today = time.strftime("[%m_%d", time.localtime())

    print('Hello! Today is ' + today + ']')

    existedAPIResultFileName = FindNewestCsvFile(os.curdir, Pattern_Today())

    if existedAPIResultFileName:
        print('One API search have finished today, name: ' + existedAPIResultFileName)
        print('type \'rescan\' to scan for the second time,'
              + '\'quit\' to exit。 Any other input will run first scan\n', end='')
        userInput = input('> ')
    else:
        print('No API search finished today, we are about to do so!')
        userInput = 'firstScan'

    if userInput == 'rescan':
        reScan(existedAPIResultFileName)
    elif userInput == 'quit' or userInput == 'exit':
        print('OK bye bye!')
    else:
        firstScan()
        # automatically start the second scan
        existedAPIResultFileName = FindNewestCsvFile(os.curdir, Pattern_Today())
        if not existedAPIResultFileName:
            raise Exception('[R][Auto]Cannot find first scan file for auto-rescan!')
        reScan(existedAPIResultFileName, 'y')


if __name__ == '__main__':
    runALL()
