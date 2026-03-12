import logging
from pathlib import Path

def setup_logger(log_file: Path):
    logger = logging.getLogger("mangoAgent")
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    return logger
