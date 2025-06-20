import logging
import random
import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validar_xml(xml_string):
    """Valida o XML da NF-e"""
    try:
        logger.info('Iniciando validação do XML...')
        
        # Parse do XML
        root = ET.fromstring(xml_string)
        
        # Definir namespace
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Validar campos obrigatórios
        emit_cnpj = root.find('.//nfe:emit/nfe:CNPJ', ns)
        if emit_cnpj is None or not emit_cnpj.text:
            return False, "Tag emit/CNPJ não encontrada no XML"
            
        dest_cnpj = root.find('.//nfe:dest/nfe:CNPJ', ns)
        if dest_cnpj is None or not dest_cnpj.text:
            return False, "Tag dest/CNPJ não encontrada no XML"
            
        dh_emi = root.find('.//nfe:ide/nfe:dhEmi', ns)
        if dh_emi is None or not dh_emi.text:
            return False, "Tag ide/dhEmi não encontrada no XML"
            
        # Validar formato da data de emissão
        try:
            datetime.strptime(dh_emi.text, '%Y-%m-%dT%H:%M:%S-03:00')
        except ValueError:
            return False, "Formato de data inválido na tag ide/dhEmi"
            
        # Validar valores dos produtos
        for det in root.findall('.//nfe:det', ns):
            v_prod = det.find('.//nfe:vProd', ns)
            if v_prod is None or not v_prod.text:
                return False, "Tag vProd não encontrada em algum item"
            try:
                float(v_prod.text)
            except ValueError:
                return False, "Valor do produto inválido"
                
        logger.info('XML validado com sucesso!')
        return True, "XML válido"
        
    except Exception as e:
        logger.error(f'Erro na validação do XML: {str(e)}')
        return False, f"Erro na validação do XML: {str(e)}"

def enviar_nfe(xml_nfe):
    """Simula o envio da NF-e para a SEFAZ"""
    try:
        logger.info('Simulando envio da NF-e para a SEFAZ...')
        
        # Validar XML
        valido, mensagem = validar_xml(xml_nfe)
        if not valido:
            return False, mensagem, None
        
        # Nova validação: rejeitar data de emissão anterior ao dia atual
        root = ET.fromstring(xml_nfe)
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        dh_emi = root.find('.//nfe:ide/nfe:dhEmi', ns)
        if dh_emi is not None and dh_emi.text:
            data_emissao = datetime.strptime(dh_emi.text[:10], '%Y-%m-%d').date()
            hoje = datetime.now().date()
            if data_emissao < hoje:
                logger.error('NF-e rejeitada: Data de emissão anterior ao permitido')
                return False, 'Data de emissão anterior ao permitido', None
        
        # Simular autorização (80% de chance de sucesso)
        if random.random() < 0.8:
            protocolo = f"123456789012345{datetime.now().strftime('%Y%m%d%H%M%S')}"
            status = "Autorizada"
            prot = ET.Element('protNFe', {'versao': '4.00'})
            infProt = ET.SubElement(prot, 'infProt')
            ET.SubElement(infProt, 'tpAmb').text = '2'  # Homologação
            ET.SubElement(infProt, 'verAplic').text = '1.0'
            ET.SubElement(infProt, 'chNFe').text = f"43{datetime.now().strftime('%y%m')}999999990001911{random.randint(1, 999999):06d}"
            ET.SubElement(infProt, 'dhRecbto').text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S-03:00')
            ET.SubElement(infProt, 'nProt').text = protocolo
            ET.SubElement(infProt, 'digVal').text = hashlib.sha1(xml_nfe.encode()).hexdigest()
            ET.SubElement(infProt, 'cStat').text = '100'  # Autorizado
            ET.SubElement(infProt, 'xMotivo').text = 'Autorizado o uso da NF-e'
            xml_protocolo = ET.tostring(prot, encoding='unicode')
            logger.info(f'NF-e autorizada com sucesso! Protocolo: {protocolo}')
            return True, "NF-e autorizada com sucesso", {
                'protocolo': protocolo,
                'status': status,
                'xml_protocolo': xml_protocolo,
                'chave': infProt.find('chNFe').text
            }
        else:
            # Simular rejeição (sem valor total ou data)
            codigos_erro = ['114']
            mensagens_erro = [
                "Valor do produto inválido"
            ]
            erro = random.choice(list(zip(codigos_erro, mensagens_erro)))
            logger.error(f'NF-e rejeitada: {erro[1]}')
            return False, f"NF-e rejeitada: {erro[1]}", None
    except Exception as e:
        logger.error(f'Erro ao enviar NF-e: {str(e)}')
        return False, f"Erro ao enviar NF-e: {str(e)}", None 