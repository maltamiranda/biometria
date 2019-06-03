import speech_recognition as sr
import wavio, random
import pdb
from tinytag import TinyTag
from pydub import AudioSegment
from os import remove



class Transcriptor(object):

    def parse(self, archivo):

        canal1 = []
        canal2 = []
        files = []
        count = 0

        file_name = str(archivo)
        w = file_name.split('.')
        nombre = w[0]
        extension = w[1]
        nombre = 'static/media/'+nombre

        File = wavio.read(archivo)
        rate = File.rate

        chn = File.data.shape[1]
        print (rate)

        #pdb.set_trace()

        if chn == 1:
            channel_1 = File.data[:,0]
            files.append(nombre+'_1.'+extension)
            wavio.write(nombre+'_1.'+extension, channel_1, rate )
        if chn == 2:
            channel_1 = File.data[:,0]
            channel_2 = File.data[:,1]
            files.append(nombre+'_1.'+extension)
            files.append(nombre+'_2.'+extension)
            wavio.write(nombre+'_1.'+extension, channel_1, rate )
            wavio.write(nombre+'_2.'+extension, channel_2, rate )

        for file in files:

            tag = TinyTag.get(file)
            p = tag.duration / 30
            p_int = int(p)
            p_dec = abs(p) - abs(int(p))
            

            skip = 0
            segmentos = []
            terminos = []

            if p_int > 0:
                t2 = 0
                while skip < p_int:
                    t1 = t2
                    t2 = (30 + t1)
                    skip = skip + 1
                    newAudio = AudioSegment.from_wav(file)
                    newAudio = newAudio[t1*1000:t2*1000]
                    newfile = ('llamado_provincia_'+str(skip)+
                        '_'+str(t1)+'s_'+str(t2)+'s.wav')
                    newAudio.export(newfile, format="wav")
                    segmentos.append(newfile)
                if p_dec > 0:
                    t1 = t2
                    t2 = p_dec*30 + t1
                    skip = skip + 1
                    newAudio = AudioSegment.from_wav(nombre+'.'+extension)
                    newAudio = newAudio[t1*1000:t2*1000]
                    newfile = ('llamado_provincia_'+str(skip)+
                        '_'+str(t1)+'s_'+str(t2)+'s.wav')
                    newAudio.export(newfile, format="wav")
                    segmentos.append(newfile)
            else:
                t1 = 0
                t2 = p_dec*30 + t1
                skip = skip + 1
                newAudio = AudioSegment.from_wav(nombre+'.'+extension)
                newAudio = newAudio[t1*1000:t2*1000]
                newfile = ('llamado_provincia_'+str(skip)+'_'+
                    str(t1)+'s_'+str(t2)+'s.wav')
                newAudio.export(newfile, format="wav")
                segmentos.append(newfile)

            for segmento in segmentos:
                r = sr.Recognizer()

                with sr.AudioFile(segmento) as source:
                    audio = r.record(source)
                try:
                    s = r.recognize_google(audio, language='es-ar')
                except:
                    terminos.append('********')
                else:
                    terminos.append(s)

                #Se limpia el registro
                remove(segmento)
            if count == 0:
                canal1 = terminos
            if count == 1:
                canal2 = terminos

            count = count + 1

            remove(file)

        print('mark')

        return (canal1, canal2)