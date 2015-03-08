from ryu.base import app_manager
from ryu.controller import ofp_event
from aplicacaoSpanningTree import SpanningTree
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link

class AplicacaoDiscovery(app_manager.RyuApp):
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(AplicacaoDiscovery, self).__init__(*args, **kwargs)
        self.rede = {}
        '''
        Precisamos de dependencias auxiliares?
        '''

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def tratador_switch_features(self, ev):
        enlace = ev.msg.datapath
        protocolo_open_flow = enlace.ofproto
        decodificador = enlace.ofproto_parser
        mascara_de_busca = decodificador.OFPMatch()
        acoes = [decodificador.OFPActionOutput(protocolo_open_flow.OFPP_CONTROLLER, protocolo_open_flow.OFPCML_NO_BUFFER)]
        # neste caso esta instalando uma tabela da fluxo vazia com prioridade 0
        self.instala_fluxo(enlace, 0, mascara_de_busca, acoes)

    def instala_fluxo(self, enlace, prioridade, mascara_de_busca, acoes, buffer_id=None):
        protocolo_open_flow = enlace.ofproto
        decodificador = enlace.ofproto_parser
        instrucao = [decodificador.OFPInstructionActions(protocolo_open_flow.OFPIT_APPLY_ACTIONS, acoes)]
        if buffer_id:
            modificacao_fluxo = decodificador.OFPFlowMod(datapath=enlace, buffer_id=buffer_id,
                                                            priority=prioridade, match=mascara_de_busca,
                                                            instructions=instrucao)
        else:
            modificacao_fluxo = decodificador.OFPFlowMod(datapath=enlace, priority=prioridade,
                                                            match=mascara_de_busca, instructions=instrucao)

        # essa eh a instrucao que efetivamente manda uma mensagem para o switch
        enlace.send_msg(modificacao_fluxo)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def tratador_packet_in(self, ev):        
        # Pacote com fluxo desconhecido enviado ao controlador

        # Detectar limitacao da biblioteca de emulacao de switch virtual OVS
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes", ev.msg.msg_len, ev.msg.total_len)

        mensagem = ev.msg
        enlace = mensagem.datapath
        protocolo_open_flow = enlace.ofproto
        decodificador = enlace.ofproto_parser
        porta_entrante = mensagem.match['in_port']

        # Transformar dados do PacketIN como pacote de rede
        pacote = packet.Packet(mensagem.data)

        cabecalho_ethernet = pacote.get_protocols(ethernet.ethernet)[0]

        destino = cabecalho_ethernet.dst
        origem = cabecalho_ethernet.src

        id_enlace = enlace.id
        
        # previne problemas de ordem de registro de switch e recebimento de PacketIn
        self.rede.setdefault(id_enlace,{})

        '''
        Instalar fluxos para rotas desconecidas
        '''
        
        acao = [decodificador.OFPActionOutput(porta_saida)]

        # instalando fluxos, nao havera mais packet in se o estado da rede se mantiver estavel
        if porta_saida != protocolo_open_flow.OFPP_FLOOD:
            mascara_de_busca = decodificador.OFPMatch(in_port=porta_entrante, eth_dst=proximo_mac)

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
            corpo_mensagem = mensagem.data

        packet_out = decodificador.OFPPacketOut(datapath=enlace, buffer_id=mensagem.buffer_id,
                                  in_port=porta_entrante, actions=acao, data=corpo_mensagem)
    
        # devolucao do pacote para o switch
        enlace.send_msg(packet_out)

    @set_ev_cls(event.EventLinkAdd)
    def registrar_link(self, ev):
        '''
        Novo Link criado entre switches
        '''

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        self
        '''
        Mundanca de estado da porta
        '''

    @set_ev_cls(event.EventSwitchLeave)
    def remover_switch(self, ev):
        self
        '''
        Switch novo entra na rede
        '''