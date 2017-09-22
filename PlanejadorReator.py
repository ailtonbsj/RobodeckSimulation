# -*- coding: utf-8 -*-
from robodeck_pkg.robodeckSIM import *
from geometria import *
import  time
from PIL import *
from matplotlib.pyplot import *

class CONST():
    WIDTH_STOP = 35
    WIDTH_DESVIO = 20
    FINDED_OBJ = 10

class Reator():
    """ Modulo responsavel pelo acionamento direto do robodeck,
    Envia informações dos sensores e espera comandos do modulo
    planejador. Tambem atua de forma reativa se necessario """
    
    #Atributos
    robo = None
    anguloInicial = 0
    odometro = 0
    PASSO = 0.5
    
    #Método Construtor
    def __init__(self):
        """Construtor"""
        self.robo = Robodeck()
        self.robo.start()
        self.anguloInicial = 90 - self.robo.lerBussola()
        self.robo.zerarOdometro()
        
    def getAngulo(self):
        """ Retorna o angulo atual com relacao ao sistema de coordenadas """
        ang = floatToDegree(self.robo.lerBussola()+self.anguloInicial)
        self.angulo = ang
        return ang
    
    def giraToAngulo(self, valor, callbackUltra=None):
        """ Gira robo para angulo informado percorrendo o menor grau """
        orig = self.getAngulo() #captura angulo atual
        dest = floatToDegree(valor) #transforma valor em graus
        difabs = abs(dest-orig) #subtrai angulo em origem pelo angulo de destino
        difsign = sign(dest-orig)
        if difabs < 180:
            if difsign == -1:
                self.robo.girar(Robodeck.HORARIO,Robodeck.PADRAO)
            else:
                self.robo.girar(Robodeck.ANTIHORARIO,Robodeck.PADRAO)
        else:
            if difsign == -1:
                self.robo.girar(Robodeck.ANTIHORARIO,Robodeck.PADRAO)
            else:
                self.robo.girar(Robodeck.HORARIO,Robodeck.PADRAO)
        #encontra faixa dos angulos robo pode parar
        menorAng = floatToDegree(dest-self.PASSO)
        maiorAng = floatToDegree(dest+self.PASSO)
        angAtual = self.getAngulo()
        #linhas abaixo verifica se angulo atual está entre a faixa de destino
        compa = 0
        if menorAng > maiorAng:
            compa = (360-menorAng)
        else:
            compa = -menorAng
        menorAng = floatToDegree(menorAng + compa)
        maiorAng = floatToDegree(maiorAng + compa)
        dest = floatToDegree(dest + compa)
        while not (menorAng < floatToDegree(angAtual + compa) < maiorAng): #enquanto nao estiver no range espere!
            angAtual = self.getAngulo()
            if callbackUltra == None:
                time.sleep(0.001)
            else:
                callbackUltra()
        self.robo.girar(Robodeck.PARAR,None)
        return True

    def giraPlusAngulo(self,valor):
        """ Gira robo para angulo informado com relação ao angulo Atual """
        ang = self.getAngulo()
        return self.giraToAngulo(floatToDegree(ang+valor))
    
    def getOdomentro(self):
        """ Retorna a media dos odometros do Robodeck """
        odomen = (self.robo.lerOdometroD()+self.robo.lerOdometroE())/2
        self.odometro = odomen
        return odomen
    
    def andarDistancia(self, valor,callbackUltra = None):
        """ Faz o robo se movimentar para frente a partir do valor da
        distancia informada. Tambem atua de forma reativa parando ao
        encontrar um obstaculo"""
        self.robo.zerarOdometro()
        COL = 40
        sf = self.robo.lerUltrasomDianteiro()
        #st = self.robo.LerUltrasomTraseiro()
        #se = self.robo.LerUltrasomEsquerdo()
        #sd = self.robo.LerUltrasomDireito()
        if (sf < COL and sf != 0): # or (st < COL and st != 0) or (se < COL and se != 0) or (sd < COL and sd != 0):
            self.robo.andar(Robodeck.PARAR)                
            return False        
        self.robo.andar(Robodeck.ANDAR)
        od = 0
        while od  < valor:
            od = self.getOdomentro()
            # Inicio - codigo para acao reativa
            sf = self.robo.lerUltrasomDianteiro()
            #st = self.robo.LerUltrasomTraseiro()
            #se = self.robo.LerUltrasomEsquerdo()
            #sd = self.robo.LerUltrasomDireito()
            if (sf < COL and sf != 0): # or (st < COL and st != 0) or (se < COL and se != 0) or (sd < COL and sd != 0):
                #print str(sf) + "," + str(st) + "," + str(se) + "," + str(sd)               
                self.robo.andar(Robodeck.PARAR)                
                return False
            if callbackUltra != None:
                vl = callbackUltra(od)
                if vl == CONST.FINDED_OBJ:
                    self.robo.andar(0)
                    return CONST.FINDED_OBJ
            #fim - codigo para acao reativa
            time.sleep(0.001)
        self.robo.andar(0)
        return True #retorna True caso nao encontre objeto
    
