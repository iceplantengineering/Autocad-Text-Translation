import ezdxf
import dxfgrabber
import os
import subprocess
import tempfile
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import shutil

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

class EnhancedDWGProcessor:
    def __init__(self):
        self.supported_formats = ['.dwg', '.dxf']
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Enhanced DWG Processor initialized with temp dir: {self.temp_dir}")

    def __del__(self):
        # Clean up temporary directory
        try:
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temp dir: {self.temp_dir}")
        except:
            pass

    def convert_dwg_to_dxf(self, dwg_path: str) -> str:
        """Convert DWG to DXF using multiple methods"""
        try:
            dxf_path = dwg_path.rsplit('.', 1)[0] + '_converted.dxf'

            # If it's already a DXF file, return as is
            if dwg_path.lower().endswith('.dxf'):
                return dwg_path

            logger.info(f"Converting DWG to DXF: {dwg_path} -> {dxf_path}")

            # Method 1: Try using ODA File Converter (if available)
            if self._try_oda_converter(dwg_path, dxf_path):
                logger.info("Successfully converted using ODA File Converter")
                return dxf_path

            # Method 2: Try using Teigha Converter (if available)
            if self._try_teigha_converter(dwg_path, dxf_path):
                logger.info("Successfully converted using Teigha Converter")
                return dxf_path

            # Method 3: Try using AutoCAD (if available)
            if self._try_autocad_conversion(dwg_path, dxf_path):
                logger.info("Successfully converted using AutoCAD")
                return dxf_path

            # Method 4: Try using LibreCAD (if available)
            if self._try_librecad_conversion(dwg_path, dxf_path):
                logger.info("Successfully converted using LibreCAD")
                return dxf_path

            # Method 5: Try using online conversion service
            if self._try_online_conversion(dwg_path, dxf_path):
                logger.info("Successfully converted using online service")
                return dxf_path

            logger.error("All DWG to DXF conversion methods failed")
            raise Exception("DWG変換ツールがインストールされていません。setupガイドに従ってODA File Converterなどをインストールしてください。")

        except Exception as e:
            logger.error(f"Error converting DWG to DXF: {e}")
            raise

    def _try_oda_converter(self, dwg_path: str, dxf_path: str) -> bool:
        """Try converting using ODA File Converter"""
        try:
            oda_paths = [
                "ODAFileConverter",
                r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
                r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
                r"C:\Program Files\ODA\ODAFileConverter_4.3.2\ODAFileConverter.exe"
            ]

            for oda_path in oda_paths:
                if os.path.exists(oda_path):
                    try:
                        output_dir = os.path.dirname(dxf_path)
                        result = subprocess.run([
                            oda_path, output_dir, output_dir, "ACAD2018", "DXF", "0", "1"
                        ], capture_output=True, text=True, timeout=120)

                        if result.returncode == 0:
                            # Check if converted file exists
                            converted_dxf = dwg_path.rsplit('.', 1)[0] + '.dxf'
                            if os.path.exists(converted_dxf):
                                shutil.move(converted_dxf, dxf_path)
                                return True
                    except Exception as e:
                        logger.warning(f"ODA converter failed: {e}")

            return False
        except Exception as e:
            logger.warning(f"ODA converter error: {e}")
            return False

    def _try_teigha_converter(self, dwg_path: str, dxf_path: str) -> bool:
        """Try converting using Teigha Converter"""
        try:
            teigha_paths = [
                "TeighaFileConverter",
                r"C:\Program Files\ODA\Teigha File Converter\TeighaFileConverter.exe",
                r"C:\Program Files (x86)\ODA\Teigha File Converter\TeighaFileConverter.exe"
            ]

            for teigha_path in teigha_paths:
                if os.path.exists(teigha_path):
                    try:
                        output_dir = os.path.dirname(dxf_path)
                        result = subprocess.run([
                            teigha_path, output_dir, output_dir, "ACAD2018", "DXF", "0", "1"
                        ], capture_output=True, text=True, timeout=120)

                        if result.returncode == 0:
                            converted_dxf = dwg_path.rsplit('.', 1)[0] + '.dxf'
                            if os.path.exists(converted_dxf):
                                shutil.move(converted_dxf, dxf_path)
                                return True
                    except Exception as e:
                        logger.warning(f"Teigha converter failed: {e}")

            return False
        except Exception as e:
            logger.warning(f"Teigha converter error: {e}")
            return False

    def _try_autocad_conversion(self, dwg_path: str, dxf_path: str) -> bool:
        """Try converting using AutoCAD COM automation"""
        try:
            import comtypes.client

            # Try to get AutoCAD application
            acad = comtypes.client.GetActiveObject("AutoCAD.Application")
            if acad:
                try:
                    # Open the DWG file
                    doc = acad.Documents.Open(dwg_path)

                    # Save as DXF
                    doc.SaveAs(dxf_path, 21)  # 21 = DXF format

                    # Close the document
                    doc.Close()

                    return True
                except Exception as e:
                    logger.warning(f"AutoCAD conversion failed: {e}")
                    try:
                        doc.Close()
                    except:
                        pass

            return False
        except Exception as e:
            logger.warning(f"AutoCAD not available or error: {e}")
            return False

    def _try_librecad_conversion(self, dwg_path: str, dxf_path: str) -> bool:
        """Try converting using LibreCAD command line"""
        try:
            librecad_paths = [
                "librecad",
                r"C:\Program Files\LibreCAD\librecad.exe",
                r"C:\Program Files (x86)\LibreCAD\librecad.exe"
            ]

            for librecad_path in librecad_paths:
                if os.path.exists(librecad_path):
                    try:
                        # LibreCAD command line conversion (if supported)
                        result = subprocess.run([
                            librecad_path, "-x", dxf_path, dwg_path
                        ], capture_output=True, text=True, timeout=120)

                        if result.returncode == 0 and os.path.exists(dxf_path):
                            return True
                    except Exception as e:
                        logger.warning(f"LibreCAD conversion failed: {e}")

            return False
        except Exception as e:
            logger.warning(f"LibreCAD converter error: {e}")
            return False

    def _try_online_conversion(self, dwg_path: str, dxf_path: str) -> bool:
        """Try using online conversion service (basic implementation)"""
        try:
            # This is a placeholder for online conversion
            # In a real implementation, you would use an API service
            logger.warning("Online conversion not implemented")
            return False
        except Exception as e:
            logger.warning(f"Online conversion error: {e}")
            return False

    def extract_text_entities(self, file_path: str) -> List[TextEntity]:
        """Extract text entities from DWG/DXF file"""
        try:
            logger.info(f"Extracting text entities from: {file_path}")

            # Convert DWG to DXF if necessary
            if file_path.lower().endswith('.dwg'):
                dxf_path = self.convert_dwg_to_dxf(file_path)
            else:
                dxf_path = file_path

            # Try using ezdxf first
            try:
                return self._extract_with_ezdxf(dxf_path)
            except Exception as e:
                logger.warning(f"ezdxf extraction failed: {e}")

            # Fallback to dxfgrabber
            try:
                return self._extract_with_dxfgrabber(dxf_path)
            except Exception as e:
                logger.warning(f"dxfgrabber extraction failed: {e}")

            raise Exception("Both extraction methods failed")

        except Exception as e:
            logger.error(f"Error extracting text entities: {e}")
            raise

    def _extract_with_ezdxf(self, dxf_path: str) -> List[TextEntity]:
        """Extract text entities using ezdxf"""
        try:
            doc = ezdxf.readfile(dxf_path)
            entities = []

            # Extract from model space
            msp = doc.modelspace()

            # TEXT entities
            for entity in msp.query('TEXT'):
                try:
                    text_entity = TextEntity(
                        handle=entity.dxf.handle,
                        text=entity.dxf.text,
                        entity_type='TEXT',
                        layer=entity.dxf.layer,
                        position=(entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z),
                        height=entity.dxf.height,
                        style=entity.dxf.style,
                        rotation=entity.dxf.rotation,
                        width_factor=entity.dxf.width,
                        insertion_point=(entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z)
                    )
                    entities.append(text_entity)
                except Exception as e:
                    logger.warning(f"Error processing TEXT entity: {e}")

            # MTEXT entities
            for entity in msp.query('MTEXT'):
                try:
                    text_entity = TextEntity(
                        handle=entity.dxf.handle,
                        text=entity.text,
                        entity_type='MTEXT',
                        layer=entity.dxf.layer,
                        position=(entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z),
                        height=entity.dxf.char_height,
                        style=entity.dxf.style,
                        rotation=entity.dxf.rotation,
                        width_factor=1.0,
                        insertion_point=(entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z)
                    )
                    entities.append(text_entity)
                except Exception as e:
                    logger.warning(f"Error processing MTEXT entity: {e}")

            logger.info(f"Extracted {len(entities)} text entities using ezdxf")
            return entities

        except Exception as e:
            logger.error(f"Error with ezdxf extraction: {e}")
            raise

    def _extract_with_dxfgrabber(self, dxf_path: str) -> List[TextEntity]:
        """Extract text entities using dxfgrabber"""
        try:
            dxf = dxfgrabber.readfile(dxf_path)
            entities = []

            for entity in dxf.entities:
                try:
                    if entity.dxftype == 'TEXT':
                        text_entity = TextEntity(
                            handle=getattr(entity, 'handle', str(id(entity))),
                            text=entity.text,
                            entity_type='TEXT',
                            layer=entity.layer,
                            position=(entity.insert[0], entity.insert[1], entity.insert[2] if len(entity.insert) > 2 else 0.0),
                            height=entity.height,
                            style=getattr(entity, 'style', 'Standard'),
                            rotation=getattr(entity, 'rotation', 0.0),
                            width_factor=getattr(entity, 'width_factor', 1.0),
                            insertion_point=(entity.insert[0], entity.insert[1], entity.insert[2] if len(entity.insert) > 2 else 0.0)
                        )
                        entities.append(text_entity)
                    elif entity.dxftype == 'MTEXT':
                        text_entity = TextEntity(
                            handle=getattr(entity, 'handle', str(id(entity))),
                            text=entity.text,
                            entity_type='MTEXT',
                            layer=entity.layer,
                            position=(entity.insert[0], entity.insert[1], entity.insert[2] if len(entity.insert) > 2 else 0.0),
                            height=entity.char_height,
                            style=getattr(entity, 'style', 'Standard'),
                            rotation=getattr(entity, 'rotation', 0.0),
                            width_factor=1.0,
                            insertion_point=(entity.insert[0], entity.insert[1], entity.insert[2] if len(entity.insert) > 2 else 0.0)
                        )
                        entities.append(text_entity)
                except Exception as e:
                    logger.warning(f"Error processing {entity.dxftype} entity: {e}")

            logger.info(f"Extracted {len(entities)} text entities using dxfgrabber")
            return entities

        except Exception as e:
            logger.error(f"Error with dxfgrabber extraction: {e}")
            raise

    def replace_text_entities(self, file_path: str, replacements: Dict[str, str]) -> str:
        """Replace text entities in DWG/DXF file"""
        try:
            logger.info(f"Replacing text entities in: {file_path}")

            # Convert DWG to DXF if necessary
            if file_path.lower().endswith('.dwg'):
                dxf_path = self.convert_dwg_to_dxf(file_path)
            else:
                dxf_path = file_path

            # Create output file
            output_path = file_path.rsplit('.', 1)[0] + '_translated.dxf'

            # Use ezdxf for replacement
            try:
                return self._replace_with_ezdxf(dxf_path, output_path, replacements)
            except Exception as e:
                logger.warning(f"ezdxf replacement failed: {e}")

            raise Exception("Text replacement failed")

        except Exception as e:
            logger.error(f"Error replacing text entities: {e}")
            raise

    def _replace_with_ezdxf(self, dxf_path: str, output_path: str, replacements: Dict[str, str]) -> str:
        """Replace text using ezdxf"""
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            replaced_count = 0

            # Replace TEXT entities
            for entity in msp.query('TEXT'):
                if entity.dxf.handle in replacements:
                    entity.dxf.text = replacements[entity.dxf.handle]
                    replaced_count += 1
                    logger.info(f"Replaced TEXT entity {entity.dxf.handle}: '{replacements[entity.dxf.handle]}'")

            # Replace MTEXT entities
            for entity in msp.query('MTEXT'):
                if entity.dxf.handle in replacements:
                    entity.text = replacements[entity.dxf.handle]
                    replaced_count += 1
                    logger.info(f"Replaced MTEXT entity {entity.dxf.handle}: '{replacements[entity.dxf.handle]}'")

            # Save the modified document
            doc.saveas(output_path)

            logger.info(f"Successfully replaced {replaced_count} text entities")
            return output_path

        except Exception as e:
            logger.error(f"Error with ezdxf replacement: {e}")
            raise

    def get_file_info(self, file_path: str) -> Dict:
        """Get information about the CAD file"""
        try:
            if file_path.lower().endswith('.dwg'):
                dxf_path = self.convert_dwg_to_dxf(file_path)
            else:
                dxf_path = file_path

            # Try to get file info using ezdxf
            try:
                doc = ezdxf.readfile(dxf_path)
                return {
                    'format': 'DWG' if file_path.lower().endswith('.dwg') else 'DXF',
                    'version': doc.dxfversion,
                    'layers': len(doc.layers),
                    'entities': len(list(doc.modelspace())),
                    'units': doc.units
                }
            except Exception as e:
                logger.warning(f"Could not get file info with ezdxf: {e}")

            # Fallback using dxfgrabber
            try:
                dxf = dxfgrabber.readfile(dxf_path)
                return {
                    'format': 'DWG' if file_path.lower().endswith('.dwg') else 'DXF',
                    'version': getattr(dxf, 'version', 'Unknown'),
                    'layers': len(dxf.layers),
                    'entities': len(dxf.entities),
                    'units': getattr(dxf, 'units', 'Unknown')
                }
            except Exception as e:
                logger.warning(f"Could not get file info with dxfgrabber: {e}")

            return {
                'format': 'DWG' if file_path.lower().endswith('.dwg') else 'DXF',
                'version': 'Unknown',
                'layers': 0,
                'entities': 0,
                'units': 'Unknown'
            }

        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {
                'format': 'Unknown',
                'version': 'Unknown',
                'layers': 0,
                'entities': 0,
                'units': 'Unknown'
            }