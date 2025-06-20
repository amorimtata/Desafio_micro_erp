import xml.etree.ElementTree as ET
from datetime import datetime
import os

class NFEGenerator:
    def __init__(self, nota_fiscal):
        self.nota_fiscal = nota_fiscal
        self.root = ET.Element("NFe")
        self.root.set("xmlns", "http://www.portalfiscal.inf.br/nfe")
        
    def _add_ide(self):
        ide = ET.SubElement(self.root, "ide")
        ET.SubElement(ide, "cUF").text = "35"  # Código do estado (exemplo: SP)
        ET.SubElement(ide, "cNF").text = self.nota_fiscal.numero
        ET.SubElement(ide, "natOp").text = "Venda ao Consumidor"
        ET.SubElement(ide, "mod").text = "55"  # Modelo NF-e
        ET.SubElement(ide, "serie").text = "1"
        ET.SubElement(ide, "nNF").text = self.nota_fiscal.numero
        ET.SubElement(ide, "dhEmi").text = self.nota_fiscal.data_emissao.strftime("%Y-%m-%dT%H:%M:%S-03:00")
        ET.SubElement(ide, "tpNF").text = "1"  # Saída
        ET.SubElement(ide, "idDest").text = "1"  # Interna
        ET.SubElement(ide, "cMunFG").text = "3550308"  # Código do município (exemplo: São Paulo)
        ET.SubElement(ide, "tpImp").text = "1"  # Retrato
        ET.SubElement(ide, "tpEmis").text = "1"  # Normal
        ET.SubElement(ide, "cDV").text = "1"  # Dígito verificador
        ET.SubElement(ide, "tpAmb").text = "2"  # Homologação
        ET.SubElement(ide, "finNFe").text = "1"  # Normal
        ET.SubElement(ide, "indFinal").text = "1"  # Consumidor final
        ET.SubElement(ide, "indPres").text = "1"  # Presencial
        
    def _add_emit(self):
        emit = ET.SubElement(self.root, "emit")
        ET.SubElement(emit, "CNPJ").text = "12345678901234"  # CNPJ exemplo
        ET.SubElement(emit, "xNome").text = "Empresa Exemplo Ltda"
        ET.SubElement(emit, "enderEmit")
        ET.SubElement(emit, "IE").text = "123456789"
        ET.SubElement(emit, "CRT").text = "1"  # Simples Nacional
        
    def _add_dest(self):
        dest = ET.SubElement(self.root, "dest")
        ET.SubElement(dest, "CPF").text = "12345678901"  # CPF exemplo
        ET.SubElement(dest, "xNome").text = "Cliente Exemplo"
        
    def _add_itens(self):
        det = ET.SubElement(self.root, "det")
        for item in self.nota_fiscal.itens:
            prod = ET.SubElement(det, "prod")
            ET.SubElement(prod, "cProd").text = item.produto.codigo
            ET.SubElement(prod, "xProd").text = item.produto.nome
            ET.SubElement(prod, "NCM").text = "00000000"  # NCM exemplo
            ET.SubElement(prod, "CFOP").text = "5102"  # CFOP exemplo
            ET.SubElement(prod, "uCom").text = "UN"
            ET.SubElement(prod, "qCom").text = str(item.quantidade)
            ET.SubElement(prod, "vUnCom").text = f"{item.valor_unitario:.2f}"
            ET.SubElement(prod, "vProd").text = f"{item.valor_total:.2f}"
            
    def _add_total(self):
        total = ET.SubElement(self.root, "total")
        ICMSTot = ET.SubElement(total, "ICMSTot")
        ET.SubElement(ICMSTot, "vBC").text = f"{self.nota_fiscal.valor_total:.2f}"
        ET.SubElement(ICMSTot, "vICMS").text = "0.00"
        ET.SubElement(ICMSTot, "vProd").text = f"{self.nota_fiscal.valor_total:.2f}"
        ET.SubElement(ICMSTot, "vNF").text = f"{self.nota_fiscal.valor_total:.2f}"
        
    def generate(self):
        self._add_ide()
        self._add_emit()
        self._add_dest()
        self._add_itens()
        self._add_total()
        
        # Criar diretório se não existir
        if not os.path.exists('nfe_simulada'):
            os.makedirs('nfe_simulada')
            
        # Gerar nome do arquivo
        filename = f"nfe_simulada/NFe{self.nota_fiscal.numero}.xml"
        
        # Criar árvore XML e salvar
        tree = ET.ElementTree(self.root)
        tree.write(filename, encoding='UTF-8', xml_declaration=True)
        
        return filename 