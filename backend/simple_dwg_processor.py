import ezdxf
import os
import subprocess
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextEntity:
    handle: str
    text: str
    entity_type: str
    layer: str
    position: Tuple[float, float, float]
    height: float
    style: str
    rotation: float
    width_factor: float
    insertion_point: Optional[Tuple[float, float, float]] = None

class SimpleDWGProcessor:
    def __init__(self):
        self.supported_formats = ['.dwg', '.dxf']

    def convert_dwg_to_dxf(self, dwg_path: str) -> str:
        """Attempt to convert DWG to DXF using available methods"""
        try:
            dxf_path = dwg_path.rsplit('.', 1)[0] + '.dxf'

            # If it's already a DXF file, return as is
            if dwg_path.lower().endswith('.dxf'):
                return dwg_path

            # Method 1: Try using ODA File Converter (if available)
            oda_paths = [
                "ODAFileConverter",
                r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
                r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe"
            ]

            for oda_path in oda_paths:
                if os.path.exists(oda_path):
                    try:
                        output_dir = os.path.dirname(dwg_path)
                        result = subprocess.run([
                            oda_path, output_dir, output_dir, "ACAD2018", "DXF", "0", "1"
                        ], capture_output=True, text=True, timeout=60)

                        if result.returncode == 0 and os.path.exists(dxf_path):
                            logger.info(f"Successfully converted DWG to DXF using ODA File Converter")
                            return dxf_path
                    except Exception as e:
                        logger.warning(f"ODA File Converter failed: {e}")

            # Method 2: Try using DWGDirect/DWGDirect libraries
            try:
                import win32com.client
                acad = win32com.client.Dispatch("AutoCAD.Application")
                if acad:
                    doc = acad.Documents.Open(dwg_path)
                    doc.SaveAs(dxf_path, 12)  # 12 = DXF format
                    doc.Close()
                    acad.Quit()
                    if os.path.exists(dxf_path):
                        logger.info(f"Successfully converted DWG to DXF using AutoCAD COM")
                        return dxf_path
            except Exception as e:
                logger.warning(f"AutoCAD COM method failed: {e}")

            # If no conversion method works, raise informative error
            raise Exception(
                "DWG to DXF conversion failed. Please install one of the following:\n"
                "1. ODA File Converter (free)\n"
                "2. AutoCAD (with COM support)\n"
                "3. Use DXF files instead of DWG files for testing"
            )

        except Exception as e:
            logger.error(f"Failed to convert DWG to DXF: {str(e)}")
            raise

    def extract_text_entities(self, file_path: str) -> List[TextEntity]:
        """Extract text entities from DWG/DXF file"""
        try:
            # Convert DWG to DXF if necessary
            if file_path.lower().endswith('.dwg'):
                logger.info("Converting DWG to DXF...")
                dxf_path = self.convert_dwg_to_dxf(file_path)
            else:
                dxf_path = file_path

            logger.info(f"Processing file: {dxf_path}")

            # Load DXF file
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            text_entities = []

            # Extract MTEXT entities
            try:
                for mtext in msp.query('MTEXT'):
                    text_entities.append(TextEntity(
                        handle=mtext.dxf.handle,
                        text=mtext.text,
                        entity_type='MTEXT',
                        layer=mtext.dxf.layer,
                        position=mtext.dxf.insert,
                        height=getattr(mtext.dxf, 'char_height', 2.5),
                        style=mtext.dxf.style,
                        rotation=getattr(mtext.dxf, 'rotation', 0),
                        width_factor=getattr(mtext.dxf, 'width', 1),
                        insertion_point=mtext.dxf.insert
                    ))
            except Exception as e:
                logger.warning(f"Error extracting MTEXT entities: {e}")

            # Extract TEXT entities
            try:
                for text in msp.query('TEXT'):
                    text_entities.append(TextEntity(
                        handle=text.dxf.handle,
                        text=text.dxf.text,
                        entity_type='TEXT',
                        layer=text.dxf.layer,
                        position=text.dxf.insert,
                        height=getattr(text.dxf, 'height', 2.5),
                        style=text.dxf.style,
                        rotation=getattr(text.dxf, 'rotation', 0),
                        width_factor=getattr(text.dxf, 'width', 1),
                        insertion_point=text.dxf.insert
                    ))
            except Exception as e:
                logger.warning(f"Error extracting TEXT entities: {e}")

            # Extract DIMENSION text
            try:
                for dim in msp.query('DIMENSION'):
                    if hasattr(dim, 'text') and dim.text:
                        text_entities.append(TextEntity(
                            handle=dim.dxf.handle,
                            text=dim.text,
                            entity_type='DIMENSION',
                            layer=dim.dxf.layer,
                            position=getattr(dim.dxf, 'insert', (0, 0, 0)),
                            height=getattr(dim.dxf, 'height', 2.5),
                            style=getattr(dim.dxf, 'style', 'Standard'),
                            rotation=0,
                            width_factor=1,
                            insertion_point=getattr(dim.dxf, 'insert', (0, 0, 0))
                        ))
            except Exception as e:
                logger.warning(f"Error extracting DIMENSION entities: {e}")

            logger.info(f"Extracted {len(text_entities)} text entities from {file_path}")
            return text_entities

        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            raise

    def replace_text_entities(self, file_path: str, translations: Dict[str, str]) -> str:
        """Replace text entities in DWG/DXF file with translations"""
        try:
            # Convert DWG to DXF if necessary
            if file_path.lower().endswith('.dwg'):
                logger.info("Converting DWG to DXF for text replacement...")
                dxf_path = self.convert_dwg_to_dxf(file_path)
            else:
                dxf_path = file_path

            # Load DXF file
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            # Replace MTEXT entities
            try:
                for mtext in msp.query('MTEXT'):
                    if mtext.dxf.handle in translations:
                        original_text = mtext.text
                        mtext.text = translations[mtext.dxf.handle]
                        logger.info(f"Replaced MTEXT: '{original_text}' -> '{translations[mtext.dxf.handle]}'")
            except Exception as e:
                logger.warning(f"Error replacing MTEXT entities: {e}")

            # Replace TEXT entities
            try:
                for text in msp.query('TEXT'):
                    if text.dxf.handle in translations:
                        original_text = text.dxf.text
                        text.dxf.text = translations[text.dxf.handle]
                        logger.info(f"Replaced TEXT: '{original_text}' -> '{translations[text.dxf.handle]}'")
            except Exception as e:
                logger.warning(f"Error replacing TEXT entities: {e}")

            # Replace DIMENSION text
            try:
                for dim in msp.query('DIMENSION'):
                    if dim.dxf.handle in translations and hasattr(dim, 'text'):
                        original_text = dim.text
                        dim.text = translations[dim.dxf.handle]
                        logger.info(f"Replaced DIMENSION: '{original_text}' -> '{translations[dim.dxf.handle]}'")
            except Exception as e:
                logger.warning(f"Error replacing DIMENSION entities: {e}")

            # Save modified file
            output_path = file_path.rsplit('.', 1)[0] + '_translated.dxf'
            doc.saveas(output_path)

            logger.info(f"Saved translated file to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to replace text in {file_path}: {str(e)}")
            raise

    def get_file_info(self, file_path: str) -> Dict:
        """Get basic information about the DWG/DXF file"""
        try:
            # Convert DWG to DXF if necessary
            if file_path.lower().endswith('.dwg'):
                dxf_path = self.convert_dwg_to_dxf(file_path)
            else:
                dxf_path = file_path

            doc = ezdxf.readfile(dxf_path)

            return {
                'filename': os.path.basename(file_path),
                'format': doc.dxfversion,
                'units': doc.units,
                'layers': [layer.dxf.name for layer in doc.layers],
                'text_styles': [style.dxf.name for style in doc.styles],
                'model_space_entities': len(list(doc.modelspace())),
                'file_size': os.path.getsize(file_path)
            }

        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {str(e)}")
            return {'error': str(e)}