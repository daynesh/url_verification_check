import urllib2
import httplib
from time import sleep
from urllib2 import HTTPError
import time

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):  
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)
        result.status = code
        return result                                

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        result.status = code              
        return result

def write_failure(outputfile, src, expected, actual, statuscode):
    outputfile.write("%s," % src)
    outputfile.write("%s," % expected)
    outputfile.write("%s," % actual)
    outputfile.write("%s\n" % str(statuscode))

def main():
    # Initialized variables
    f = open('input.csv', 'r')
    output_failures = open('output_failures.csv', 'w')
    output_failures.write("URL to Test,Expected,Actual,Status Code")
    index = 0
    failures = 0
    sleep_time = 0.10 # 100ms
    ignore_https_check = True
    ignore_trailing_slash = True
    start_time = time.time()

    for line in f:
        index += 1
        if index == 1:
            continue

        pieces = line.split(',')
        src = pieces[0]
        dest = pieces[1]
        original_dest = dest

        # Replace http with https
        if ignore_https_check:
            dest = dest.replace('https', '')
            dest = dest.replace('http', '')
        if ignore_trailing_slash:
            if dest.endswith('/'):
                dest = dest[:-1]

        # Request URL
        try:
            req = urllib2.Request(src)
            opener = urllib2.build_opener(SmartRedirectHandler())
            res = urllib2.urlopen(req)
            res_opener = opener.open(req)
            res.close
        except HTTPError, e:
            print "Failed test!"
            print "  Requesting URL: ", src
            print "    Response code: " + str(e.code)
            failures += 1
            write_failure(output_failures, src, original_dest, "", str(e.code))
            continue


        # Verification
        actual = res_opener.url
        if ignore_https_check:
            actual = actual.replace('https', '')
            actual = actual.replace('http', '')
        if ignore_trailing_slash:
            if actual.endswith('/'):
                actual = actual[:-1]
        
        if actual != dest:
            print "Failed test!"
            print "  Requesting URL: ", src
            print "    Response code: " + str(res_opener.status)
            print "    Expected URL: " + dest
            print "    Actual URL: " + actual
            failures += 1
            write_failure(output_failures, src, original_dest, res_opener.url, str(res_opener.status))

        print "Testing URL #" + str(index-1)
        sleep(sleep_time)


    # total failures
    end_time = time.time()
    output_failures.close
    print "Total failures = " + str(failures)
    print "Completion time: " + str(end_time - start_time)

if __name__ == "__main__":
    main()
