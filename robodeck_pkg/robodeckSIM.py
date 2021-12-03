# -*- coding: utf-8 -*-
#********************************************************************
# Classe de Simulação RoboDeck 
#********************************************************************
 
import time
from threading import Thread
import pygame, math
from pygame.transform import *
from numpy import *
import pickle

class Robodeck(Thread):
    HORARIO = -1
    ANTIHORARIO = 1
    PARAR = 0
    ANDAR = 1
    PADRAO = 1    
    
    sensorEncoderED = .0 #simulador
    sensorUltraSomF = 0 #simulador
    sensorUltraSomE = 0 #simulador
    sensorUltraSomT = 0 #simulador
    sensorUltraSomD = 0 #simulador
    angulo = 90.0
    norte = 0 #simulador
    stepMoving = 0.1 #simulador
    stepTurn = 0.1 #simulador
    tela = 0 #simulador
    robo = 0 #simulador
    rosa = 0#simulador
    fonte = 0 #simulador
    imgFont = 0 #simulador
    X = .0 #simulador
    Y = .0 #simulador
    isLineShow = True #simulador
    isMoving = False #simulador
    isColision = False
    isTurn = 0 #simulador
    obstaculos = []
    plotar = []
    objetivo = (0,0)
    isRunningSimulation = True

    def __init__(self):
        f = open('robodeck_pkg/robodeckSIM.ini','r')
        for i in f:
            pos = i.find('=')
            k = i[:pos]
            v = i[pos+1:]
            if k == 'NORTE':
                self.norte = float(v)
            elif k == 'STEPMOVE':
                self.stepMoving = float(v)
            elif k == 'STEPTURN':
                self.stepTurn = float(v)
            elif k == 'POSEINICIALNORTE':
                self.angulo = float(v)
            elif k == 'OBJETIVO':
                busca = v.find(',')
                a = int(v[:busca])
                b = int(v[busca+1:])
                self.objetivo = (a,b)
            elif k == 'SHOWLINEULTRASOM':
                busca = v.find(',')
                a = int(v)
                if a == 0:
                    self.isLineShow = False
            elif k == 'POSEROBO':
                busca = v.find(',')
                a = int(v[:busca])
                b = int(v[busca+1:])
                self.X = a
                self.Y = b
            elif k == 'HURDLEH':
                busca = v.find(',')
                a = int(v[:busca])
                b = int(v[busca+1:])
                self.obstaculos.append(((a,b),(a+20,b)))
            elif k == 'HURDLEV':
                busca = v.find(',')
                a = int(v[:busca])
                b = int(v[busca+1:])
                self.obstaculos.append(((a,b),(a,b+20)))
        f.close()
        Thread.__init__(self)

    #Simulação Completada
    def andar(self, velocidade):
        if (velocidade == 0):
            self.isMoving = False
            #print ("parado")
        else:
            self.isMoving = True
            #print ("andando")
        return True

    #Simulação Completada
    def girar(self, lado, velocidade):
        if lado == 1:
            #print ("girando para direita...")
            self.isTurn = 1
        elif lado == -1:
            #print ("girando para esquerda...")
            self.isTurn = -1
        else:
            #print ("parou de girar")
            self.isTurn = 0
        return True

    #Simulação Completada
    def lerOdometroD(self):
        return self.sensorEncoderED

    #Simulação Completada
    def lerOdometroE(self):
        return self.sensorEncoderED

    #Simulação Completada
    def zerarOdometro(self):
        self.sensorEncoderED = 0
        #print "zerado!", type(self.odometro)
        return True

    #Simulação Completada
    def lerUltrasomDianteiro(self):
        return self.sensorUltraSomF
    
    #Simulação Completada
    def lerUltrasomTraseiro(self):
        return self.sensorUltraSomT
    
    #Simulação Completada
    def lerUltrasomEsquerdo(self):
        return self.sensorUltraSomE

    #Simulação Completada
    def lerUltrasomDireito(self):
        return self.sensorUltraSomD

    #Simulação Completada
    def lerBussola(self):
        return self.angulo

    #Funcao exclusiva da simulacao NAO USAR OU ALTERAR
    def convertCoords(self,(x,y),(origemX,origemY)=(250,450)):
        x = origemX+x
        y = origemY-y
        return (float(x),float(y))
        
    #Funcao exclusiva da simulacao NAO USAR OU ALTERAR
    def convertCoordsInversa(self,(x,y),(origemX,origemY)=(0,450)):
        x = x-origemX
        y = y
        return (float(x),float(y))
        
    def convertCoordsNovo(self,(x,y)):
        x = x-250
        y = -(y-450)
        return (float(x),float(y))
    
    #Funcao exclusiva da simulacao NAO USAR OU ALTERAR
    def intToGraus(self,num):
        if num > 359.9:
            num = num - 360
        elif num < 0:
            num = 360 + num
        return num
    
    #Funcao exclusiva da simulacao NAO USAR OU ALTERAR
    def recToPol(self,(xf,yf),(xi,yi)=(0,0)):
        xf = float(xf)
        yf = float(yf)
        xi = float(xi)
        yi = float(yi)
        b = xf-xi
        c = yf-yi
        r = math.sqrt(b**2+c**2)
        teta = math.degrees(math.acos(b/r))
        if c < 0:
            teta = self.intToGraus(-teta)
        return (teta,r)
    
    #Funcao exclusiva da simulacao NAO USAR OU ALTERAR
    def polToRec(self,(teta,r),(xi,yi)=(0,0)):
        x = r*math.cos(math.radians(teta))+xi
        y = r*math.sin(math.radians(teta))+yi
        return (x,y)

    # Finaliza simulação
    def turnOff(self):
        self.isRunningSimulation = False

    # Executa Thread de simulação
    def run(self):
        WIDTHSCREEN = 800
        HEIGHTSCREEN = 600
        CENTER_X = int(WIDTHSCREEN/2)
        CENTER_Y = int(HEIGHTSCREEN/2)
        CENTER_CROSS_X = CENTER_X-150
        CENTER_CROSS_Y = CENTER_Y+150
        RED = (255,0,0)
        BLUE = (0,0,255)
        WHITE = (255,255,255)
        BLACK = (0,0,0)
        pygame.quit()
        pygame.init()
        self.tela = pygame.display.set_mode((WIDTHSCREEN,HEIGHTSCREEN))
        self.robo = pygame.image.load("robodeck_pkg/robo.png")
        self.rosa = pygame.image.load("robodeck_pkg/rosa.png")
        objetivo = pygame.image.load('robodeck_pkg/objetivo.png')
        self.rosa = rotate(self.rosa,self.norte)
        self.fonte = pygame.font.Font("robodeck_pkg/font.ttf",12)
        pygame.display.set_caption('Robodeck Simulation 0.2 by Jose Ailton B. da Silva')
        stepMov = self.stepMoving
        stepTur = self.stepTurn
        obstDesenho = []
        tipoObstaculo = 1
        pos1 = (0,0)
        pos2 = (0,0)
        for i in self.obstaculos:
            posi = self.convertCoords(i[0])
            posf = self.convertCoords(i[1])
            ob = (posi[0],posi[1]),(posf[0],posf[1])
            obstDesenho.append(ob)
        while self.isRunningSimulation:
            #area de atualizacao
            if self.isMoving: #anda
                if self.isColision:
                    cls = -1
                else:
                    cls = 1
                radAng = math.radians(self.angulo+self.norte)
                self.X = self.X + cls*(stepMov*math.cos(radAng))
                self.Y = self.Y + cls*(stepMov*math.sin(radAng))
                self.sensorEncoderED += stepMov
                #print passo
                
            if self.isTurn == 1: #gira
                self.angulo += stepTur
                self.sensorEncoderED += stepMov
                if self.angulo > 359.9:
                    self.angulo -= 360
                #print self.angulo
            elif self.isTurn == -1:
                self.angulo -= stepTur
                self.sensorEncoderED += stepMov
                if self.angulo < 0:
                    self.angulo = 360 + self.angulo
                #print self.angulo
                
            self.tela.fill(WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_1:
                        self.obstaculos = pickle.load(open('robodeck_pkg/scenes/1/salveX.txt', 'r'))
                        obstDesenho = pickle.load(open('robodeck_pkg/scenes/1/salveY.txt', 'r'))
                        print "Carregado"
                    elif event.key == pygame.K_2:
                        self.obstaculos = pickle.load(open('robodeck_pkg/scenes/2/salveX.txt', 'r'))
                        obstDesenho = pickle.load(open('robodeck_pkg/scenes/2/salveY.txt', 'r'))
                        print "Carregado"
                    elif event.key == pygame.K_3:
                        self.obstaculos = pickle.load(open('robodeck_pkg/scenes/3/salveX.txt', 'r'))
                        obstDesenho = pickle.load(open('robodeck_pkg/scenes/3/salveY.txt', 'r'))
                        print "Carregado"
                    elif event.key == pygame.K_4:
                        self.obstaculos = pickle.load(open('robodeck_pkg/scenes/4/salveX.txt', 'r'))
                        obstDesenho = pickle.load(open('robodeck_pkg/scenes/4/salveY.txt', 'r'))
                        print "Carregado"
                    elif event.key == pygame.K_s:
                        pickle.dump(self.obstaculos,open('robodeck_pkg/salveX.txt', 'w'))
                        pickle.dump(obstDesenho,open('robodeck_pkg/salveY.txt', 'w'))
                        print "Salvo"
                    elif event.key == pygame.K_l:
                        self.obstaculos = pickle.load(open('robodeck_pkg/salveX.txt', 'r'))
                        obstDesenho = pickle.load(open('robodeck_pkg/salveY.txt', 'r'))
                        print "Carregado"
                    elif event.key == pygame.K_q:
                        self.isRunningSimulation = False
                        print "Finishing..."
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if tipoObstaculo == 1:
                        pos1 = event.pos
                    elif tipoObstaculo == 2:
                        pos2 = event.pos
                        tipoObstaculo = 0
                        posIni = self.convertCoordsInversa(pos1)
                        posFim = self.convertCoordsInversa(pos2)                       
                        x = posFim[0]-posIni[0]
                        y = posFim[1]-posIni[1]                       
                        if abs(x) > abs(y):
                            passox = 20
                            passoy = 0
                            quant = abs(int(x/20))
                        else:
                            passox = 0
                            passoy = 20
                            quant = abs(int(y/20))
                        for i in range(0,quant+1):
                            if abs(x) > abs(y):
                                xa = posIni[0]+sign(x)*(i*20)
                                ya = posIni[1]+i*(y/quant)
                            else:
                                xa = posIni[0]+i*(x/quant)
                                ya = posIni[1]+sign(y)*i*20
                            posa = (xa,ya)
                            obstDesenho.append((posa,(posa[0]+sign(x)*passox,posa[1]+sign(y)*passoy)))
                            nv = self.convertCoordsNovo(posa)
                            self.obstaculos.append((nv,(nv[0]+sign(x)*passox,nv[1]+sign(y)*passoy)))
                    tipoObstaculo += 1

            bjtv = self.convertCoords(self.objetivo)
            frm = objetivo.get_rect()
            bjtv = (bjtv[0]-(frm[2]/2),bjtv[1]-(frm[3]/2))
            self.tela.blit(objetivo,bjtv,objetivo.get_rect())            
            
            self.tela.blit(self.rosa,(700,CENTER_CROSS_Y+10),self.rosa.get_rect())            
            
            pygame.draw.line(self.tela, BLACK, (CENTER_CROSS_X, 0), (CENTER_CROSS_X, HEIGHTSCREEN))
            pygame.draw.line(self.tela, BLACK, (0, CENTER_CROSS_Y), (WIDTHSCREEN, CENTER_CROSS_Y))
            
            relativo = self.convertCoords((self.X,self.Y))

            roboWithRotation = rotate(self.robo,self.angulo+self.norte)
            novoX = relativo[0]-roboWithRotation.get_rect()[2]/2
            novoY = relativo[1]-roboWithRotation.get_rect()[3]/2
            self.tela.blit(roboWithRotation,(novoX,novoY),roboWithRotation.get_rect())
            
            #HERE
            #pygame.draw.circle(self.tela, RED, (relativo[0], relativo[1]), 10)
            #plotador
            for i in Robodeck.plotar:
                posicao = self.convertCoords(i)
                posicao = (int(posicao[0]),int(posicao[1]))
                pygame.draw.circle(self.tela, RED,posicao,3)
            
            #Obstaculos
            poseRoboDesenho = self.convertCoords((self.X,self.Y))
            poseRobo = (self.X,self.Y)
            #desenha obstaculos
            for i in obstDesenho:
                posi = i[0]
                posf = i[1]
                pygame.draw.line(self.tela, BLUE, posi, posf,5)
            #testa colisao de obstaculos
            contLinesDet = [0,0,0,0]
            ultraSomFE = 10000
            ultraSomEE = 10000
            ultraSomTE = 10000
            ultraSomDE = 10000
            self.isColision = False
            for i in self.obstaculos:
                for obj in i:
                    AngAndDistObj = self.recToPol(obj,poseRobo)
                    ultra = AngAndDistObj[1]-30
                    if ultra <= 400:
                        for sus in range(0,4):
                            decr = self.intToGraus(sus*90+self.angulo+self.norte-20)
                            incr = self.intToGraus(sus*90+self.angulo+self.norte+20)
                            compa = 0
                            if decr > incr:
                                compa = (360-decr)
                            else:
                                compa = -decr
                            decrN = self.intToGraus(decr + compa)
                            incrN = self.intToGraus(incr + compa)
                            plocal = self.intToGraus(AngAndDistObj[0] + compa)
                            if decrN < plocal < incrN:
                                if self.isLineShow:                                
                                    pygame.draw.line(self.tela, RED, poseRoboDesenho, self.convertCoords(obj),1)
                                contLinesDet[sus]+=1                                
                                if (sus == 0) and (ultraSomFE > ultra):
                                    ultraSomFE = ultra
                                elif (sus == 1) and (ultraSomEE > ultra):
                                    ultraSomEE = ultra
                                elif (sus == 2) and (ultraSomTE > ultra):
                                    ultraSomTE = ultra
                                elif (sus == 3) and (ultraSomDE > ultra):
                                    ultraSomDE = ultra
                    if ultra < 0:
                        self.isColision = True
            if contLinesDet[0] == 0:
                self.sensorUltraSomF = 0
            else:
                self.sensorUltraSomF = ultraSomFE
            if contLinesDet[1] == 0:
                self.sensorUltraSomE = 0
            else:
                self.sensorUltraSomE = ultraSomEE
            if contLinesDet[2] == 0:
                self.sensorUltraSomT = 0
            else:
                self.sensorUltraSomT = ultraSomTE
            if contLinesDet[3] == 0:
                self.sensorUltraSomD = 0
            else:
                self.sensorUltraSomD = ultraSomDE
            text = str((round(self.X,1),round(self.Y,1)))
            self.imgFont = self.fonte.render(text, True,RED)            
            self.tela.blit(self.imgFont,(relativo[0]+13,relativo[1]+13))
            
            pygame.display.flip()
            pygame.display.update()
            
class ColisionRobotException(Exception):
    '''Uma exceção de colisao'''
    def __init__(self):
        Exception.__init__(self)