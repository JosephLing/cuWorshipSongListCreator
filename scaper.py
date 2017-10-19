import time
import requests
from bs4 import BeautifulSoup
import logging
import os
RATE_LIMITING = 2


def error(msg, url):
    logging.error("{0}\tsource: {1}".format(msg, url))


def warning(msg, url):
    logging.warning("{0}\tsource: {1}".format(msg, url))



OUTPUT_PATH = "output" + os.path.sep
BASE_URL = "http://www.worshiptogether.com/songs/"
FILE_EXTENSION = ".txt"


def connectedToInternet():
    """
    :return: True if connected otherwise false
    """
    status_code = 0
    try:
        status_code = requests.get("http://www.google.com").status_code
    except requests.exceptions.ConnectTimeout:
        warning("Connection timed out [ConnectionTimeOut]")
    except requests.exceptions.ConnectionError:
        warning("Cannot connect to internet [ConnectionError]")

    return status_code == 200


def query(url, params=None, headers_param=None):
    """
    queries the given url and places in the params and headers into the request if present.
    :param url: string
    :param params: dict
    :param headers_param: dict
    :return: string of body of the request result
    """
    if params is None:
        params = {}
    logging.info("url={0}\tparams={1}".format(url, params))
    headers = {
        'Referer': url,
        "Content-Type": "text/xml; charset=UTF-8",  # implement after checking if this doesn't kill the other scripts
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    }
    if headers_param is not None:
        # mergers the headers into one so that the basic headers don't have to duplicated
        for k in headers_param.keys():
            headers[k] = headers_param[k]

    session = requests.session()

    result = session.get(
        url,
        cookies=requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies)),
        headers=headers,
        params=params
    ).text

    time.sleep(RATE_LIMITING)
    return result


def getSong(name):
    data = []
    results = query(BASE_URL + name)
    soup = BeautifulSoup(results, "html.parser")
    author = "Unkown"
    ccli = ""

    taxonomy = soup.find("div", {"class":"song_taxonomy"})
    if taxonomy is not None:
        taxonomy = taxonomy.find_all("div", {"class": "row"})
        author = taxonomy[0].getText().replace("Writer(s):", "").strip()

        found = False
        count = 1
        while (count < len(taxonomy) and not found):
            if "CCLI" in taxonomy[count].getText():
                ccli = taxonomy[count].getText().replace("CCLI #:", "").strip()
                found = True
            count += 1



    page = soup.find("div", {"class":"chord-pro-disp"})
    if page is not None:
        for div in page.find_all("div"):
            if div.get("class") == ["chord-pro-br"]:
                data.append("")
            elif div.get("class") == ["chord-pro-line"]:
                data.append("".join([segment.getText() for segment in div.find_all("div", {"class":"chord-pro-lyric"})]))

        data.append("")
        data.append("Author: " + author)
        data.append("CCLI: " + ccli)
    return data

def save(name, data):
    emptyCount = 0
    final_data = []
    for i in range(len(data)):
        data[i] = data[i].strip()
        if not (i == 0 and data[0] != "" and data[1] == "") and not (
                    data[i - 1].replace(" ", "") == "" and data[i] != "" and data[i + 1].replace(" ", "") == ""):
            if data[i] == "":
                if emptyCount == 0:
                    final_data.append(data[i])
                emptyCount += 1
            else:
                emptyCount = 0
                final_data.append(data[i])
    with open(OUTPUT_PATH + name + FILE_EXTENSION, "wb") as f:
        f.write("\n"+("\n".join(final_data)).strip().replace(u"\u2018", "'").replace(u"\u2019", "'").replace("0xe2", "?").encode('utf-8'))


def logErrors(name, type_song="default"):

    with open(OUTPUT_PATH + type_song + "errors.txt", "ab") as f:
        f.write(name + "\n")


def processSong(name, type_song="default"):
    success = True
    song = getSong(name)
    output = "searching: " + name
    try:
        if len(song) > 0:
            save(type_song + os.path.sep + name, song)
        else:
            logErrors(name, type_song + os.path.sep)
            output += " status: failed"
            success = False

    except Exception as e:
        error(e, "")
        print(e)
        success = False
    print(output)
    return success


def loadInSongs(name):
    songs = []
    with open(name) as f:
        songs = f.readlines()
    return [song.split("-")[0]
                .replace("  ", "")
                .replace("\t", "")
                .replace(" ", "-")
                .replace(",", "-")
                .replace("\n", "") for song in songs]

def createDirs(name):
    if not os.path.exists(OUTPUT_PATH + name):
        os.makedirs(OUTPUT_PATH + name)


def runDir(type_of_song):
    createDirs(type_of_song)
    createDirs("default")
    found = 0
    songs = loadInSongs(type_of_song + ".txt")
    for song in songs:
        if processSong(song, type_of_song):
            found += 1
    print("found: {0} / {1}".format(found, len(songs)))


def main():
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    s = time.time()
    # name = "Forever-Reign"
    # name = "asdf"
    # []
    for file in ["worshipNight_1", "worshipNight_2", "hymns", "notWellKnown", "modernWorship"]:
    # for file in ["temp"]:
        runDir(file)



    print("finished")
    print(time.time() - s)

    # data = loadInTemplate().render(name="hi")
    # outputAsHtml(data)

    # rooms.append(getRoom(site))


if __name__ == '__main__':
    main()