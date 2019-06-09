import itertools
from itertools import permutations
from itertools import groupby
from math import factorial
import pdb
import time

'''
Type of Cards:

S -> single
D -> pair
DS-> pairstraight
TRP/T1S/T2D -> triple, tripe(1), triple(2),
STR -> straight
B/B1/B2/B4 -> bomb, bomb(1,1), bomb(2), bomb(2,2)
SB -> Joker/small Joker
TD -> Triple Doulbe

Not casted
double triple, Dtripe(2), Dtriple(2,2),
Triple Triple (3),(2,2,2)
Quarttriple,Quarttriple(4)

Hand = [list of numbers]
Move = user defined class
'''


class Move:
    def __init__(self, kind, num, tagcards):
        self.kind = kind
        self.num = num
        self.tagcards = tagcards

    def __repr__(self):
        return "M({},{},{})".format(self.kind, self.num, self.tagcards)

fullhand = list(range(3,18))
paz = 0
#11 = J, 12=Q, 13=K, 14=A, 15 = 2, 16 = sj, 17 = bj'


def smartMoves(hand1, hand2, lastmove):
    global paz
    cards = [key for key, group in groupby(hand1)]
    cardsfq = [len(list(group)) for key, group in groupby(hand1)]

    #frequency  of cards
    singles = []
    doubles = []
    triples = []
    bombs = []
    for x in range(len(cards)):
        if cardsfq[x] == 1:
            singles.append(cards[x])
        elif cardsfq[x] == 2:
            doubles.append(cards[x])
        elif cardsfq[x] == 3:
            triples.append(cards[x])
        elif cardsfq[x] == 4:
            bombs.append(cards[x])

    straightlist = straight_moves(cards,lastmove)                           # 1. straight
    triplelist = triple_moves(singles,doubles,triples,bombs,lastmove)       # 2. triples
    tdlist = td_moves(singles,doubles,triples,bombs,lastmove)               # 3. tripledouble
    doublelist = double_moves(singles,doubles,triples,bombs,lastmove)       # 4. nature doubles and split doubles
    singlelist = single_moves(cards,lastmove)                               # 5. nature singles
    bomblist = bomb_moves(singles,doubles,triples,bombs,lastmove)           # 6. bomb and special bomb

    moves = list(itertools.chain(straightlist,triplelist,tdlist,doublelist,singlelist,bomblist))

    #Add paz
    if lastmove != paz:
        moves.append(paz)

    return moves

def bomb_moves(singles,doubles,triples,bombs,lastmove):
    bomblist= []
    for z in bombs:
        bomb = Move("B", z, [])
        bomblist.append(bomb)

        if len(singles) > 1:
            bomb1 = Move("B1", z, [singles[0], singles[1]])
            if legalMove(lastmove, bomb1):
                bomblist.append(bomb1)

        if len(doubles) > 0:
            firstd = doubles[0]
            bomb2 = Move("B2", z, [firstd, firstd])
            if legalMove(lastmove, bomb2):
                bomblist.append(bomb2)

        if len(doubles) > 1:
            firstd = doubles[0]
            secondd = doubles[1]
            bomb4 = Move("B4", z, [firstd, firstd, secondd, secondd])
            if legalMove(lastmove, bomb4):
                bomblist.append(bomb4)

    if 16 in singles and 17 in singles:
        specialbomb = Move("SB", 16, [])
        bomblist.append(specialbomb)

    return bomblist


def single_moves(cards, lastmove):
    singlelist = []
    for i in cards:
        single = Move("S", i, [])
        if legalMove(lastmove, single):
            singlelist.append(single)

    return singlelist

def double_moves(singles,doubles,triples,bombs,lastmove):
    # nature double
    start = doubles+triples+bombs
    doublelist = []
    for card in start:
        double = Move("D", card, [])
        if legalMove(lastmove, double):
            doublelist.append(double)

    # split double
    for card in start:
        split = Move("S", card, [])
        if legalMove(lastmove, split):
            doublelist.append(split)

    return doublelist


def straight_moves(cards,lastmove):
    n = 3
    straightlist = [] #list of legal straight moves
    allstraights = [] #list of straight moves
    while n < 11:
        if n in cards:
            cardlen = consec(n,cards)
            if cardlen > 4:
                allstraights = allstraights+ straightComb(n,cardlen)
            n = n + cardlen+1
        else:
            n= n+1

    for h in range(len(allstraights)):
        if legalMove(lastmove,allstraights[h]):
            straightlist.append(allstraights[h])

    return straightlist

def straightComb(start,length):
    straight = []
    end = start + length #3+7=10
    for x in range(5,length+1): #5
        y = start #3
        while (y + x) < (end+1): #3+5<10
            thisline = Move("Str", y ,list(range(y,y + x))) #3,[3,8]
            straight.append(thisline)
            y = y + 1
    
    return straight


def triple_moves(singles,doubles,triples,bombs,lastmove):
    valid_trps = triples + bombs
    triplelist = []
    for card in valid_trps:
        trpmove = Move("TRP",card,[])
        if legalMove (lastmove,trpmove):
            triplelist.append(trpmove)

        for c in singles:
            t1smove =Move("T1S",card,[c])
            if legalMove (lastmove,t1smove):
                triplelist.append(t1smove)

        for d in doubles:
            t1dmove =Move("T1D",card,[d,d])
            if legalMove (lastmove,t1dmove):
                triplelist.append(t1dmove)

            t1dsplitmove = Move("T1S",card,[d])
            if legalMove (lastmove,t1dsplitmove):
                triplelist.append(t1dsplitmove)
    return triplelist

