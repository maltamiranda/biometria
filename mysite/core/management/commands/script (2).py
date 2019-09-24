import os
import pandas as pd
import speech_recognition as sr
from pydub import AudioSegment
from tinytag import TinyTag
from datetime import datetime


start = []
temp_start = []
end = []
start_diag = []
end_diag = []
start_bloque = []
temp_start_bloque = []
end_bloque = []
start_diag_bloque = []
end_diag_bloque = []
llamados = []
canales = []
segmentos = []


llamados.append('190810094414631_IVR_04001.wav')

#Preparado del dataFrame
data = pd.DataFrame(columns=('inicio', 'fin', 'canal', 'dialogo'))

#Procedemos a procesar cada llamado

for llamado in llamados:
    #Split stereo to mono
    W = llamado.split('.')
    canal1 = W[0] +'a.wav'
    canales.append(canal1)
    canal2 = W[0] +'b.wav'
    canales.append(canal2)
    channels = ['operador', 'cliente']
    pos = 0

    #Descomprimimos el audio de g729 a pcm_s16le
    cmd_unpack = ('ffmpeg  -acodec g729 -i '+llamado+' -acodec '+
    'pcm_s16le -f wav '+llamado)

    os.system(cmd_unpack)

    #Separamos audio canal A y B (operador / cliente)
    cmd_split = ('ffmpeg -i ' + llamado + ' -map_channel 0.0.0 ' 
    + canal1 +' -map_channel 0.0.1 '+ canal2)

    os.system(cmd_split)

    #Procesamos cada uno de los canales donde operario = canalA y cliente = canalB

    for canal in canales:
        Wch = canal.split('.')
        canal_texto = Wch[0]+'.txt'
        volumen_texto = Wch[0]+'_volumen.txt'

        #limpiamos las listas de silencios y dialogos
        del start[:]
        del temp_start[:]
        del end[:]
        del start_diag[:]
        del end_diag[:]


        #Determinamos el volumen o potencia promedio de cada canal
        cmd_volumen = ('ffmpeg -t 10 -i '+ canal +' -af "volumedetect" -f null '
        +'/dev/null 2> '+volumen_texto)

        os.system(cmd_volumen)

        #Obtenemos el nivel promedio de potencia
        with open(volumen_texto) as v:
            v = v.readlines()

        for vol in v:
            if vol.find("mean_volume:") != -1:
                nivel = float(vol[vol.find('mean_volume:')+13:vol.find('dB')-1])
                nivel = abs(nivel) - 10

        #Determinamos los intervalos de silencios de acuerdo a la potencia de cada canal
        cmd_silence = ('ffmpeg.exe -i ' + canal + ' -af silencedetect=n=-'+str(nivel)+'dB:d=2.5 -f null - '
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
    
            #Control Lapsos Corte
            if (i == 0) and (start_diag[i] == 0):
                t1 = start_diag[i] * 1000
                t2 = (end_diag[i] + 0.8) * 1000
            elif (i == 0) and (start_diag[i] != 0):
                t1 = (start_diag[i] - 0.8) * 1000
                t2 = (end_diag[i] + 0.8) * 1000
            elif (i == len(start_diag)) and (end_diag[i] == p):
                t1 = (start_diag[i] - 0.8) * 1000
                t2 = end_diag[i] * 1000
            elif (i == len(start_diag)) and (end_diag[i] != p):
                t1 = (start_diag[i] - 0.8) * 1000
                t2 = (end_diag[i] + 0.8) * 1000
            else:
                t1 = (start_diag[i] - 0.8) * 1000
                t2 = (end_diag[i] + 0.8) * 1000
            #Control Lapsos Corte


            lapso = (t2 - t1)/1000
            parte = 1
            #Validamos si el bloque es mayor a 10 segundos para un segundo filtrado de silencios 
            if (lapso) > 10:

                #limpiamos las listas de silencios y dialogos por bloque
                del start_bloque[:]
                del temp_start_bloque[:]
                del end_bloque[:]
                del start_diag_bloque[:]
                del end_diag_bloque[:]

                newAudio = AudioSegment.from_wav(canal)
                newAudio = newAudio[t1:t2]
                w = canal.split('.')
                newfile = w[0]+'_'+str(i)+'.'+w[1]
                newAudio.export(newfile, format="wav")

                Sgmt = newfile.split('.')
                Sgmt_texto = Sgmt[0]+'.txt'
                Sgmt_volumen = Sgmt[0]+'_volumen.txt'
                
                cmd_volumen = ('ffmpeg -t 10 -i '+ newfile +' -af "volumedetect" -f null '
                +'/dev/null 2> '+Sgmt_volumen)

                os.system(cmd_volumen)

                #Obtenemos el nivel promedio de potencia en ese bloque
                with open(Sgmt_volumen) as v_sgmt:
                    v_sgmt = v_sgmt.readlines()

                for vol_sgmt in v_sgmt:
                    if vol_sgmt.find("mean_volume:") != -1:
                        nivel_sgmt = float(vol_sgmt[vol_sgmt.find('mean_volume:')+13:vol_sgmt.find('dB')-1])
                        nivel_sgmt = abs(nivel_sgmt) - 10

                #Determinamos los intervalos de silencios de acuerdo a la potencia de cada canal
                cmd_silence = ('ffmpeg.exe -i ' + newfile + ' -af silencedetect=n=-'+str(nivel_sgmt)+'dB:d=0.8 -f null - '
                + '2> '+Sgmt_texto)

                os.system(cmd_silence)

                with open(Sgmt_texto) as sgmt_f:
                    sgmt_f = sgmt_f.readlines()


                #Duración del bloque de dialogo
                tag = TinyTag.get(newfile)
                p = tag.duration

                #obtenemos todos los fines de silencio por bloque
                for line in sgmt_f:
                    if line.find("silence_end:") != -1:
                        end_bloque.append(float(line[line.find("silence_end:")+13:line.find("|")-1]))

                #obtenemos todos los principios de silencio por bloque
                for line in sgmt_f:
                    if line.find("silence_start:") != -1:
                        temp_start_bloque.append(line[line.find("silence_start:")+15:line.find("|")-1])

                #casting a flot de lista inicio silencios por bloque
                for s in temp_start_bloque:
                    if s == '':
                        s = 0
                        start_bloque.append(float(s))
                    else:
                        start_bloque.append(float(s))


                #Obtenemos los bloques de diálogo
                #Validando que el bloque tenga algun silencio
                if len(start_bloque) > 0:

                    for x in range(0, len(start_bloque)):
                        if x == 0:
                            if start_bloque[x] > 0:
                                start_diag_bloque.append(0)
                                end_diag_bloque.append(start[0])
                            else:
                                pass
                        else:
                            start_diag_bloque.append(end_bloque[x-1])
                            end_diag_bloque.append(start_bloque[x])

                    if end_bloque[-1] < p:
                        start_diag_bloque.append(end_bloque[-1])
                        end_diag_bloque.append(p)
                else:
                    start_diag_bloque.append(0)
                    end_diag_bloque.append(p)


                #Validamos que los bloques de dialogo sean de duración mayor a 0.1 seg
                #de lo contrario son considerados silencios o ruidos eventuales
                a = 0 

                for z in range(0, len(start_diag_bloque)):
                    if (end_diag_bloque[z-a] - start_diag_bloque[z-a]) < 0.01:
                        start_diag_bloque.pop(z-a)
                        end_diag_bloque.pop(z-a)
                        a = a + 1

                for block in range(0, len(start_diag_bloque)):
                    t1 = (start_diag_bloque[block] -0.3) * 1000
                    t2 = (end_diag_bloque[block] + 0.3) * 1000

                    myAudio = AudioSegment.from_wav(newfile)
                    myAudio = myAudio[t1:t2]
                    w_sgmt = newfile.split('.')
                    bloque = w_sgmt[0]+'_'+str(block)+'.'+w_sgmt[1]
                    myAudio.export(bloque, format='wav')

                    r = sr.Recognizer()

                    with sr.AudioFile(bloque) as source:
                        audio = r.record(source)
                    try:
                        s = r.recognize_google(audio, language='es-ar')
                        segmentos.append(s)
                    except:
                        s = ''
                        segmentos.append(s)
                

                #concatenar y guardar el dialogo del bloque
                s = ' '.join(segmentos)
                data.loc[len(data)]=[t1, t2, channels[pos], s]




            else:

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
                    s = ''
                    data.loc[len(data)]=[t1, t2, channels[pos], s]
        
        #Avance al siguiente canal
        pos = pos + 1

    print('............')
    print('\n')
    print('............')
    print('\n')
    print('Registro de ' + llamado)
    print('\n')
    trans = ""
    canal1 = ""
    canal2 = ""
    for index, row in data.sort_values(by=['inicio'], ascending=True).iterrows():
        trans = trans + datetime.fromtimestamp(int(row['inicio']/1000)).strftime("%M:%S") + "|" + row['canal'] + "|" + row['dialogo'] + "||"
        if row['canal'] == 'operador':
            canal1 = canal1 + row['dialogo'] + "|"
        else:
            canal2 = canal2 + row['dialogo'] + "|"
    #print(data['dialogo'].sort_values(by=['inicio'], ascending=True))