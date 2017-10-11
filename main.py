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



def connectedToInternet():
    """
    :return: True if connected otherwise false
    """
    status_code = 0
    try:
        status_code = requests.get("http://www.google.com").status_code
    except requests.exceptions.ConnectTimeout:
        logging.warning("Connection timed out [ConnectionTimeOut]")
    except requests.exceptions.ConnectionError:
        logging.warning("Cannot connect to internet [ConnectionError]")

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
    page = soup.find("div", {"class":"chord-pro-disp"})
    if page is not None:
        for div in page.find_all("div"):
            if div.get("class") == ["chord-pro-br"]:
                data.append("")
            elif div.get("class") == ["chord-pro-line"]:
                data.append("".join([segment.getText() for segment in div.find_all("div", {"class":"chord-pro-lyric"})]))

    return data

def save(name, data):
    with open(OUTPUT_PATH + name, "wb") as f:
        f.write(("\n".join(data)).encode('utf-8').strip().replace(u"\u2018", "'").replace(u"\u2019", "'"))


def logErrors(name, type_song="default"):
    with open(OUTPUT_PATH + type_song + "errors.txt", "ab") as f:
        f.write(name + "\n")


def processSong(name, type_song="default"):
    success = True
    song = getSong(name)
    if len(song) > 0:
        save(type_song + os.path.sep + name, song)
    else:
        logErrors(name, type_song + os.path.sep)
        print("could not find song for: " + name)
        success = False
    return success


def loadInSongs(name):
    songs = []
    with open(name) as f:
        songs = f.readlines()
    return [song.split("-")[0].replace("  ", "").replace("\t", "").replace(" ", "-").replace(",", "-").replace("\n", "") for song in songs]

def createDirs(name):
    if not os.path.exists(OUTPUT_PATH + name):
        os.makedirs(OUTPUT_PATH + name)

def main():
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    s = time.time()
    # name = "Forever-Reign"
    # name = "asdf"

    type_of_song = "notWellKnown"
    createDirs(type_of_song)
    createDirs("default")
    found = 0
    songs = loadInSongs(type_of_song + ".txt")
    for song in songs:
        if processSong(song, type_of_song):
            found += 1
    print("found: {0} / {1}".format(found, len(songs)))

    print("finished")
    print(time.time() - s)

    # data = loadInTemplate().render(name="hi")
    # outputAsHtml(data)

    # rooms.append(getRoom(site))


if __name__ == '__main__':
    main()