def td_moves(singles,doubles,triples,bombs,lastmove):
    td_candidate = doubles+triples+bombs
    td_movelist= []
    td_list = []
    for q in td_candidate:
        cardlen = consec(q, td_candidate)
        if cardlen > 2:
            td_combo = TDComb(q, cardlen)
            td_movelist += td_combo
    for r in td_movelist:
        if legalMove(lastmove, r):
            td_list.append(r)
    return td_list

def TDComb(start,length): 
    TDtrain = []
    for x in range(3,length+1):
        temp = list(range(start,start+x))
        taglist = sorted(temp + temp)
        thismove = Move("TD", start, taglist)
        TDtrain.append(thismove)
                    
    return TDtrain


def consec(key, keylist):
    counter = 1
    pos = keylist.index(key)
    while pos < (len(keylist)-1) and keylist[pos] + 1 == keylist[pos+1] and keylist[pos+1]<15:
        counter +=1
        pos +=1
    return counter

def legalMove(move,response):
    global paz
    if move == paz and response != paz:
        return True
    elif move != paz and response == paz:
        return True
    elif move == paz and response == paz:
        return False
    elif response.kind == "SB":
        return True
    elif move.kind == response.kind and response.num > move.num and len(response.tagcards) == len(move.tagcards):
        return True
    elif move.kind != "B" and move.kind != "SB" and response.kind == "B":
        return True
    else:
        return False


def fast_solve(p1hand,p2hand,turn,move,mem):
    global count
    count += 1

    key1 = tuple(p1hand)
    key2 = tuple(p2hand)
    key = (key1,key2,turn,move)
    # pdb.set_trace()
    if key in mem:
        return mem[key]

    elif p1hand == []:
        return 1
    elif p2hand == []:
        return 0

    elif turn == 1:
        idealist = smartMoves(p1hand, p2hand, move)
        for nextmove in idealist:
            new_p1hand = play(nextmove,p1hand)
            if fast_solve(new_p1hand,p2hand,2,nextmove,mem) == 1:
                mem[key] = 1
                return 1
        else:
            mem[key] = 0
            return 0
    else: # turn == 2
        idealist = smartMoves(p2hand, p1hand, move)
        for nextmove in idealist:
            new_p2hand = play(nextmove,p2hand)
            if fast_solve(p1hand, new_p2hand, 1, nextmove, mem) == 0:
                mem[key] = 0
                return 0
        else:
            mem[key] = 1
            return 1

def play(move,hand):
    global paz
    if move == paz:
        return hand
    else:
        newhand = hand[:]
        if move.kind == "S":
            newhand.remove(move.num)
        elif move.kind == "D":
            for _ in range(2):
                newhand.remove(move.num)
        elif move.kind =="B" or move.kind =="B1" or move.kind =="B2" or move.kind =="B4":
            for _ in range(4):
                newhand.remove(move.num)
            for x in move.tagcards:
                newhand.remove(x)
        elif move.kind =="T1S" or move.kind =="T1D" or move.kind =="TRP":
            for _ in range(3):
                newhand.remove(move.num)
            for x in move.tagcards:
                newhand.remove(x)
        elif move.kind =="SB":
            newhand.remove(16)
            newhand.remove(17)
        elif move.kind == "Str" or move.kind == "TD":
            for x in move.tagcards:
                newhand.remove(x)
        return newhand

def smartsolve(hand1,hand2,lastmove):
    # always hand1 to move
    # not recursive
    global count
    count = 0
    start_time = time.time()
    hand1 = sorted(hand1)
    hand2 = sorted(hand2)

    idealist = smartMoves(hand1,hand2,lastmove)
    print ("total %s possible moves" % len(idealist))

    if len(idealist) == 1:
        x = idealist[0]
        print ("no other option")
        print (x)
        print("--- %s seconds ---" % (time.time() - start_time))
        print("--- %s nodes searched ---" % count )
        return x
    else:
        mem = {}
        for x in idealist:
            print("currently searching %s" % (x))
            print(count)
            newhand1 = play(x,hand1)
            # pdb.set_trace()
            ideascore = fast_solve(newhand1, hand2, 2, x, mem)
            if ideascore == 1:
                print("sol found")
                print(x)
                print("--- %s seconds ---" % (time.time() - start_time))
                print("--- %s nodes searched ---" % count )
                return x
    print("no sol")
    print("--- %s seconds ---" % (time.time() - start_time))
    print("--- %s nodes searched ---" % count )

def get_input():
    cardtype = input("Your move_Type:")
    cardtype = cardtype.upper()
    if cardtype == "0":
        p2_move = paz
    elif cardtype == "T1S":
        triplenum = int(input("Your Triple move_Number:"))
        tagnum = int(input("Your Tag Card_Number:"))
        p2_move = Move("T1S", triplenum, [tagnum])
    elif cardtype == "T1D":
        triplenum = int(input("Your Triple move_Number:"))
        tagnum = int(input("Your Tag Card_Number:"))
        p2_move = Move("T1S", triplenum, [tagnum, tagnum])
    else:
        cardnum = int(input("Your move_Number:"))
        p2_move = Move(cardtype, cardnum, [])
    return p2_move


def main(hand1, hand2, lastmove):
    global paz
    while hand1 != [] and hand2 != []:
        move1 = smartsolve(hand1,hand2,lastmove)
        move2 = get_input()
        while legalMove(move1,move2)==False:
            print ("illegal move, please enter again:")
            move2 = get_input()

        hand1 = play(move1,hand1)
        print (hand1)
        hand2 = play(move2,hand2)
        print (hand2)
        lastmove = move2



#-----------------------------
count = 0
hand1 = [3,7,8,9,9,9,10,10,11,12,13,15]
hand2 = [3,4,7,9,10,11,11,12,13,14,15,17]
othermove = Move("S",7,[])

main(hand1,hand2,paz)
