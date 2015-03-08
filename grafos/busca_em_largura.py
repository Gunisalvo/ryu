from estruturas_de_dados import No, Fila, Grafo

def buscar_caminho(grafo, id_no_inicio, id_final, logger = None):
    lista_caminhos = busca_em_profundidade(grafo, id_no_inicio, id_final, logger)
    caminho = [id_final]
    no_atual = id_final
    while no_atual != id_no_inicio :
        no_atual = lista_caminhos[no_atual]
        caminho.append(no_atual)

    # reverter lista
    return caminho[::-1]

def busca_em_profundidade(grafo, id_no_inicio, id_final, logger = None):
    fila = Fila()
    fila.insere(id_no_inicio)
    visitados = {}
    visitados[id_no_inicio] = None
    
    while not fila.esta_vazia():
        id_no_atual = fila.remove()

        if id_no_atual == id_final:
            break

        if logger:
            logger.info("[Busca em Largura] no: %r" % id_no_atual)
            
        for proximo_id in grafo.buscar_vizinhos(id_no_atual):
            if proximo_id not in visitados:
                fila.insere(proximo_id)
                visitados[proximo_id] = id_no_atual

    return visitados

if __name__ == '__main__':

    class LoggerTeste:

        def info(mensagem, argumentos):
            print(mensagem, argumentos)


    cobaia = Grafo({
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