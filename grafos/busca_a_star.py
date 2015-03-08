import math
from estruturas_de_dados import No, FilaValorada, GrafoValorado

def buscar_caminho(grafo, id_no_inicio, id_final, logger = None):
    lista_caminhos, lista_pesos = a_star(grafo, id_no_inicio, id_final, logger)
    caminho = [id_final]
    no_atual = id_final
    while no_atual != id_no_inicio :
        no_atual = lista_caminhos[no_atual]
        caminho.append(no_atual)
        
    # reverter lista
    return caminho[::-1]

def a_star(grafo, id_no_inicio, id_final, logger = None):

    fila = FilaValorada()
    fila.insere(id_no_inicio, 0)
    
    visitados = {}
    visitados[id_no_inicio] = None

    pesos = {}
    peso_atual = {}
    peso_atual[id_no_inicio] = 0
    
    while not fila.esta_vazia():
        id_no_atual = fila.remove()

        if id_no_atual == id_final:
            break

        if logger:
            logger.info("[Busca A*] no: %r" % id_no_atual)

        for proximo_id in grafo.buscar_vizinhos(id_no_atual):
            peso_iteracao = peso_atual[id_no_atual] + grafo.buscar_custo(id_no_atual, proximo_id)

            if proximo_id not in peso_atual or peso_iteracao < peso_atual[proximo_id]:
                # Heuristica: Links de rede mais proximo tem menor latencia
                peso_atual[proximo_id] = peso_iteracao + heuristica(grafo[id_no_atual],grafo[proximo_id])
                fila.insere(proximo_id, peso_iteracao)
                visitados[proximo_id] = id_no_atual

    return visitados, peso_atual

def heuristica(no_a, no_b):
    '''
        Calcura vetor distancia entre os dois pares de coordenadas
    '''
    componente_x = abs(no_a.geo[0] - no_b.geo[0]) ** 2
    componente_y = abs(no_a.geo[1] - no_b.geo[1]) ** 2
    return math.sqrt( componente_x + componente_y )

if __name__ == '__main__':

    class LoggerTeste:

        def info(mensagem, argumentos):
            print(mensagem, argumentos)


    cobaia = GrafoValorado({
        'A': No({ 'B' : 1 , 'E' : 3 },(4,1)),
        'B': No({ 'C' : 2 , 'D' : 5 , 'A' : 1 },(5,10)),
        'C': No({ 'D' : 1 , 'B' : 2 },(2,13)),
        'D': No({ 'B' : 5 , 'C' : 1 , 'G' : 2 },(3,3)),
        'E': No({ 'F' : 1 , 'A' : 3 },(2,1)),
        'F': No({ 'G' : 2 , 'E' : 1 },(1,2)),
        'G': No({ 'D' : 2 , 'F' : 2 },(2,4))
    })

    caminho = buscar_caminho(cobaia, 'A', 'D', LoggerTeste())

    print caminho