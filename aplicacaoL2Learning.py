from controladorBase import ControladorBase
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

class AplicacaoL2Learning(ControladorBase):

    def __init__(self, *args, **kwargs):
        super(AplicacaoL2Learning, self).__init__(*args, **kwargs)
    # Mapa de estados da rede
        self.mapa_rede = {}

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def tratador_packet_in(self, ev):
    # Pacote com fluxo desconhecido enviado ao controlador
        self.logger.info('[ControladorL2Learning]---> PacketIN recebido de: %s', ev.msg.datapath.id)

    # Detectar limitacao da biblioteca de emulacao de switch virtual OVS
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes", ev.msg.msg_len, ev.msg.total_len)

        mensagem = ev.msg
        enlace = mensagem.datapath
        protocolo_open_flow = enlace.ofproto
        decodificador = enlace.ofproto_parser
        porta_entrante = mensagem.match['in_port']

    # Empacotar dados do PacketIN como pacote de rede
        pacote = packet.Packet(mensagem.data)
    # No cabecalho podemos checar os dados Ethernet padrao, como endereco de origem, endereco de destino, tipo de pacote, etc...
        cabecalho_ethernet = pacote.get_protocols(ethernet.ethernet)[0]

        destino = cabecalho_ethernet.dst
        origem = cabecalho_ethernet.src

        id_enlace = enlace.id

    # Evitar resposta Excecao caso um enlace nao tenha associacao
        self.mapa_rede.setdefault(id_enlace, {})

        self.logger.info('[ControladorL2Learning]---> %s %s %s %s', id_enlace, origem, destino, porta_entrante)

    # Guarda endereco Mac para evitar FLOOD na proxima chamada
        self.mapa_rede[id_enlace][origem] = porta_entrante

        if destino in self.mapa_rede[id_enlace]:
            porta_saida = self.mapa_rede[id_enlace][destino]
        else:
            porta_saida = protocolo_open_flow.OFPP_FLOOD

        acao = [decodificador.OFPActionOutput(porta_saida)]

    # instalando fluxos, nao havera mais packet in se o estado da rede se mantiver estavel
        if porta_saida != protocolo_open_flow.OFPP_FLOOD:
            mascara_de_busca = decodificador.OFPMatch(in_port=porta_entrante, eth_dst=destino)

            if mensagem.buffer_id != protocolo_open_flow.OFP_NO_BUFFER:
    # instalando uma tabela da fluxo na porta encontrada com prioridade 1
    # para o pacote completo (sem o buffer)
                self.instala_fluxo(enlace, 1, mascara_de_busca, acao, mensagem.buffer_id)
                return
            else:
    # instalando uma tabela da fluxo na porta encontrada com prioridade 1
                self.instala_fluxo(enlace, 1, mascara_de_busca, acao)
        corpo_mensagem = None
        if mensagem.buffer_id == protocolo_open_flow.OFP_NO_BUFFER:
            corpo_mensagem = msg.data

        packet_out = decodificador.OFPPacketOut(datapath=enlace, buffer_id=mensagem.buffer_id,
                                  in_port=porta_entrante, actions=acao, data=corpo_mensagem)
    
    # devolucao do pacote para o switch
        enlace.send_msg(packet_out)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        enlace = ev.msg.datapath
        porta = ev.msg.desc
    # Porta esta DOWN?
        if porta.state == 1:
            protocolo_open_flow = enlace.ofproto
            decodificador = enlace.ofproto_parser
    # Evitar resposta Excecao caso um enlace nao tenha associacao
            self.mapa_rede.setdefault(enlace.id, {})
    # Remover destinos associados
            for destino in self.mapa_rede[enlace.id].keys():
                self.logger.info('[ControladorL2Learning]---> removendo destino %s',destino)
                mascara_de_busca = decodificador.OFPMatch(eth_dst=destino)
                remover_destino = decodificador.OFPFlowMod(enlace, command=protocolo_open_flow.OFPFC_DELETE,
                                                            out_port=protocolo_open_flow.OFPP_ANY, 
                                                            out_group=protocolo_open_flow.OFPG_ANY,
                                                            priority=1, match=mascara_de_busca)
                enlace.send_msg(remover_destino)
            # del self.mapa_rede[enlace.id]

    @set_ev_cls(ofp_event.EventOFPStateChange,DEAD_DISPATCHER)
    def tratador_conexao_switch(self, ev):
    # Evento de queda de conexao
        enlace = ev.datapath
        if enlace.id in self.mapa_rede:
            self.logger.info('[ControladorL2Learning]---> removendo enlace %s',enlace.id)
            del self.mapa_rede[enlace.id]