import telepot
from telepot.loop import MessageLoop
import sys

def cargarHanzi(fileName):
	hanziDict = open(fileName,"r")
	for hanziPin in hanziDict:
		# separamos los elementos y armamos las listas
		reg = hanziPin.split("|")
		listHan.append(reg[0])
		listPin.append(reg[1])
def getPinyin(hanzi):
	i = 0
	for elemList in listHan:
		if (elemList == hanzi):
			return listPin[i]
		i += 1	



######################## MAIN #######################

listHan = []
listPin = []	

cargarHanzi("hanzi.txt")
hanzi = sys.argv[1]
pinyin = getPinyin(hanzi)
print("hanzi: "+hanzi+" pinyin: "+pinyin)
