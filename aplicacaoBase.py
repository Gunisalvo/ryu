from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, HANDSHAKE_DISPATCHER, DEAD_DISPATCHER 
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib import hub

class AplicacaoBase(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(AplicacaoBase, self).__init__(*args, **kwargs)
        self.enlaces = {}
        # thread que checa estado da rede - o servico chama o metodo: _monitorar_rede
        # self.servico_monitoramento = hub.spawn(self._monitorar_rede)

    @set_ev_cls(ofp_event.EventOFPHello, HANDSHAKE_DISPATCHER)
    def tratador_switch_hello(self, ev):
        #controlador estabelecendo comunicacao com o switch
        self.logger.info('[ControladorBase]---> HELLO recebido de: %s', ev.msg.elements)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def tratador_switch_features(self, ev):
        #controlador recebe a resposta com as configuracoes do switch
        self.logger.info('[ControladorBase]---> FeatureRequest recebido de: %s', ev.msg.datapath.id)
        enlace = ev.msg.datapath
        protocolo_open_flow = enlace.ofproto
        decodificador = enlace.ofproto_parser
        mascara_de_busca = decodificador.OFPMatch()
        acoes = [decodificador.OFPActionOutput(protocolo_open_flow.OFPP_CONTROLLER, protocolo_open_flow.OFPCML_NO_BUFFER)]
        # neste caso esta instalando uma tabela da fluxo vazia com prioridade 0
        self.instala_fluxo(enlace, 0, mascara_de_busca, acoes)

    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def tratador_conexao_switch(self, ev):
        self.logger.info('[ControladorBase]---> mudanca estado conexao: %s', ev.state)
        enlace = ev.datapath
        # Evento de registro de conexao
        if ev.state == MAIN_DISPATCHER:
            if not enlace.id in self.enlaces:
                self.enlaces[enlace.id] = enlace
        # Evento de queda de conexao
        elif ev.state == DEAD_DISPATCHER:
            if enlace.id in self.enlaces:
                del self.enlaces[enlace.id]

    @set_ev_cls(ofp_event.EventOFPPortStatus,MAIN_DISPATCHER)
    def tratador_conexao_portas(self, ev):
        porta = ev.msg.desc
        self.logger.info('[ControladorBase]---> mudanca estado porta: %s %s estado: %s', porta.hw_addr, porta.port_no, porta.state)
        #Evento interface porta caiu 
        if(porta.state == 1):
            self.logger.info('[ControladorBase]---> Interface DOWN')
        #Evento interface reestabelecida
        else:
            self.logger.info('[ControladorBase]---> Interface UP')

    def _monitorar_rede(self):
        while True:
            for enlace in self.enlaces.values():
                protocolo_open_flow = enlace.ofproto
                decodificador = enlace.ofproto_parser
                requsicao_estado_portas = decodificador.OFPPortStatsRequest(enlace, 0, protocolo_open_flow.OFPP_ANY)
                enlace.send_msg(requsicao_estado_portas)
            hub.sleep(10)

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

    def remove_fluxo(self, enlace, mascara_de_busca):
        protocolo_open_flow = enlace.ofproto
        decodificador = enlace.ofproto_parser
        modificacao = decodificador.OFPFlowMod(datapath=enlace,
                                                command=protocolo_open_flow.OFPFC_DELETE,
                                                out_port=protocolo_open_flow.OFPP_ANY,
                                                out_group=protocolo_open_flow.OFPG_ANY,
                                                match= mascara_de_busca)
        enlace.send_msg(modificacao)