class Planejador():
    
    #Atributos
    reator = None
    mapa  = None
    odBuf = 0
    oXm = 350
    oYm = 200
    wm = 1000
    hm = 750
    mapx = []
    mapy = []
    xRobo = -180
    yRobo = -80
    direitaIni = 0
    direitaEnd = 0
    esquerdaIni = 0
    esquerdaEnd = 0
    ativadorEsq = False
    ativadorDir = False
    PARADO = 0
    ANDANDO = 1
    GIRANDO = 2
    acao = PARADO
    desvios = []
    xObjPri = 470
    yObjPri = 370
    xObjSec = xObjPri
    yObjSec = yObjPri
    #Metodo Construtor
    def __init__(self):
        self.reator = Reator()
        self.mapa = Image.new("L",(self.wm,self.hm))
        gray()
        time.sleep(3)
        while True:
            sf,st,se,sd = self.scanUltras()
            if sf:
                pass
            elif se:
                self.girarPlusAngulo(90)
            elif sd:
                self.girarPlusAngulo(-90)
            else:
                self.girarPlusAngulo(180)
                coords = self.desvios.pop()
                self.xObjSec = coords[0][0]
                self.yObjSec = coords[0][1]
            if self.andar(1000) == CONST.FINDED_OBJ:
                if (self.xObjSec == self.xObjPri) and (self.yObjSec == self.yObjPri):
                    print "Objetivo Completado!"
                    imshow(self.mapa,interpolation='bilinear')
                    show()
                    break
                else:
                    self.xObjSec = self.xObjPri
                    self.yObjSec = self.yObjPri
                self.girarToAngulo(coords[1])

    def atualizaPosicaoCallback(self,od):
        odom = od - self.odBuf
        self.odBuf = od
        if odom > 0:
            self.xRobo,self.yRobo = polToRec((self.reator.getAngulo(),odom),(self.xRobo,self.yRobo))
            if (self.xObjPri == self.xObjSec) and (self.yObjPri == self.yObjSec):
                larg = CONST.WIDTH_STOP
            else:
                larg = CONST.WIDTH_DESVIO
            if (recToPol((self.xObjSec,self.yObjSec),(self.xRobo,self.yRobo))[0]) < larg:
                return CONST.FINDED_OBJ
            self.scan()
    
    def andar(self,dist):
        self.acao = Planejador.ANDANDO
        vl = self.reator.andarDistancia(dist,self.atualizaPosicaoCallback)
        self.acao = Planejador.PARADO
        if vl == CONST.FINDED_OBJ:
            return vl
        return True
         
    def girarToAngulo(self,valor):
        self.acao = Planejador.GIRANDO
        self.reator.giraToAngulo(valor,self.scan)
        self.direitaIni = 0
        self.direitaEnd = 0
        self.esquerdaIni = 0
        self.esquerdaEnd = 0
        self.ativadorDir = False
        self.ativadorEsq = False
        self.acao = Planejador.PARADO
    
    def girarPlusAngulo(self,vl):
        orig = self.reator.getAngulo()
        dest = floatToDegree(orig + vl)
        self.girarToAngulo(dest)

    def putPx(self,X,Y):
        #print "("+str(X)+","+str(Y)+")"
        self.mapa.putpixel((X,Y),255)
        self.mapa.putpixel((X-1,Y),255)
        self.mapa.putpixel((X+1,Y),255)
        self.mapa.putpixel((X,Y-1),255)
        self.mapa.putpixel((X,Y+1),255)
        self.mapa.putpixel((X-1,Y-1),255)
        self.mapa.putpixel((X+1,Y+1),255)
        self.mapa.putpixel((X-1,Y+1),255)
        self.mapa.putpixel((X+1,Y-1),255)
    
    def geraImage(self):
        DISTAN = 60
        us = self.reator.robo.lerUltrasomDianteiro()
        if us < DISTAN and us != 0:
            theta = self.reator.getAngulo()
            X,Y = polToRec((theta,us+30),(self.xRobo,self.yRobo))
            self.putPx(int(X+self.oXm),int(Y+self.oYm))            
        us = self.reator.robo.lerUltrasomTraseiro()
        if us < DISTAN and us != 0:
            theta = self.reator.getAngulo()+180
            X,Y = polToRec((theta,us+30),(self.xRobo,self.yRobo))
            self.putPx(int(X+self.oXm),int(Y+self.oYm))
        us = self.reator.robo.lerUltrasomEsquerdo()
        if us < DISTAN and us != 0:
            theta = self.reator.getAngulo()+90
            X,Y = polToRec((theta,us+30),(self.xRobo,self.yRobo))
            self.putPx(int(X+self.oXm),int(Y+self.oYm))
        us = self.reator.robo.lerUltrasomDireito()
        if us < DISTAN and us != 0:
            theta = self.reator.getAngulo()-90
            X,Y = polToRec((theta,us+30),(self.xRobo,self.yRobo))
            self.putPx(int(X+self.oXm),int(Y+self.oYm))       

    def scanUltras(self):
        usf = self.reator.robo.lerUltrasomDianteiro()
        ust = self.reator.robo.lerUltrasomTraseiro()
        use = self.reator.robo.lerUltrasomEsquerdo()
        usd = self.reator.robo.lerUltrasomDireito()
        DIST = 80
        sf=True
        st=True
        se=True
        sd=True        
        if (usf < DIST) and (usf != 0):
            sf = False
        else:
            sf = True
            
        if (ust < DIST) and (ust != 0):
            st = False
        else:
            st = True
            
        if (use < DIST)  and (use != 0):
            se = False
        else:
            se = True

        if (usd < DIST)  and (usd != 0):
            sd = False
        else:
            sd = True
        return (sf,st,se,sd)
            
    def scan(self):
        sf,st,se,sd = self.scanUltras()        
        if self.acao == Planejador.ANDANDO:
            if se:
                if (self.esquerdaIni == 0) and self.ativadorEsq:
                    self.esquerdaIni = (self.xRobo,self.yRobo)
                else:
                    self.esquerdaEnd = (self.xRobo,self.yRobo)
            else:
                if not self.ativadorEsq:
                    self.ativadorEsq = True
                if (self.esquerdaIni != 0) and (self.esquerdaEnd != 0):
                    xx = self.esquerdaEnd[0] - self.esquerdaIni[0]
                    yy = self.esquerdaEnd[1] - self.esquerdaIni[1]
                    xx = self.esquerdaIni[0]+(xx/2)
                    yy = self.esquerdaIni[1]+(yy/2)
                    pt = ((xx,yy),floatToDegree(self.reator.getAngulo()+90))
                    self.desvios.append(pt)
                    print str(pt)                    
                    self.esquerdaIni = 0
                    self.esquerdaEnd = 0
                    
            if sd:
                if (self.direitaIni == 0) and self.ativadorDir:
                    self.direitaIni = (self.xRobo,self.yRobo)
                else:
                    self.direitaEnd = (self.xRobo,self.yRobo)
            else:
                if not self.ativadorDir:
                    self.ativadorDir = True
                if (self.direitaIni != 0) and (self.direitaEnd != 0):
                    xx = self.direitaEnd[0] - self.direitaIni[0]
                    yy = self.direitaEnd[1] - self.direitaIni[1]
                    xx = self.direitaIni[0]+(xx/2)
                    yy = self.direitaIni[1]+(yy/2)
                    pt = ((xx,yy),floatToDegree(self.reator.getAngulo()-90))
                    self.desvios.append(pt)
                    print str(pt)                    
                    self.direitaIni = 0
                    self.direitaEnd = 0
        self.geraImage()    

pl = Planejador()

#pl.andar(800)
#pl.girarToAngulo(0)
#
#pl.andar(800)
#pl.girarToAngulo(180)
#
#pl.andar(800)
#pl.girarToAngulo(270)
#
#pl.andar(180)
#pl.girarToAngulo(0)
#
#pl.andar(300) 
#pl.girarToAngulo(270)
#
#pl.andar(300)
#pl.girarToAngulo(0)
#
#pl.andar(600)
#pl.girarToAngulo(90)
#
#pl.andar(800)
#pl.girarToAngulo(180)
#
#pl.andar(800)
#pl.girarToAngulo(90)
#
#pl.andar(800)
#pl.girarToAngulo(0)
#
#pl.andar(800)
#pl.girarToAngulo(270)
#
#pl.andar(200)
#pl.girarToAngulo(0)
#
#pl.andar(200)
#pl.girarToAngulo(90)
#
#pl.andar(200)
#
#imshow(pl.mapa,interpolation='bilinear')