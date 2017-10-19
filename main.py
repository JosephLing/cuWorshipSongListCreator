import powerpoint
import scaper
import songbeamer

def main():
    pass

if __name__ == '__main__':
    for files in ["worshipNight_1", "worshipNight_2", "hymns", "notWellKnown", "modernWorship"]:
        scaper.runDir(files)
        powerpoint.runDir(files)
        songbeamer.runDir(files)