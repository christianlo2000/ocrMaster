import telepot
from telepot.loop import MessageLoop
import sys
import subprocess
import getTextFrom as gtf
import pytesseract
from PIL import Image
import cv2
import qrcode
import time
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# Comentarios: funciona el flavor, lo visualiza pero tira excepcion cuando elige opcion
# Falta tambien tunear los pdf. Las imagenes y los words los procesa rapidisimo!# ya manejamos caracteres polifonos para la parte de Gabi y lo ingresado por teclado
# pero hay que modificar procesarArchivoTxt y ProcesarContenido para que tambien lo contemple
########## Funciones y Metodos
# Funcion Handle de chatbot de telegram
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat Id: %s' % str(chat_id))
    print("content_type: "+str(content_type))
    if (content_type == 'text'):
        # analizamos si el mensaje es inicio del bot /start
        pregunta_inic = msg['text']
        print('pregunta: %s' % pregunta_inic)	
        if (pregunta_inic == "/start"):
            bot.sendMessage(chat_id,"Hola! Bienvenido a ocrMaster Bot. Si necesitas ayuda, contacta a 罗克力")
            return
        else:
            imagen = qrcode.make(pregunta_inic)
            archivo_imagen = open('./output/qrcode.png','wb')
            imagen.save(archivo_imagen)
            archivo_imagen.close()
            bot.sendPhoto(chat_id,photo=open('./output/qrcode.png','rb'))
            return
    if (content_type == 'voice_note'):
        bot.sendMessage(chat_id,"Lo siento, no soporto archivos de videomensaje.")
        return
    if (content_type == 'photo'):
        fileName = "/home/pi/python/ocrMaster/download/image_"+str(chat_id)
        bot.download_file(msg['photo'][-1]['file_id'],fileName)
        # convierto la imagen a texto
        bot.sendMessage(chat_id,"Archivo recibido! Aguarde un momento por favor, estamos procesando la imagen para convertirla a texto ...")
        archSalidaTmp = procesarImagen(fileName,chat_id)
        return

def procesarArchivoPdf(fileName,chat_id):
	""" Lee los archivos pdf y los convierte a texto. Finalmente termina de procesar el archivo invocando a procesarArchivoTxt """
	# convertimos formato pdf a texto
	contenido = gtf.getTextFromPdfHanzi(fileName)
	# abrimos archivo de salida temporario
	# comentamos para optimizar uso de archivos
	#listFil = []
	#listFil = fileName.split(".")
	#tempTxt = listFil[0]+"_txt_temp_"+str(chat_id)
	#tempFile = open(tempTxt,"w")
	#tempFile.write(str(contenido))
	#tempFile.close()
	#procesarArchivoTxt(tempTxt,chat_id)
	# fin de comentarios de optimizacion
	procesarContenido(contenido,chat_id)

def procesarArchivoWord(fileName,chat_id):
	""" Lee los archivos word docx y los convierte a texto. Finalmente temrina de procesar el archivo de texto para agregar el pinyin. """
	contenido = gtf.getTextFromWord(fileName)
	#print("estoy en procesarArchivoWord")
	listFil = []
	listFil = fileName.split(".")
	tempTxt = listFil[0]+"_text_temp_"+str(chat_id)
	tempFile = open(tempTxt,"w")
	tempFile.write(contenido)
	tempFile.close()
	procesarArchivoTxt(tempTxt,chat_id)

def img2Txt(fileName,chat_id):
	image = Image.open(fileName)
	arch_salida = "/home/pi/python/ocrMaster/download/text_"+str(chat_id)+"_temp"
	archOut = open(arch_salida,"w")
	# pasamos la imagen a texto
	try:
		image2Text = pytesseract.image_to_string(image,lang='chi_sim')
		img2Text = image2Text.replace(" ","")
		# grabamos la salida
		archOut.write(image2Text)
		#archOut.write(img2Text)
		archOut.close()
	except:
		bot.sendMessage(chat_id,"No es posible convertir a texto esta imagen. Problemas de resolucion.")
		archOut.close()
		return("NO FUNCO")
	return(arch_salida)

def procesarImagen(fileName,chat_id):
	#image = Image.open(fileName)
	#arch_salida = "/home/pi/python/ocrMaster/download/file_"+str(chat_id)+"_temp"
	try:
            img = cv2.imread(fileName)
            detector = cv2.QRCodeDetector()
            # decodificamos
            data, bbox, stight_code = detector.detectAndDecode(img)
            print("Datos decodificados: "+data)
            bot.sendMessage(chat_id,data)
            return "Ok"
	except:
		bot.sendMessage(chat_id,"No es posible convertir a texto esta imagen. Problemas de resolucion. ")
		return("NO FUNCO")

