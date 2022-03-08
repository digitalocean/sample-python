#!/usr/bin/env python

####################################################
#                                                  #
#  This bot only works with https://strawpoll.de.  #
#                                                  #
####################################################
# Usage: Main.py [options]
#
# Options:
#   -h, --help            show this help message and exit
#   -v VOTES, --votes=VOTES
#                         number of votes to give
#   -s SURVEY, --survey=SURVEY
#                         id of the survey
#   -t TARGET, --target=TARGET
#                         checkbox to vote for
#   -f, --flush           Deletes skipping proxy list
#
#   EXAMPLE
#
# python Main.py -v 10 -s abbcw17 -t check3537987
#
#



try:
    from xml.dom import minidom
    import xml.etree.cElementTree as ET
    from optparse import OptionParser
    import sys
    import os
except ImportError as msg:
    print("[-] Library not installed: " + str(msg))
    exit()

try:
    import requests
except ImportError:
    print("[-] Missing library 'requests'")
    print("[*] Please install missing library with: pip install requests")

# Creator: Luis Hebendanz
class Main:

    # SETTINGS
    maxVotes = 1
    voteFor = ""
    surveyId = ""

    # GLOBAL VARIABLES
    proxyListFile = "https-proxy-list.xml"
    saveStateFile = "saveState.xml"
    proxyTimeout = 10 # Seconds
    currentProxyPointer = 0
    successfulVotes = 0

    def __init__(self):
        try:

            ###
            # Command line argument parser
            ###
            parser = OptionParser()
            parser.add_option("-v", "--votes", action="store", type="string", dest="votes",help="number of votes to give")
            parser.add_option("-s", "--survey", action="store", type="string", dest="survey",help="id of the survey")
            parser.add_option("-t", "--target", action="store", type="string", dest="target", help="checkbox to vote for")
            parser.add_option("-f", "--flush", action="store_true", dest="flush",help="Deletes skipping proxy list")
            (options, args) = parser.parse_args()

            if len(sys.argv) > 2:
                    if options.votes is None:
                        print("[-] Number of votes not defined with: -v ")
                        exit(1)
                    if options.survey is None:
                        print("[-] Survey id not defined with: -s")
                        exit(1)
                    if options.target is None:
                        print("[-] Target to vote for is not defined with: -t")
                        exit(1)
                    try:
                        self.maxVotes = int(options.votes)
                    except ValueError:
                        print("[-] Please define an integer for -v")

                    # Save arguments into global variable
                    self.voteFor = options.target
                    self.surveyId = options.survey

                    # Flush saveState.xml
                    if options.flush == True:
                        print("[*] Flushing saveState.xml file...")
                        os.remove(self.saveStateFile)

            # Print help
            else:
                print("[-] Not enough arguments given")
                print()
                parser.print_help()
                exit()

            # Read proxy list file
            alreadyUsedProxy = False
            xmldoc = minidom.parse(self.proxyListFile)
            taglist = xmldoc.getElementsByTagName('para')
            tagList2 = None

            # Check if saveState.xml exists and read file
            if os.path.isfile(self.saveStateFile):
                xlmSave = minidom.parse(self.saveStateFile)
                tagList2 = xlmSave.getElementsByTagName("usedProxy")

            # Print remaining proxies
            if tagList2 is not None:
                print("[*] Number of remaining proxies in list: " + str(len(taglist) - len(tagList2)))
                print()
            else:
                print("[*] Number of proxies in new list: " + str(len(taglist)))
                print()

            # Go through proxy list
            for tag in taglist:

                # Check if max votes has been reached
                if self.successfulVotes >= self.maxVotes:
                    break

                # Increase number of used proxy integer
                self.currentProxyPointer += 1

                # Read value out of proxy list
                tagValue = tag.childNodes[0].nodeValue

                # Read in saveState.xml if this proxy has already been used
                if tagList2 is not None:
                    for tag2 in tagList2:
                        if tagValue == tag2.childNodes[0].nodeValue:
                            alreadyUsedProxy = True
                            break

                # If it has been used print message and continue to next proxy
                if alreadyUsedProxy == True:
                    print("["+ str(self.currentProxyPointer) +"] Skipping proxy: " + tagValue)
                    alreadyUsedProxy = False
                    continue

                # Print current proxy information
                print("["+ str(self.currentProxyPointer) +"] New proxy: " + tagValue)
                print("[*] Connecting... ")

                # Connect to strawpoll and send vote
                self.sendToWebApi('https://' + tagValue)

                # Write used proxy into saveState.xml
                self.writeUsedProxy(tagValue)
                print()

            # Check if max votes has been reached
            if self.successfulVotes >= self.maxVotes:
                print("[+] Finished voting: " + str(self.successfulVotes))
            else:
                print("[+] Finished every proxy!")

            exit()
        except IOError as ex:
            print("[-] " + ex.strerror + ": " + ex.filename)

        except KeyboardInterrupt as ex:
            print("[*] Saving last proxy...")
            print("[*] Programm aborted")
            exit()


    def getClientIp(self, httpProxy):
        proxyDictionary = {"https": httpProxy}
        rsp = requests.get("https://api.ipify.org/", proxies=proxyDictionary)
        return str(rsp.text)


    def writeUsedProxy(self, proxyIp):
        if os.path.isfile(self.saveStateFile):
            # Read file
            tree =  ET.parse(self.saveStateFile)
            # Get <root> tag
            root = tree.getroot()
            child = ET.Element("usedProxy")
            child.text = str(proxyIp)
            root.append(child)
            # Write to file
            tree.write(self.saveStateFile, encoding="UTF-8")
        else:
            # Create <root> tag
            root = ET.Element("article")
            # Get element tree
            tree = ET.ElementTree(root)
            # Write to file
            tree.write(self.saveStateFile, encoding="UTF-8")

            # Now write defined entry into file
            self.writeUsedProxy(proxyIp)



    def sendToWebApi(self, httpsProxy):
        try:
            headers = \
                {
                    'Host': 'strawpoll.de',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0',
                    'Accept': '*/*',
                    'Accept-Language': 'de,en-US;q=0.7,en; q=0.3',
                    'Referer': 'https://strawpoll.de/' + self.surveyId,
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Length': '29',
                    'Cookie': 'lang=de',
                    'DNT': '1',
                    'Connection': 'close'
                }
            payload = {'pid': self.surveyId, 'oids': self.voteFor}
            proxyDictionary = {"https": httpsProxy}

            # Connect to server
            r = requests.post('https://strawpoll.de/vote', data=payload, headers=headers, proxies=proxyDictionary, timeout=self.proxyTimeout)
            json = r.json()

            # Check if succeeded
            if(bool(json['success'])):
                print("[+] Successfully voted.")
                self.successfulVotes += 1
                return True
            else:
                print("[-] Voting failed. This Ip already voted.")
                return False

        except requests.exceptions.Timeout as ex:
            print("[-] Timeout")
            return False

        except requests.exceptions.ConnectionError as ex:
            print("[-] Couldn't connect to proxy")
            return False

        except Exception as ex:
            print(str(ex))
            return False

# Execute main
Main()
