import ezdxf
import os
import tempfile
import subprocess
from typing import List, Dict, Tuple, Optional
import logging
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

class DWGProcessor:
    def __init__(self):
        self.supported_formats = ['.dwg', '.dxf']

    def convert_dwg_to_dxf(self, dwg_path: str) -> str:
        """Convert DWG file to DXF using available converters"""
        try:
            dxf_path = dwg_path.rsplit('.', 1)[0] + '.dxf'

            # Try using LibreDWG (dwg2dxf) if available
            if self._check_command_available("dwg2dxf"):
                result = subprocess.run([
                    "dwg2dxf", "-o", dxf_path, dwg_path
                ], capture_output=True, text=True, timeout=120)

                if result.returncode == 0 and os.path.exists(dxf_path):
                    logger.info("Successfully converted DWG to DXF using LibreDWG")
                    return dxf_path
                else:
                    logger.warning(f"LibreDWG conversion failed: {result.stderr}")

            # Try using ODA File Converter if available (Linux/Windows)
            oda_converter_paths = [
                "ODAFileConverter",
                "/usr/bin/ODAFileConverter",
                "C:\\Program Files\\ODA\\ODAFileConverter\\ODAFileConverter.exe"
            ]

            for converter_path in oda_converter_paths:
                if os.path.exists(converter_path):
                    # Use ODA File Converter
                    output_dir = os.path.dirname(dwg_path)
                    version = "ACAD2018"  # Target version
                    result = subprocess.run([
                        converter_path, output_dir, output_dir, version, "DXF", "0", "1"
                    ], capture_output=True, text=True, timeout=60)

                    if result.returncode == 0 and os.path.exists(dxf_path):
                        logger.info("Successfully converted DWG to DXF using ODA File Converter")
                        return dxf_path

            # Fallback: Try using AutoCAD via COM (Windows only)
            try:
                import win32com.client
                acad = win32com.client.Dispatch("AutoCAD.Application")
                doc = acad.Documents.Open(dwg_path)
                doc.SaveAs(dxf_path, 12)  # 12 = DXF format
                doc.Close()
                acad.Quit()
                logger.info("Successfully converted DWG to DXF using AutoCAD COM")
                return dxf_path
            except:
                pass

            # If no converter is available, try using ezdxf directly
            try:
                import ezdxf
                # Some versions of ezdxf can read DWG files directly
                doc = ezdxf.readfile(dwg_path)
                doc.saveas(dxf_path)
                logger.info("Successfully converted DWG to DXF using ezdxf")
                return dxf_path
            except Exception as ezdxf_error:
                logger.warning(f"ezdxf direct conversion failed: {ezdxf_error}")

            raise Exception("No DWG to DXF conversion method available. Please install LibreDWG (dwg2dxf) or ODA File Converter.")

        except Exception as e:
            logger.error(f"Failed to convert DWG to DXF: {str(e)}")
            raise

    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available in the system PATH"""
        try:
            result = subprocess.run(['which', command], capture_output=True, text=True)
            return result.returncode == 0
        except:
            try:
                # Fallback for Windows
                result = subprocess.run(['where', command], capture_output=True, text=True)
                return result.returncode == 0
            except:
                return False

    def extract_text_entities(self, file_path: str) -> List[TextEntity]:
        """Extract text entities from DWG/DXF file"""
        try:
            # Convert DWG to DXF if necessary
            if file_path.lower().endswith('.dwg'):
                dxf_path = self.convert_dwg_to_dxf(file_path)
            else:
                dxf_path = file_path

            # Load DXF file
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            text_entities = []

            # Extract MTEXT entities
            for mtext in msp.query('MTEXT'):
                text_entities.append(TextEntity(
                    handle=mtext.dxf.handle,
                    text=mtext.text,
                    entity_type='MTEXT',
                    layer=mtext.dxf.layer,
                    position=mtext.dxf.insert,
                    height=mtext.dxf.char_height,
                    style=mtext.dxf.style,
                    rotation=mtext.dxf.rotation if hasattr(mtext.dxf, 'rotation') else 0,
                    width_factor=mtext.dxf.width if hasattr(mtext.dxf, 'width') else 1,
                    insertion_point=mtext.dxf.insert
                ))

            # Extract TEXT entities
            for text in msp.query('TEXT'):
                text_entities.append(TextEntity(
                    handle=text.dxf.handle,
                    text=text.dxf.text,
                    entity_type='TEXT',
                    layer=text.dxf.layer,
                    position=text.dxf.insert,
                    height=text.dxf.height,
                    style=text.dxf.style,
                    rotation=text.dxf.rotation if hasattr(text.dxf, 'rotation') else 0,
                    width_factor=text.dxf.width if hasattr(text.dxf, 'width') else 1,
                    insertion_point=text.dxf.insert
                ))

            # Extract DIMENSION text
            for dim in msp.query('DIMENSION'):
                if hasattr(dim, 'text') and dim.text:
                    text_entities.append(TextEntity(
                        handle=dim.dxf.handle,
                        text=dim.text,
                        entity_type='DIMENSION',
                        layer=dim.dxf.layer,
                        position=dim.dxf.insert if hasattr(dim.dxf, 'insert') else (0, 0, 0),
                        height=getattr(dim.dxf, 'height', 2.5),
                        style=getattr(dim.dxf, 'style', 'Standard'),
                        rotation=0,
                        width_factor=1,
                        insertion_point=dim.dxf.insert if hasattr(dim.dxf, 'insert') else (0, 0, 0)
                    ))

            # Extract ATTRIB entities (block attributes)
            for attrib in msp.query('ATTRIB'):
                text_entities.append(TextEntity(
                    handle=attrib.dxf.handle,
                    text=attrib.dxf.text,
                    entity_type='ATTRIB',
                    layer=attrib.dxf.layer,
                    position=attrib.dxf.insert,
                    height=attrib.dxf.height,
                    style=attrib.dxf.style,
                    rotation=0,
                    width_factor=1,
                    insertion_point=attrib.dxf.insert
                ))

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
                dxf_path = self.convert_dwg_to_dxf(file_path)
            else:
                dxf_path = file_path

            # Load DXF file
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            # Replace MTEXT entities
            for mtext in msp.query('MTEXT'):
                if mtext.dxf.handle in translations:
                    mtext.text = translations[mtext.dxf.handle]

            # Replace TEXT entities
            for text in msp.query('TEXT'):
                if text.dxf.handle in translations:
                    text.dxf.text = translations[text.dxf.handle]

            # Replace DIMENSION text
            for dim in msp.query('DIMENSION'):
                if dim.dxf.handle in translations and hasattr(dim, 'text'):
                    dim.text = translations[dim.dxf.handle]

            # Replace ATTRIB entities
            for attrib in msp.query('ATTRIB'):
                if attrib.dxf.handle in translations:
                    attrib.dxf.text = translations[attrib.dxf.handle]

            # Save modified file
            output_path = file_path.rsplit('.', 1)[0] + '_translated.dxf'
            doc.saveas(output_path)

            logger.info(f"Saved translated file to {output_path}")
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