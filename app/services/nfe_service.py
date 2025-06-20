from zeep import Client
from zeep.transports import Transport
from zeep.wsse.signature import Signature
from zeep.wsse.username import UsernameToken
from datetime import datetime
import os
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import logging

logger = logging.getLogger(__name__)

class NFEService:
    def __init__(self):
        self.certificado_path = os.path.join(os.path.dirname(__file__), '../../certificados/teste.pfx')
        self.certificado_senha = '123456'
        self.uf = 'RS'
        self.homologacao = True
        self.versao = '4.00'
        self.ambiente = 2  # 1=Produção, 2=Homologação
        
        # Configurações do emitente (usando dados de teste da SEFAZ)
        self.emitente = {
            'cnpj': '99999999000191',
            'razao_social': 'EMPRESA DE TESTE',
            'nome_fantasia': 'EMPRESA DE TESTE',
            'ie': 'ISENTO',
            'endereco': 'Rua Teste',
            'numero': '123',
            'bairro': 'Centro',
            'cidade': 'Porto Alegre',
            'uf': 'RS',
            'cep': '90000000',
            'telefone': '5133333333',
            'email': 'teste@teste.com.br'
        }

    def calcular_preco_final_icms(self, preco_base, aliquota):
        """Calcula o preço final com ICMS embutido (por dentro)"""
        return round(preco_base / (1 - aliquota), 2)

    def calcular_icms_por_dentro(self, preco_final, aliquota):
        """Calcula o valor do ICMS destacado (por dentro)"""
        return round((preco_final * aliquota) / (1 + aliquota), 2)

    def gerar_nfe(self, nfe_model):
        """Gera uma NF-e a partir do modelo do banco de dados, ICMS por dentro, centralizando o cálculo para XML e PDF."""
        try:
            aliquota = 0.18
            nfe = ET.Element('NFe', {'xmlns': 'http://www.portalfiscal.inf.br/nfe'})
            infNFe = ET.SubElement(nfe, 'infNFe', {'Id': f'NFe{nfe_model.numero}'})
            ide = ET.SubElement(infNFe, 'ide')
            ET.SubElement(ide, 'cUF').text = '43'  # RS
            ET.SubElement(ide, 'cNF').text = str(nfe_model.numero)
            ET.SubElement(ide, 'natOp').text = nfe_model.natureza_operacao
            ET.SubElement(ide, 'serie').text = str(nfe_model.serie)
            ET.SubElement(ide, 'nNF').text = str(nfe_model.numero)
            data_emissao = nfe_model.data_emissao
            agora = datetime.now()
            if data_emissao > agora:
                data_emissao = agora
            ET.SubElement(ide, 'dhEmi').text = data_emissao.strftime('%Y-%m-%dT%H:%M:%S-03:00')
            ET.SubElement(ide, 'tpNF').text = '1'  # Saída
            ET.SubElement(ide, 'idDest').text = '1'  # Interna
            ET.SubElement(ide, 'cMunFG').text = '4314902'  # Porto Alegre
            ET.SubElement(ide, 'tpImp').text = '1'  # Retrato
            ET.SubElement(ide, 'tpEmis').text = '1'  # Normal
            ET.SubElement(ide, 'cDV').text = '0'  # Dígito verificador
            ET.SubElement(ide, 'tpAmb').text = str(self.ambiente)
            ET.SubElement(ide, 'finNFe').text = '1'  # Normal
            ET.SubElement(ide, 'indFinal').text = '1'  # Final
            ET.SubElement(ide, 'indPres').text = '1'  # Presencial
            ET.SubElement(ide, 'procEmi').text = '0'  # Aplicativo do contribuinte
            ET.SubElement(ide, 'verProc').text = '1.0'
            
            # Emitente
            emit = ET.SubElement(infNFe, 'emit')
            ET.SubElement(emit, 'CNPJ').text = self.emitente['cnpj']
            ET.SubElement(emit, 'xNome').text = self.emitente['razao_social']
            ET.SubElement(emit, 'xFant').text = self.emitente['nome_fantasia']
            ET.SubElement(emit, 'IE').text = self.emitente['ie']
            
            enderEmit = ET.SubElement(emit, 'enderEmit')
            ET.SubElement(enderEmit, 'xLgr').text = self.emitente['endereco']
            ET.SubElement(enderEmit, 'nro').text = self.emitente['numero']
            ET.SubElement(enderEmit, 'xBairro').text = self.emitente['bairro']
            ET.SubElement(enderEmit, 'cMun').text = '4314902'  # Porto Alegre
            ET.SubElement(enderEmit, 'xMun').text = self.emitente['cidade']
            ET.SubElement(enderEmit, 'UF').text = self.emitente['uf']
            ET.SubElement(enderEmit, 'CEP').text = self.emitente['cep']
            ET.SubElement(enderEmit, 'cPais').text = '1058'  # Brasil
            ET.SubElement(enderEmit, 'xPais').text = 'BRASIL'
            
            # Destinatário
            dest = ET.SubElement(infNFe, 'dest')
            ET.SubElement(dest, 'CNPJ').text = nfe_model.destinatario_cnpj
            ET.SubElement(dest, 'xNome').text = nfe_model.destinatario_razao_social
            ET.SubElement(dest, 'IE').text = nfe_model.destinatario_ie
            
            enderDest = ET.SubElement(dest, 'enderDest')
            ET.SubElement(enderDest, 'xLgr').text = nfe_model.destinatario_endereco
            ET.SubElement(enderDest, 'nro').text = nfe_model.destinatario_numero
            ET.SubElement(enderDest, 'xBairro').text = nfe_model.destinatario_bairro
            ET.SubElement(enderDest, 'cMun').text = '4314902'  # Porto Alegre
            ET.SubElement(enderDest, 'xMun').text = nfe_model.destinatario_cidade
            ET.SubElement(enderDest, 'UF').text = nfe_model.destinatario_uf
            ET.SubElement(enderDest, 'CEP').text = nfe_model.destinatario_cep
            ET.SubElement(enderDest, 'cPais').text = '1058'  # Brasil
            ET.SubElement(enderDest, 'xPais').text = 'BRASIL'
            
            # Itens
            total_vBC = 0
            total_vICMS = 0
            total_vProd = 0
            for item in nfe_model.itens:
                det = ET.SubElement(infNFe, 'det', {'nItem': str(len(infNFe.findall('det')) + 1)})
                prod = ET.SubElement(det, 'prod')
                preco_base = item.valor_unitario
                preco_final = self.calcular_preco_final_icms(preco_base, aliquota)
                vUnCom = preco_final  # valor unitário COM ICMS embutido
                vProd = round(vUnCom * item.quantidade, 2)
                vICMS = round((vProd * aliquota) / (1 + aliquota), 2)
                vBC = round(vProd - vICMS, 2)
                total_vBC += vBC
                total_vICMS += vICMS
                total_vProd += vProd
                ET.SubElement(prod, 'cProd').text = item.produto.codigo
                ET.SubElement(prod, 'xProd').text = item.produto.nome
                ET.SubElement(prod, 'NCM').text = item.ncm
                ET.SubElement(prod, 'CFOP').text = item.cfop
                ET.SubElement(prod, 'uCom').text = 'UN'
                ET.SubElement(prod, 'qCom').text = f"{item.quantidade:.2f}"
                ET.SubElement(prod, 'vUnCom').text = f"{vUnCom:.2f}"  # valor final ao consumidor
                ET.SubElement(prod, 'vProd').text = f"{vProd:.2f}"
                imposto = ET.SubElement(det, 'imposto')
                icms = ET.SubElement(imposto, 'ICMS')
                icms00 = ET.SubElement(icms, 'ICMS00')
                ET.SubElement(icms00, 'CST').text = '00'
                ET.SubElement(icms00, 'vBC').text = f"{vBC:.2f}"
                ET.SubElement(icms00, 'pICMS').text = '18.00'
                ET.SubElement(icms00, 'vICMS').text = f"{vICMS:.2f}"
            
            # Totais
            total = ET.SubElement(infNFe, 'total')
            icmsTot = ET.SubElement(total, 'ICMSTot')
            ET.SubElement(icmsTot, 'vBC').text = f"{total_vBC:.2f}"
            ET.SubElement(icmsTot, 'vICMS').text = f"{total_vICMS:.2f}"
            ET.SubElement(icmsTot, 'vNF').text = f"{total_vProd:.2f}"
            
            # Transporte
            transp = ET.SubElement(infNFe, 'transp')
            ET.SubElement(transp, 'modFrete').text = '9'  # Sem frete
            
            # Pagamento
            pag = ET.SubElement(infNFe, 'pag')
            detPag = ET.SubElement(pag, 'detPag')
            ET.SubElement(detPag, 'tPag').text = '01'  # Dinheiro
            ET.SubElement(detPag, 'vPag').text = f"{total_vProd:.2f}"
            
            # Informações adicionais
            infAdic = ET.SubElement(infNFe, 'infAdic')
            ET.SubElement(infAdic, 'infAdFisco').text = 'NF-e gerada em ambiente de homologação'
            
            # Corrigir data de emissão no XML
            dhEmi = ide.find('dhEmi')
            if dhEmi is not None:
                dhEmi.text = data_emissao.strftime('%Y-%m-%dT%H:%M:%S-03:00')
            
            # Converter para string
            xml_string = ET.tostring(nfe, encoding='unicode')
            
            # Salvar XML
            xml_path = os.path.join(os.path.dirname(__file__), f'../../xml/nfe_{nfe_model.numero}.xml')
            os.makedirs(os.path.dirname(xml_path), exist_ok=True)
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_string)
            
            # Atualizar status da NF-e
            nfe_model.status = 'emitida'
            nfe_model.xml_path = xml_path
            
            return True, "NF-e gerada com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao gerar NF-e: {str(e)}"

    def gerar_pdf(self, nfe_model):
        """Gera o DANFE SIMPLIFICADO com ICMS por dentro, exibindo preço final e ICMS correto no DANFE"""
        try:
            aliquota = 0.18
            pdf_path = os.path.join(os.path.dirname(__file__), f'../../pdf/nfe_{nfe_model.numero}.pdf')
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            y = height - 50
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, y, f"DANFE SIMPLIFICADO - NF-e {nfe_model.numero}")
            y -= 30
            c.setFont("Helvetica", 11)
            c.drawString(50, y, f"Série: {nfe_model.serie}  Data: {nfe_model.data_emissao.strftime('%d/%m/%Y %H:%M')}")
            y -= 20
            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Emitente: {nfe_model.emitente_razao_social}  CNPJ: {nfe_model.emitente_cnpj}  IE: {nfe_model.emitente_ie}")
            y -= 15
            c.drawString(50, y, f"Destinatário: {nfe_model.destinatario_razao_social}  CNPJ: {nfe_model.destinatario_cnpj}")
            y -= 15
            c.drawString(50, y, f"Endereço: {nfe_model.destinatario_endereco}, {nfe_model.destinatario_numero} - {nfe_model.destinatario_bairro}, {nfe_model.destinatario_cidade}/{nfe_model.destinatario_uf} CEP: {nfe_model.destinatario_cep}")
            y -= 25
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Itens:")
            y -= 20
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, "Código")
            c.drawString(150, y, "Produto")
            c.drawString(320, y, "Qtd")
            c.drawString(370, y, "Vl. Unit.")
            c.drawString(450, y, "Total")
            c.drawString(520, y, "ICMS (18%)")
            y -= 10
            c.line(50, y, width - 50, y)
            y -= 15
            c.setFont("Helvetica", 10)
            total_icms = 0
            total_prod = 0
            for item in nfe_model.itens:
                preco_base = item.valor_unitario
                preco_final = self.calcular_preco_final_icms(preco_base, aliquota)
                vUnCom = preco_final  # valor unitário exibido no DANFE (com ICMS embutido)
                vProd = round(vUnCom * item.quantidade, 2)
                vICMS = self.calcular_icms_por_dentro(vProd, aliquota)  # ICMS calculado sobre o valor final
                total_icms += vICMS
                total_prod += vProd
                c.drawString(50, y, item.produto.codigo)
                c.drawString(150, y, item.produto.nome)
                c.drawString(320, y, f"{item.quantidade:.0f}")
                c.drawString(370, y, f"R$ {vUnCom:.2f}")
                c.drawString(450, y, f"R$ {vProd:.2f}")
                c.drawString(520, y, f"R$ {vICMS:.2f}")
                y -= 15
            y -= 10
            c.line(50, y, width - 50, y)
            y -= 25
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"Total do ICMS:    R$ {total_icms:.2f}")
            y -= 20
            c.drawString(50, y, f"Valor Total:    R$ {total_prod:.2f}")
            c.save()
            nfe_model.pdf_path = pdf_path
            return True, "PDF gerado com sucesso!"
        except Exception as e:
            logger.error(f'Erro ao gerar PDF: {str(e)}')
            return False, f'Erro ao gerar PDF: {str(e)}'

    def gerar_xml(self, nfe_model):
        """Gera o XML da NF-e e retorna como string"""
        try:
            logger.info('Iniciando geração do XML da NF-e...')
            
            # Criar XML da NF-e
            nfe = ET.Element('NFe', {'xmlns': 'http://www.portalfiscal.inf.br/nfe'})
            
            # Informações básicas
            infNFe = ET.SubElement(nfe, 'infNFe', {'Id': f'NFe{nfe_model.numero}'})
            ide = ET.SubElement(infNFe, 'ide')
            ET.SubElement(ide, 'cUF').text = '43'  # RS
            ET.SubElement(ide, 'cNF').text = str(nfe_model.numero)
            ET.SubElement(ide, 'natOp').text = nfe_model.natureza_operacao
            ET.SubElement(ide, 'serie').text = str(nfe_model.serie)
            ET.SubElement(ide, 'nNF').text = str(nfe_model.numero)
            ET.SubElement(ide, 'dhEmi').text = nfe_model.data_emissao.strftime('%Y-%m-%dT%H:%M:%S-03:00')
            ET.SubElement(ide, 'tpNF').text = '1'  # Saída
            ET.SubElement(ide, 'idDest').text = '1'  # Interna
            ET.SubElement(ide, 'cMunFG').text = '4314902'  # Porto Alegre
            ET.SubElement(ide, 'tpImp').text = '1'  # Retrato
            ET.SubElement(ide, 'tpEmis').text = '1'  # Normal
            ET.SubElement(ide, 'cDV').text = '0'  # Dígito verificador
            ET.SubElement(ide, 'tpAmb').text = str(self.ambiente)
            ET.SubElement(ide, 'finNFe').text = '1'  # Normal
            ET.SubElement(ide, 'indFinal').text = '1'  # Final
            ET.SubElement(ide, 'indPres').text = '1'  # Presencial
            ET.SubElement(ide, 'procEmi').text = '0'  # Aplicativo do contribuinte
            ET.SubElement(ide, 'verProc').text = '1.0'
            
            # Emitente
            emit = ET.SubElement(infNFe, 'emit')
            ET.SubElement(emit, 'CNPJ').text = self.emitente['cnpj']
            ET.SubElement(emit, 'xNome').text = self.emitente['razao_social']
            ET.SubElement(emit, 'xFant').text = self.emitente['nome_fantasia']
            ET.SubElement(emit, 'IE').text = self.emitente['ie']
            
            enderEmit = ET.SubElement(emit, 'enderEmit')
            ET.SubElement(enderEmit, 'xLgr').text = self.emitente['endereco']
            ET.SubElement(enderEmit, 'nro').text = self.emitente['numero']
            ET.SubElement(enderEmit, 'xBairro').text = self.emitente['bairro']
            ET.SubElement(enderEmit, 'cMun').text = '4314902'  # Porto Alegre
            ET.SubElement(enderEmit, 'xMun').text = self.emitente['cidade']
            ET.SubElement(enderEmit, 'UF').text = self.emitente['uf']
            ET.SubElement(enderEmit, 'CEP').text = self.emitente['cep']
            ET.SubElement(enderEmit, 'cPais').text = '1058'  # Brasil
            ET.SubElement(enderEmit, 'xPais').text = 'BRASIL'
            
            # Destinatário
            dest = ET.SubElement(infNFe, 'dest')
            ET.SubElement(dest, 'CNPJ').text = nfe_model.destinatario_cnpj
            ET.SubElement(dest, 'xNome').text = nfe_model.destinatario_razao_social
            ET.SubElement(dest, 'IE').text = nfe_model.destinatario_ie
            
            enderDest = ET.SubElement(dest, 'enderDest')
            ET.SubElement(enderDest, 'xLgr').text = nfe_model.destinatario_endereco
            ET.SubElement(enderDest, 'nro').text = nfe_model.destinatario_numero
            ET.SubElement(enderDest, 'xBairro').text = nfe_model.destinatario_bairro
            ET.SubElement(enderDest, 'cMun').text = '4314902'  # Porto Alegre
            ET.SubElement(enderDest, 'xMun').text = nfe_model.destinatario_cidade
            ET.SubElement(enderDest, 'UF').text = nfe_model.destinatario_uf
            ET.SubElement(enderDest, 'CEP').text = nfe_model.destinatario_cep
            ET.SubElement(enderDest, 'cPais').text = '1058'  # Brasil
            ET.SubElement(enderDest, 'xPais').text = 'BRASIL'
            
            # Itens
            aliquota = 0.18
            total_vBC = 0
            total_vICMS = 0
            total_vProd = 0
            for item in nfe_model.itens:
                det = ET.SubElement(infNFe, 'det', {'nItem': str(len(infNFe.findall('det')) + 1)})
                prod = ET.SubElement(det, 'prod')
                preco_base = item.valor_unitario
                preco_final = self.calcular_preco_final_icms(preco_base, aliquota)
                vUnCom = preco_final  # valor unitário COM ICMS embutido
                vProd = round(vUnCom * item.quantidade, 2)
                vICMS = round((vProd * aliquota) / (1 + aliquota), 2)
                vBC = round(vProd - vICMS, 2)
                total_vBC += vBC
                total_vICMS += vICMS
                total_vProd += vProd
                ET.SubElement(prod, 'cProd').text = item.produto.codigo
                ET.SubElement(prod, 'xProd').text = item.produto.nome
                ET.SubElement(prod, 'NCM').text = item.ncm
                ET.SubElement(prod, 'CFOP').text = item.cfop
                ET.SubElement(prod, 'uCom').text = 'UN'
                ET.SubElement(prod, 'qCom').text = f"{item.quantidade:.2f}"
                ET.SubElement(prod, 'vUnCom').text = f"{vUnCom:.2f}"  # valor final ao consumidor
                ET.SubElement(prod, 'vProd').text = f"{vProd:.2f}"
                imposto = ET.SubElement(det, 'imposto')
                icms = ET.SubElement(imposto, 'ICMS')
                icms00 = ET.SubElement(icms, 'ICMS00')
                ET.SubElement(icms00, 'CST').text = '00'
                ET.SubElement(icms00, 'vBC').text = f"{vBC:.2f}"
                ET.SubElement(icms00, 'pICMS').text = '18.00'
                ET.SubElement(icms00, 'vICMS').text = f"{vICMS:.2f}"
            
            # Totais
            total = ET.SubElement(infNFe, 'total')
            icmsTot = ET.SubElement(total, 'ICMSTot')
            ET.SubElement(icmsTot, 'vBC').text = f"{total_vBC:.2f}"
            ET.SubElement(icmsTot, 'vICMS').text = f"{total_vICMS:.2f}"
            ET.SubElement(icmsTot, 'vNF').text = f"{total_vProd:.2f}"
            
            # Transporte
            transp = ET.SubElement(infNFe, 'transp')
            ET.SubElement(transp, 'modFrete').text = '9'  # Sem frete
            
            # Pagamento
            pag = ET.SubElement(infNFe, 'pag')
            detPag = ET.SubElement(pag, 'detPag')
            ET.SubElement(detPag, 'tPag').text = '01'
            ET.SubElement(detPag, 'vPag').text = f"{total_vProd:.2f}"
            
            # Informações adicionais
            infAdic = ET.SubElement(infNFe, 'infAdic')
            ET.SubElement(infAdic, 'infAdFisco').text = 'NF-e gerada em ambiente de homologação'
            
            # Converter para string
            xml_string = ET.tostring(nfe, encoding='unicode')
            
            # Log do XML gerado
            logger.info(f'XML gerado: {xml_string[:200]}...')
            
            # Salvar XML
            xml_path = os.path.join(os.path.dirname(__file__), f'../../xml/nfe_{nfe_model.numero}.xml')
            os.makedirs(os.path.dirname(xml_path), exist_ok=True)
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_string)
            
            # Atualizar status da NF-e
            nfe_model.status = 'emitida'
            nfe_model.xml_path = xml_path
            
            logger.info('XML gerado com sucesso!')
            return xml_string
            
        except Exception as e:
            logger.error(f'Erro ao gerar XML da NF-e: {str(e)}')
            raise Exception(f"Erro ao gerar XML da NF-e: {str(e)}")

    def salvar_protocolo(self, nfe_model, protocolo_data):
        """Salva o protocolo da NF-e"""
        try:
            # Salvar XML do protocolo
            xml_path = os.path.join(os.path.dirname(__file__), f'../../xml/protocolo_{nfe_model.numero}.xml')
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(protocolo_data['xml_protocolo'])
            
            # Atualizar modelo
            nfe_model.protocolo = protocolo_data['protocolo']
            nfe_model.chave = protocolo_data['chave']
            nfe_model.status = 'autorizada'
            nfe_model.protocolo_path = xml_path
            
            return True
        except Exception as e:
            logger.error(f'Erro ao salvar protocolo: {str(e)}')
            return False 