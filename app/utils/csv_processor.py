import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def process_csv_file(file) -> List[Dict[str, Any]]:
    """Обрабатывает CSV файл и возвращает список словарей с данными"""
    try:
        df = pd.read_csv(file.file)

        data = df.where(pd.notnull(df), None).to_dict(orient='records')

        logger.debug(f"Processed {len(data)} records from CSV")
        return data
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}")
        raise