# -*- coding: utf-8 -*-
""" Modulo Geometria """

import math
from numpy import sign

def floatToDegree(num):
    """ Converter numero real em angulos-graus """
    rev = int(num/360.)
    if sign(num) == -1:
        rev-=1
    return (num-(rev*360.))
    
def recToPol((xf,yf),(xi,yi)=(0,0)):
    """ Encontra hipotenusa e o angulo a partir de dois pontos,
    Caso o ponto inicial não seja informado, usa origem 0,0 """
    xf = float(xf)
    yf = float(yf)
    xi = float(xi)
    yi = float(yi)
    b = xf-xi
    c = yf-yi
    r = math.sqrt(b**2+c**2)
    if r != 0:
        teta = math.degrees(math.acos(b/r))
    else:
        return (0,None) #retorna 0 caso os pois pontos seja o mesmo
    if c < 0:
        teta = -teta
    teta = floatToDegree(teta)
    return (r,teta)
    
def polToRec((teta,r),(xi,yi)=(0,0)):
    """ Encontra componente x e y a partir do angulo teta a distancia r,
    Caso informa um ponto, soma as componentes ao valor encontrado """
    x = r*math.cos(math.radians(floatToDegree(teta)))+xi
    y = r*math.sin(math.radians(floatToDegree(teta)))+yi
    return (x,y) 
