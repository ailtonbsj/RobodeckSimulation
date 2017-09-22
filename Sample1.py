# -*- coding: utf-8 -*-

"""
Use o mouse para gerar um obstaculo no cenario.
Atraves de dois cliques no ambiente de simulação
pode-ser criar um obstaulo.
A tecla L carrega o ultimo cenário salvo.
A tecla S salva o cenário atual.
As teclas de 1 a 4 carrega cenários pre-definidos.
"""

#Inclusão do Módulo Robodeck Simulator
from robodeck_pkg.robodeckSIM import *

#Cria um objeto Rododeck
robo = Robodeck()

#Inicia a simulação
robo.start()

#Movimenta robo para frente e para
robo.andar(Robodeck.ANDAR)
robo.andar(Robodeck.PARAR)

#gira robo em um sentido e para
robo.girar(Robodeck.HORARIO,Robodeck.PADRAO)
robo.girar(Robodeck.ANTIHORARIO,Robodeck.PADRAO)
robo.girar(Robodeck.PARAR,None)

#Ler odometro Direito e Esquerdo e zera
direitoOdo = robo.lerOdometroD()
esquerdoOdo = robo.lerOdometroE()
robo.zerarOdometro()

#Ler sensores ultrasonicos
frenteUltra = robo.lerUltrasomDianteiro()
atrazUltra = robo.lerUltrasomTraseiro()
esquerdoUltra = robo.lerUltrasomEsquerdo()
direitoUltra = robo.lerUltrasomDireito()

#Ler bussola do robodeck
valorBussola = robo.lerBussola()