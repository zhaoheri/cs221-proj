import re
from collections import defaultdict
import util


class Character:
    def __init__(self, data):
        self.strokes = []

        stroke = Stroke()
        for part in data:
            find = re.match(r'#(\d)([P,N])[O,R]:(.*)', part)
            if find:
                direction = int(find.group(1))
                is_pause = find.group(2)
                polygon = [tuple(x.split(',')) for x in find.group(3).split(';') if x != '']
                stroke.add(direction, polygon)
                if is_pause == 'P':
                    self.strokes.append(stroke)
                    stroke = Stroke()


class Stroke:
    def __init__(self):
        self.directions = []
        self.polygons = []

    def add(self, direction, polygon):
        self.directions.append(direction)
        self.polygons.append(polygon)


bigram = defaultdict(int)    # (stroke1, stroke2) -> cost
trainingNum = 0


def readTrainingSet():
    with open('trainingData', 'r') as f:
        lines = f.readlines()
        trainingNum = len(lines)
        for line in lines:
            c = Character(eval(line))
            for i in range(len(c.strokes) - 1):
                stroke1 = str(c.strokes[i].directions)
                stroke2 = str(c.strokes[i + 1].directions)
                bigram[(stroke1, stroke2)] += 1
        for k in bigram:
            bigram[k] = trainingNum / float(bigram[k])


class strokeReoderProblem(util.SearchProblem):
    def __init__(self, strokes, bigramCost):
        self.strokes = [str(s.directions) for s in strokes]
        self.bigramCost = bigramCost

    def startState(self):
        return str((None, self.strokes))

    def isEnd(self, state):
        state = eval(state)
        if state[0] is None:
            return False
        return True if len(state[1]) == 0 else False

    def succAndCost(self, state):
        state = eval(state)
        result = []
        pre_stroke = state[0]
        left_strokes = state[1]
        if pre_stroke is None:
            result.append((left_strokes[0], str((left_strokes[0], left_strokes[1:])), 0))
        else:
            for i in range(len(left_strokes)):
                if self.bigramCost[(pre_stroke, left_strokes[i])] != 0:
                    cost = self.bigramCost[(pre_stroke, left_strokes[i])]
                else:
                    cost = trainingNum
                result.append((left_strokes[i], str((left_strokes[i], left_strokes[:i] + left_strokes[i+1:])), cost))
        return result


def getResult(strokes, bigramCost):
    if len(strokes) == 0:
        return ''
    ucs = util.UniformCostSearch(verbose=0)
    ucs.solve(strokeReoderProblem(strokes, bigramCost))
    return ucs.actions


def test():
    with open('testingData', 'r') as f:
        lines = f.readlines()
        correct = defaultdict(int)
        total = defaultdict(int)
        for i, line in enumerate(lines):
            c = Character(eval(line))
            strokes_len = len(c.strokes)
            if strokes_len == 1:
                print line
            if strokes_len > 6 or strokes_len == 1 or strokes_len == 2:
                continue
            total[strokes_len] += 1
            res = getResult(c.strokes, bigram)
            ans = [str(s.directions) for s in c.strokes]
            if res == ans:
                print 'correct!!! len(strokes) = %d' % len(res)
                correct[strokes_len] += 1

            print 'correct = %s, total = %s' % (correct, total)

    for k in correct:
        print 'strokes_len = %d, correct = %d, total = %d, accuracy = %f' % (k, correct[k], total[k], correct[k] / float(total[k]))

readTrainingSet()
# print bigram

# test = ["#3PO:134,99;133,84;133,71;132,60;131,53;129,48;128,45;124,37;127,34;138,35;148,39;154,42;155,48;155,55;153,60;153,67;152,76;152,88;152,102;151,103;151,117;150,135;150,157;148,182;147,211;146,242;131,242;131,239;131,233;131,223;132,210;133,194;133,180;134,164;134,149;134,133;134,116","#1PO:168,120;176,118;185,115;194,112;203,110;210,109;216,109;215,109;224,111;230,114;234,120;230,122;221,125;206,128;196,130;186,132;176,133;166,134;155,134;144,134;144,123;152,123;160,122","#1PR:199,227;176,230;148,233;119,237;96,240;77,242;63,244;53,245;49,245;43,246;36,246;29,246;20,247;14,249;15,248;20,256;27,261;33,263;36,262;42,261;51,260;63,258;78,256;91,255;103,253;116,251;128,250;139,249;151,247;163,246;174,246;183,245;191,245;197,244;203,245;210,245;220,245;231,245;244,245;258,246;269,246;276,246;279,246;281,242;277,237;267,229;258,226;251,223;247,222;242,223;232,224;218,225;"]
# c = Character(test)
# print [str(s.directions) for s in c.strokes] == getResult(c.strokes, bigram)

test()


