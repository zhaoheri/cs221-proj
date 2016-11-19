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
                if not polygon:
                    continue
                stroke.add(direction, polygon)
                if is_pause == 'P':
                    stroke.build()
                    self.strokes.append(stroke)
                    stroke = Stroke()


class Stroke:
    def __init__(self):
        self.directions = []    # list of direction
        self.polygons = []  # list of polygon list
        self.central = (0, 0)   # initial central point for this stroke

    def add(self, direction, polygon):
        self.directions.append(direction)
        self.polygons.append(polygon)

    def build(self):
        tmp = []
        for polygon in self.polygons:
            avg_x = sum([eval(x) for (x, y) in polygon]) / float(len(polygon))
            avg_y = sum([eval(y) for (x, y) in polygon]) / float(len(polygon))
            tmp.append((avg_x, avg_y))
        self.central = (sum([x for (x, y) in tmp])/float(len(tmp)),
                        sum([y for (x, y) in tmp])/float(len(tmp)))


bigram = defaultdict(int)    # (stroke1, stroke2) -> cost
trainingNum = 0


def readTrainingSet():
    with open('data/trainingData', 'r') as f:
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
        self.strokes = strokes  # [str(s.directions) for s in strokes]
        self.bigramCost = bigramCost

    def startState(self):
        return str((None, range(len(self.strokes))))

    def isEnd(self, state):
        state = eval(state)
        if state[0] is None:
            return False
        return True if len(state[1]) == 0 else False

    # state: (pre_index, left_index_list)
    def succAndCost(self, state):
        state = eval(state)
        result = []
        pre_index = state[0]
        left_index = state[1]
        if pre_index is None:
            result.append((left_index[0], str((left_index[0], left_index[1:])), 0))
        else:
            for i in range(len(left_index)):
                post_index = left_index[i]
                pre_stroke = str(self.strokes[pre_index].directions)
                post_stroke = str(self.strokes[post_index].directions)
                if self.bigramCost[(pre_stroke, post_stroke)] != 0:
                    cost = self.bigramCost[(pre_stroke, post_stroke)]
                else:
                    cost = trainingNum
                dist_cost = abs(self.strokes[pre_index].central[0] - self.strokes[post_index].central[0]) \
                            + abs(self.strokes[pre_index].central[1] - self.strokes[post_index].central[1])
                cost += dist_cost / float(0.3)
                left_index_copy = left_index[:]
                left_index_copy.remove(post_index)
                result.append((post_index, str((post_index, left_index_copy)), cost))
        return result


def getResult(strokes, bigramCost):
    if len(strokes) == 0:
        return ''
    ucs = util.UniformCostSearch(verbose=0)
    ucs.solve(strokeReoderProblem(strokes, bigramCost))
    return ucs.actions


def test():
    with open('data/testingData', 'r') as f:
        lines = f.readlines()
        correct = defaultdict(int)
        total = defaultdict(int)
        for i, line in enumerate(lines):
            c = Character(eval(line))
            strokes_len = len(c.strokes)
            if strokes_len == 1:
                print line
            if strokes_len > 7 or strokes_len == 1 or strokes_len == 2:
                continue
            total[strokes_len] += 1
            res_index = getResult(c.strokes, bigram)
            res = []
            for idx in res_index:
                res.append(str(c.strokes[idx].directions))
            ans = [str(s.directions) for s in c.strokes]
            if res == ans:
                print 'correct!!! len(strokes) = %d' % len(res)
                correct[strokes_len] += 1

            print 'correct = %s, total = %s' % (correct, total)

    for k in correct:
        print 'strokes_len = %d, correct = %d, total = %d, accuracy = %f' % (k, correct[k], total[k], correct[k] / float(total[k]))

readTrainingSet()
# print bigram

# char = ["#1NO:107,48;158,39;165,37;171,35;176,33;181,32;194,32;201,34;208,38;211,41;213,43;180,49;179,47;177,46;172,46;165,48;121,60;116,61;105,61;100,59;96,56;94,54;93,52;94,50;96,49;","#4PO:203,57;198,65;194,73;190,82;186,90;177,104;168,116;151,134;140,143;134,148;126,152;114,158;100,163;85,168;68,173;61,174;55,175;54,174;54,172;59,169;78,161;100,150;117,140;130,131;138,124;144,118;152,109;159,100;166,87;172,75;178,60;180,52;181,49;179,46;211,41;213,43;214,46;210,50;206,54;"]
# c = Character(char)
# print len(c.strokes)
# print c.strokes[0].central
# print [str(s.directions) for s in c.strokes] == getResult(c.strokes, bigram)

test()


