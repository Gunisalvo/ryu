from grafos import buscar_caminho_djikstra
from grafos import buscar_caminho_a_star
from grafos import No
from grafos import GrafoValorado

class SpanningTree(object):

    def __init__(self,rede,logger=None):
        self.logger = logger
        self.mapa_nos = extrair_mapa(rede)
        if self.logger:
            self.logger.info('[SpanningTree]-----> iniciado com sucesso')

    def atualizar_mapa_rede(self,rede):
        self.mapa_nos = extrair_mapa(rede)
        if self.logger:
            self.logger.info('[SpanningTree]-----> atualizado com sucesso')

    def menor_caminho(self,origem,destino):
        caminho = buscar_caminho_djikstra(self.mapa_nos, origem, destino, self.logger)
        if self.logger:
            self.logger.info('[SpanningTree]-----> caminho calculado: %s', caminho)
        return caminho

def extrair_mapa(rede):
    #transforma dados para um formato aceitavel para o algoritimo de menor caminho
    nos = {}
    for origem in rede:
        links = {}
        for destino in rede[origem]:
            links[destino] = 1
        nos[origem] = No(links)
    return GrafoValorado(nos)

if __name__=='__main__':

    rede = {1: {2: 2}, 2: {1: 2, 3: 3, 4: 4}, 3: {2: 1}, 4: {2: 1, 5: 2, 6: 3}, 5: {4: 1}, 6: {4: 1, 7: 2}, 7: {6: 2}}
    cobaia = SpanningTree(rede)
    print cobaia.menor_caminho(1,7)
    rede = {1: {2: 2, 8: 8}, 2: {1: 2, 3: 3, 4: 4}, 3: {2: 1}, 4: {2: 1, 5: 2, 6: 3}, 5: {4: 1}, 6: {4: 1, 7: 2}, 7: {6: 2, 8: 8}, 8:{1:7,7:3}}
    cobaia = SpanningTree(rede)
    print cobaia.menor_caminho(1,7)
