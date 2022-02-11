from light import LightState

class LastState:

    FILENAME = "laststate.txt"

    def load():
        try:
            with open(LastState.FILENAME, "r") as fin:
                s = fin.read()
                return int(s)
        except:
            return LightState.OFF

    def save(mode):
        with open(LastState.FILENAME, "w") as fout:
            fout.write("%d\n" % mode)


