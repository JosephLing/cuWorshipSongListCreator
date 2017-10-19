from powerpoint import  loadSongs, openSong

def processSong(song):
    song, song_list, credits_stuff = openSong(song)
    output = '#Title={}\n#Editor=Generated using https://github.com/JosephLing/cuWorshipSongListCreator\n#Author={}#CCLI={}'.\
        format(
        "".join(song.split("\\")[-1]).replace(".txt", "").replace("-", " "),
        credits_stuff[0],
        credits_stuff[1]
    )
    output += "---\n    "
    for i in range(len(song_list)):
        output += song_list[i][0]
        output += "".join(song_list[i][1])
        if i != len(song_list)-1:
            output += "---\n"

    with open(song.replace(".txt", ".sng"), "wb") as f:
        f.write(output)

def runDir(directory):
    songs = loadSongs(directory)
    for song in songs:
        processSong(song)

def main():
    for file in ["worshipNight_1", "worshipNight_2"]:
        runDir(file)

if __name__ == '__main__':
    main()