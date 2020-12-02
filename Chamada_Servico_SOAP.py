class ValidationParams:
    
    def __init__(self):
        pass
    
    def validate(self, nameParam, valueParam):
        if valueParam == "" :
            raise Exception("Obrigatorio o preenchimento do parametro %s!" % nameParam)

if __name__ == "__main__":
    v = ValidationParams()
    
    v.validate("vg_WSDL", """#vg_WSDL""")
    v.validate("vg_SOAP_ACTION", """#vg_SOAP_ACTION""")
    v.validate("pg_NUM_SESSAO", """#pg_NUM_SESSAO""")
    v.validate("v_SCG_ENVIA_TRAVA_QTD_THREAD", """#v_SCG_ENVIA_TRAVA_QTD_THREAD""")
    v.validate("v_SCG_ENVIA_TRAVA_MOD","""#v_SCG_ENVIA_TRAVA_MOD""")

#!/bin/bash
from httplib import HTTPConnection
from urlparse import urlparse

class InvokeWS:
    
    """Classe a ser utilizada para realizar request em WS"""
    
    def __init__(self, url):
        """params:
                - url: endereco da wsdl/endpoint do servico que deve ser requisitado"""
        parsed = urlparse(url)
        self.protocol = parsed.scheme
        self.host     = parsed.hostname
        self.port     = parsed.port
        self.path     = parsed.path
        
    def execute(self, message, soapAction=None):
        """ Metodo para executar o WS
            params
                - message: Mensagem a ser enviado para o WS
                - soapAction: Nao e obrigatorio informar, mas se existir mais de um servico com o
                              mesmo namespace, deve utilizar para selecionar a operacao desejada
        """
        try:
            if(message.find("&")):
                message = message.replace("&", "&amp;")
                    
            message = message.encode('ascii', 'xmlcharrefreplace')
            
            conn = HTTPConnection(self.host, self.port)
            
            conn.putrequest("POST", self.path)
            conn.putheader("Content-Type", "text/xml; charset=iso-8859-1")
            conn.putheader("Content-Length", str(len(message)))
            
            if(soapAction):
                conn.putheader("SOAPAction", soapAction)
            
            conn.endheaders()
            conn.send(message)
            
            response = conn.getresponse()
            responseRead = response.read()
            replyStatus = response.status
            replyReason = response.reason
            replyMessage = response.msg
            replyHeaders = response.getheaders()
            
            #200 - OK (Synchronous)
            #201 - CREATED
            #202 - ACCEPTED(Asynchronous)
            #if replayStatus not in [200,201, 202] :
            #    raise Exception("%s - %s " % (replyStatus, replyMessage))
            
            return (responseRead,replyStatus,replyReason,replyMessage,replyHeaders)
            
        except Exception:
            raise;
        finally:
            if (conn != None):
                conn.close()


import java.sql.SQLException

class SelectMsgSoap:

    def __init__(self):
        None

    def execute(self, wsdl, soapAction, nrSession, nrThread, nrMod):

        conn = snpRef.getJDBCConnection("SRC")

        sql = """
                SELECT 
                    ENV_WS_TRAVA.XML_REQUEST, 
                    ENV_WS_TRAVA.ID_MOD_LINHA,
                    ENV_WS_TRAVA.ID_CTAT
                FROM
                    (SELECT    XML_REQUEST,
                            MOD(ID_LINHA, '%s') ID_MOD_LINHA,
                            ID_CTAT
                    FROM INTEG_ODI_TMP.T$_ENV_WS_TRAVA
                    WHERE FL_PROC = 'P'
                ) ENV_WS_TRAVA
                WHERE ENV_WS_TRAVA.ID_MOD_LINHA = '%s'
             """ % (nrThread, nrMod)
        try:
            stmt = conn.createStatement()
            rs = stmt.executeQuery(sql)

            while rs.next():

                try:
                    xmlRequest = rs.getString("XML_REQUEST")
                    xmIdCtat = rs.getString("ID_CTAT")

                    ws = InvokeWS(wsdl)
                    (responseRead,replyStatus,replyReason,replyMessage,replyHeaders) = ws.execute(xmlRequest, soapAction)

                    xmlCdErro = "E"
                    if responseRead.find("codigodRetorno>0<") != -1 or responseRead.find("codigoRetorno>0<") != -1:
                        xmlCdErro = "S"

                    self.update(conn, replyStatus, replyReason, xmlCdErro, xmIdCtat)

                except Exception, e:
                    self.update(conn, replyStatus, replyReason, xmlCdErro, xmIdCtat)
                    
            rs.close()
            stmt.close()

        except java.sql.SQLException, e:
            print e

    def update(self,conn,replyStatus,replyReason,xmlCdErro,xmIdCtat):
        try:

            sql2 = """UPDATE INTEG_ODI_TMP.T$_ENV_WS_TRAVA SET FL_PROC = ?, RESP_STATUS = TO_NUMBER(?), RESP_REASON = ?   WHERE ID_CTAT = ? """
            ps = conn.prepareStatement(sql2)
            ps.setString(1, xmlCdErro)
            ps.setString(2, str(replyStatus))
            ps.setString(3, str(replyReason))
            ps.setString(4, xmIdCtat)

            ps.execute()
        except:
            raise
        finally:
            if (ps != None):
                ps.close()

if __name__ == '__main__':
    select = SelectMsgSoap()
    select.execute("""#vg_WSDL""", """#vg_SOAP_ACTION""", """#pg_NUM_SESSAO""", """#v_SCG_ENVIA_TRAVA_QTD_THREAD""", """#v_SCG_ENVIA_TRAVA_MOD""")