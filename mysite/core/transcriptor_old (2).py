import os, pickle
import pandas as pd
import speech_recognition as sr
from pydub import AudioSegment
from tinytag import TinyTag
from shutil import copyfile
from datetime import datetime

#os.system('ffmpeg -i llamado_3.wav -map_channel 0.0.0 llamado_3a.wav -map_channel 0.0.1 llamado_3b.wav')

start = []
temp_start = []
end = []
start_diag = []
end_diag = []
llamados = []
#canales = []

#data = pd.DataFrame(columns=('inicio', 'fin', 'canal', 'dialogo'))


#Obtenemos todos los llamados en ese directorio raíz o en el repositorio que toque



#Procedemos a procesar cada llamado

class Transcriptor(object):
    def parse(self, llamado):
        llamado = str(llamado)[11:]
        os.chdir("M:/FreeLance/Biometria/static/media/audios/tmp")
        data = pd.DataFrame(columns=('inicio', 'fin', 'canal', 'dialogo'))
        canales = []
        os.makedirs(llamado[:-4])
        copyfile(llamado, llamado[:-4]+"/"+llamado)
        os.chdir(llamado[:-4])
        #Split stereo to mono
        W = llamado.split('.')
        canal1 = W[0] +'a.wav'
        canales.append(canal1)
        canal2 = W[0] +'b.wav'
        canales.append(canal2)
        channels = ['operador', 'cliente']
        pos = 0
    
    
        cmd_split = ('ffmpeg -i ' + llamado + ' -map_channel 0.0.0 ' 
        + canal1 +' -map_channel 0.0.1 '+ canal2)
    
        os.system(cmd_split)
    
        #Procesamos cada uno de los canales donde operario = canal1 y cliente = canal2
    
        for canal in canales:
            Wch = canal.split('.')
            canal_texto = Wch[0]+'.txt'
    
            #limpiamos las listas de silencios y dialogos
            del start[:]
            del temp_start[:]
            del end[:]
            del start_diag[:]
            del end_diag[:]
    
            cmd_silence = ('ffmpeg.exe -i ' + canal + ' -af silencedetect=n=-14dB:d=2.5 -f null - '
            + '2> '+canal_texto)
            
            os.system(cmd_silence)
    
            with open(canal_texto) as f:
                f = f.readlines()
    
            #Duración de la pista
            tag = TinyTag.get(canal)
            p = tag.duration
    
    
            #obtenemos todos los fines de silencio
            for line in f:
                if line.find("silence_end:") != -1:
                    end.append(float(line[line.find("silence_end:")+13:line.find("|")-1]))
    
            #obtenemos todos los principios de silencio
            for line in f:
                if line.find("silence_start:") != -1:
                    temp_start.append(line[line.find("silence_start:")+15:line.find("|")-1])
    
            #casting a flot de lista inicio silencios
            for s in temp_start:
                if s == '':
                    s = 0
                    start.append(float(s))
                else:
                    start.append(float(s))
    
    
            #Obtenemos los bloques de diálogo
            #Validando que el bloque tenga algun silencio
            if len(start) > 0:
                for x in range(0, len(start)):
                    if x == 0:
                        if start[x] > 0:
                            start_diag.append(0)
                            end_diag.append(start[0])
                        else:
                            pass
                    else:
                        start_diag.append(end[x-1])
                        end_diag.append(start[x])
                
                if end[-1] < p:
                    start_diag.append(end[-1])
                    end_diag.append(p)
            else:
                start_diag.append(0)
                end_diag.append(p)
    
            #Validamos que los bloques de dialogo sean de duración mayor a 0.1 seg
            #de lo contrario son considerados silencios o ruidos eventuales
            a = 0 
    
            for z in range(0, len(start_diag)):
                if (end_diag[z-a] - start_diag[z-a]) < 0.01:
                    start_diag.pop(z-a)
                    end_diag.pop(z-a)
                    a = a + 1
    
                    
            #
            #Nos quedan 2 listas start_seg y end_seg X cantidad de elementos ambas
            #Los bloques de dialogo los extramos con la siguiente formula
            #bloque[i] = [start_diag[i] * end_diag[i] * 1000]
            #En pseudocigo desde el principio del dialogo X hasta el fin del dialogo X
            #
    
    
            for i in range(0, len(start_diag)):
                if (i == 0) and (start_diag[i] == 0):
                    t1 = start_diag[i] * 1000
                    t2 = (end_diag[i] + 0.8) * 1000
                    newAudio = AudioSegment.from_wav(canal)
                    newAudio = newAudio[t1:t2]
                    w = canal.split('.')
                    newfile = w[0]+'_'+str(i)+'.'+w[1]
                    newAudio.export(newfile, format="wav")
    
                    r = sr.Recognizer()
    
                    with sr.AudioFile(newfile) as source:
                        audio = r.record(source)
                    try:
                        s = r.recognize_google(audio, language='es-ar')
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
                    except:
                        s = '******'
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
                    
                elif (i == 0) and (start_diag[i] != 0):
                    t1 = (start_diag[i] - 0.8) * 1000
                    t2 = (end_diag[i] + 0.8) * 1000
                    newAudio = AudioSegment.from_wav(canal)
                    newAudio = newAudio[t1:t2]
                    w = canal.split('.')
                    newfile = w[0]+'_'+str(i)+'.'+w[1]
                    newAudio.export(newfile, format="wav")
    
                    r = sr.Recognizer()
    
                    with sr.AudioFile(newfile) as source:
                        audio = r.record(source)
                    try:
                        s = r.recognize_google(audio, language='es-ar')
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
                    except:
                        s = '******'
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
    
                elif (i == len(start_diag)) and (end_diag[i] == p):
                    t1 = (start_diag[i] - 0.8) * 1000
                    t2 = end_diag[i] * 1000
                    newAudio = AudioSegment.from_wav(canal)
                    newAudio = newAudio[t1:t2]
                    w = canal.split('.')
                    newfile = w[0]+'_'+str(i)+'.'+w[1]
                    newAudio.export(newfile, format="wav")
    
                    r = sr.Recognizer()
    
                    with sr.AudioFile(newfile) as source:
                        audio = r.record(source)
                    try:
                        s = r.recognize_google(audio, language='es-ar')
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
                    except:
                        s = '******'
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
    
                elif (i == len(start_diag)) and (end_diag[i] != p):
                    t1 = (start_diag[i] - 0.8) * 1000
                    t2 = (end_diag[i] + 0.8) * 1000       
                    newAudio = AudioSegment.from_wav(canal)
                    newAudio = newAudio[t1:t2]
                    w = canal.split('.')
                    newfile = w[0]+'_'+str(i)+'.'+w[1]
                    newAudio.export(newfile, format="wav")
    
                    r = sr.Recognizer()
    
                    with sr.AudioFile(newfile) as source:
                        audio = r.record(source)
                    try:
                        s = r.recognize_google(audio, language='es-ar')
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
                    except:
                        s = '******'
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
    
                else:
                    t1 = (start_diag[i] - 0.8) * 1000
                    t2 = (end_diag[i] + 0.8) * 1000       
                    newAudio = AudioSegment.from_wav(canal)
                    newAudio = newAudio[t1:t2]
                    w = canal.split('.')
                    newfile = w[0]+'_'+str(i)+'.'+w[1]
                    newAudio.export(newfile, format="wav")
    
                    r = sr.Recognizer()
    
                    with sr.AudioFile(newfile) as source:
                        audio = r.record(source)
                    try:
                        s = r.recognize_google(audio, language='es-ar')
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
                    except:
                        s = '******'
                        data.loc[len(data)]=[t1, t2, channels[pos], s]
            #Avance al siguiente canal
            pos = pos + 1
        
    	
    	#limpia los audios temporales
        files = os.listdir()
        
        for file in files:
            os.remove(file)
        os.chdir("..")
        os.removedirs(llamado[:-4])
    
    
        trans = ""
        canal1 = ""
        canal2 = ""
        for index, row in data.sort_values(by=['inicio'], ascending=True).iterrows():
            trans = trans + datetime.fromtimestamp(int(row['inicio']/1000)).strftime("%M:%S") + "|" + row['canal'] + "|" + row['dialogo'] + "||"
            if row['canal'] == 'operador':
                canal1 = canal1 + row['dialogo'] + "|"
            else:
                canal2 = canal2 + row['dialogo'] + "|" 
        return canal1,canal2,trans


files = os.listdir()

for file in files:
    if file.find('.wav') != -1:
        llamados.append(file)
        c1, c2, trans = parse(file)
        print (c1)
        print (c2)
        print (trans)