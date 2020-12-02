class ValidationParams:
    
    def __init__(self):
        pass
    
    def validate(self, nameParam, valueParam):
        if valueParam == "" :
            raise Exception("Obrigatorio o preenchimento do parametro %s!" % nameParam)

if __name__ == "__main__":
    v = ValidationParams()
    
    v.validate("v_SCG010_URL_REST", """#v_SCG010_URL_REST""")

#!/bin/bash
from httplib import HTTPConnection
from urlparse import urlparse

class InvokeAPI:
    
    """Classe a ser utilizada para realizar request em REST"""
    
    def __init__(self, url):
        """params:
                - url: endereco da wsdl/endpoint do servico que deve ser requisitado"""
        parsed = urlparse(url)
        self.protocol = parsed.scheme
        self.host     = parsed.hostname
        self.port     = parsed.port
        self.path     = parsed.path
        
    def execute(self, message):
        """ Metodo para executar o WS
            params
                - message: Mensagem a ser enviado para o Servidor
        """
        try:
            
            headers = {"Content-Type":"application/json", "Accept":"application/json"}
            
            conn = HTTPConnection(self.host, self.port)

            conn.request("POST", self.path, message, headers)

            response = conn.getresponse()
            responseRead = response.read()
            replyStatus = response.status
            replyMessage = response.msg
            replyHeaders = response.getheaders()
            
            #200 - OK (Synchronous)
            #201 - CREATED
            #202 - ACCEPTED(Asynchronous)
            #if replayStatus not in [200,201, 202] :
            #    raise Exception("%s - %s " % (replyStatus, replyMessage))
            
            return (responseRead,replyStatus,replyMessage,replyHeaders)
            
        except Exception:
            raise;
        finally:
            if (conn != None):
                conn.close()

import java.sql.SQLException

class SelectMsgJSON:

    def __init__(self):
        None

    def execute(self, url):

        conn = snpRef.getJDBCConnection("SRC")

        sql = """
                SELECT 
                    ID_LINHA,
                    JSON_REQUEST
                FROM INTEG_ODI_TMP.T$_ENV_SCG10_JSON
             """
        try:
            stmt = conn.createStatement()
            rs = stmt.executeQuery(sql)

            while rs.next():

                try:
                    JsonRequest = rs.getString("JSON_REQUEST")
                    JsonIdLinha = rs.getString("ID_LINHA")

                    rest = InvokeAPI(url)
                    (responseRead,replyStatus,replyMessage,replyHeaders) = rest.execute(JsonRequest)

                    JsonCdErro = "E"
                    if (replyStatus == 200):
                        JsonCdErro = "S"
                    
                    self.update(conn, replyStatus, JsonCdErro, JsonIdLinha)

                except Exception, e:
                    self.update(conn, replyStatus, JsonCdErro, JsonIdLinha)
                    
            rs.close()
            stmt.close()

        except java.sql.SQLException, e:
            print e

    def update(self,conn,replyStatus,JsonCdErro,JsonIdLinha):
        try:

            sql2 = """UPDATE INTEG_ODI_TMP.T$_ENV_SCG10_JSON SET FL_PROC = ?, RESP_STATUS = TO_NUMBER(?) WHERE ID_LINHA = ? """
            ps = conn.prepareStatement(sql2)
            ps.setString(1, JsonCdErro)
            ps.setString(2, str(replyStatus))
            ps.setString(3, JsonIdLinha)

            ps.execute()
        except:
            raise
        finally:
            if (ps != None):
                ps.close()

if __name__ == '__main__':
    select = SelectMsgJSON()
    select.execute("""#SCG.v_SCG010_URL_REST""")