def procesarArchivoTxt(fileName,chat_id):
	""" lee el archivo de entrada, genera el archivo de salida y lo envia al usuario que lo solicito. """
	# averiguamos el tipo de archivo
	#tipoArch = fileType(fileName)
	#print("tipo archivo: "+tipoArch)
	fileInput = open(fileName,"r")
	fileO = "./output/salida_"+str(chat_id)+".txt"
	fileOutput = open(fileO,"w")
	archInfoSalida = ""
	for reg in fileInput:
		i = 0
		if (str(chat_id) == "677251444"): #  677251444
			# no esta entrando por aca! revisar despues
			lineaPinyin = ""
			# modo Gabi primero hanzi y luego pinyin por linea
			#print("Estoy en modo Gabi")
			while( i < len(reg)):
				pinyin = getPinyin(reg[i:i+1])
				# aveiguro si es polifonico
				if (pinyin.find(",") > -1):
					# es polifonico
					pinyinPoli = getPinyinPolifono(i,reg)
					lineaPinyin += "("+pinyinPoli.rstrip('\n')+")"
				else:
					lineaPinyin += "("+pinyin.rstrip('\n')+")"
				salidaReg = str(reg[i:i+1]).rstrip('\n')
				salidaReg
				archInfoSalida = archInfoSalida+salidaReg
				archInfoSalida = archInfoSalida.replace("(None)","")
				i += 1
			lineaPinyin = lineaPinyin.replace("()","")
			archInfoSalida = archInfoSalida+"   "+lineaPinyin+'\n'
			fileOutput.write(archInfoSalida)
			archInfoSalida = ""
		else:
			# modo standart
			print("Estoy en modo Standard")
			#i = 0
			while( i < len(reg)):
				pinyin = getPinyin(reg[i:i+1])
				 # aveiguro si es polifonico
				if (pinyin.find(",") > -1):
					# es polifonico
					pinyinPoli = getPinyinPolifono(i,reg)
					pinyin = pinyinPoli.rstrip('\n')
				else:
					pinyin = pinyin.rstrip('\n')

				#print("caracter: "+reg[i:i+1])
				salidaReg = str(reg[i:i+1]).rstrip('\n')+"("+str(pinyin).rstrip('\n')+")"
				salidaReg1 = salidaReg.rstrip('\n')
				salidaReg1 = salidaReg1.replace("(None)","")
				#fileOutput.write(salidaReg)
				archInfoSalida = archInfoSalida+salidaReg1
				i += 1
			archInfoSalida = archInfoSalida.replace("()","")
			archInfoSalida = archInfoSalida.replace("(None)","")+'\n'
			# graabamos salida
			fileOutput.write(archInfoSalida)
			archInfoSalida = ""
	fileInput.close()
	fileOutput.close()
	# enviamos archivo de salida
	bot.sendDocument(chat_id,document=open(fileO))

def procesarContenido(contenido,chat_id):
	""" recibe un contenido en texto con caracteres chinos, y le agrega el pinyin y genera en archivo de salida """
	fileO = "./output/salida_"+str(chat_id)+".txt"
	fileOutput = open(fileO,"w")
	i = 0
	archInfoSalida = ""
	while(i < len(contenido)):
		if (contenido[i:i+1] == '\n'):
			archInfoSalida = archInfoSalida + '\n'
			# suprimimos los (None)
			archInfoSalida = archInfoSalida.replace("(None)","")
			# grabamos la salida linea a linea
			fileOutput.write(archInfoSalida)
			archInfoSalida = ""
		elif (contenido[i:i+1] == " "):
			archInfoSalida = archInfoSalida + " "
		elif (contenido[i:i+1] in ["0","1","2","3","4","5","6","7","8","9"]):
			archInfoSalida = archInfoSalida + contenido[i:i+1]	
		else: 	
			pinyin = getPinyin(contenido[i:i+1])
			#print("caractere: "+contenido[i:i+1])
			salidaReg = str(contenido[i:i+1]).rstrip('\n')+"("+str(pinyin).rstrip('\n')+")"
			archInfoSalida = archInfoSalida+salidaReg
		i += 1
	# grabamos salida en archivo de texto de salida
	#fileOutput.write(archInfoSalida)
	fileOutput.close()
	bot.sendDocument(chat_id,document=open(fileO))

def fileType(archivo):
	comando = "file "+archivo
	tipoArchivo = subprocess.check_output(comando,shell=True)
	tipoArch = str(tipoArchivo.lower())
	if (tipoArch.find("pdf") > -1):
		# es tipo texto
		return "pdf"
	elif(tipoArch.find("word") > -1):
		return "word"
	elif(tipoArch.find("text") > -1):
		return "text"
	return "desconocido"

######################## MAIN #######################

tokenFile = open("./token.key","r")
token = tokenFile.readline().rstrip('\n')
tokenFile.close()
bot = telepot.Bot(token)
bot.getMe()
bot.message_loop(handle)
chat_bot_init = '750975992'
#MessageLoop(bot,handle).run_as_thread()
try:
	while(1):
		#continue
		time.sleep(60);
except KeyboardInterrupt:
	print("Chatbot interrumpido por teclado")
	bot.sendMessage(chat_bot_init,"Se interrumpio Chatbot por teclado.")
except:
	bot.sendMessage(chat_bot_init,"Se interrumpio Chatbot abruptamente.")
