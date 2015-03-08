import collections

class Fila(object):

    def __init__(self):
        self.itens = collections.deque()
    
    def insere(self, item):
        self.itens.append(item)
    
    def remove(self):
        return self.itens.popleft()

    def esta_vazia(self):
        return len(self.itens) == 0


import heapq

class FilaValorada(object):

    def __init__(self):
        self.itens = []
    
    def insere(self, item, peso):
        heapq.heappush(self.itens, (peso, item))
    
    def remove(self):
        return heapq.heappop(self.itens)[1]

    def esta_vazia(self):
        return len(self.itens) == 0

class Grafo(object):

    def __init__(self, nos):
        self.nos = nos
    
    def buscar_vizinhos(self, id_no):
        if id_no not in self.nos:
            return {}
        else:
            return self.nos[id_no].links

    def __getitem__(self,id_no):
        if id_no not in self.nos:
            return None
        else:
            return self.nos[id_no]

    def __repr__(self):
        return '<nos=%s>' % (self.nos)

class GrafoValorado(Grafo):

    def __init__(self, nos):
        super(GrafoValorado,self).__init__(nos)

    def buscar_custo(self, id_no, id_vizinho):
        infinito = float('inf')
        if id_no not in self.nos:
            return infinito
        elif id_vizinho not in self.nos[id_no].links:
            return infinito
        else:
            no = self.nos[id_no]
            links = no.links
            return links[id_vizinho]

class No(object):

    def __init__(self, links, geo = None):
        self.links = links
        
        self.geo = geo

    def __repr__(self):
        return '<links=%s, geo=%s>' % (self.links, self.geo)