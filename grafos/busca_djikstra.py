from estruturas_de_dados import No, FilaValorada, GrafoValorado

def buscar_caminho(grafo, id_no_inicio, id_final, logger = None):
    lista_caminhos, lista_pesos = djikstra(grafo, id_no_inicio, id_final, logger)
    caminho = [id_final]
    no_atual = id_final
    while no_atual != id_no_inicio :
        no_atual = lista_caminhos[no_atual]
        caminho.append(no_atual)
        
    # reverter lista
    return caminho[::-1]

def djikstra(grafo, id_no_inicio, id_final, logger = None):
    fila = FilaValorada()
    fila.insere(id_no_inicio, 0)
    pesos = {}
    visitados = {}
    visitados[id_no_inicio] = None
    peso_atual = {}
    peso_atual[id_no_inicio] = 0
    
    while not fila.esta_vazia():
        id_no_atual = fila.remove()

        if id_no_atual == id_final:
            break

        if logger:
            logger.info("[Busca Djikstra] no: %r" % id_no_atual)

        for proximo_id in grafo.buscar_vizinhos(id_no_atual):
            peso_iteracao = peso_atual[id_no_atual] + grafo.buscar_custo(id_no_atual, proximo_id)

            if proximo_id not in peso_atual or peso_iteracao < peso_atual[proximo_id]:
                peso_atual[proximo_id] = peso_iteracao
                fila.insere(proximo_id, peso_iteracao)
                visitados[proximo_id] = id_no_atual

    return visitados, peso_atual

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