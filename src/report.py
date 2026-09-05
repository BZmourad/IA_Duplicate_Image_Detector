"""
Report generation and export functionality.
"""

import logging
import pandas as pd
from typing import List, Dict
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates reports and exports results."""
    
    def export_to_csv(self, groups: Dict[str, List[dict]], output_path: str):
        """Export results to CSV."""
        try:
            rows = []
            
            for group_type in ["duplicates", "review"]:
                for idx, group in enumerate(groups.get(group_type, []), 1):
                    group_id = f"G{idx:03d}"
                    
                    for image_path in group["images"]:
                        rows.append({
                            "Group ID": group_id,
                            "Image Path": image_path,
                            "Image Filename": os.path.basename(image_path),
                            "Product Similarity": round(group["product_similarity"], 3),
                            "Color Similarity": round(group["color_similarity"], 3),
                            "Confidence": round(group["confidence"], 3),
                            "Status": group["status"]
                        })
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(output_path, index=False)
                logger.info(f"CSV exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def export_to_excel(self, groups: Dict[str, List[dict]], output_path: str, summary: Dict):
        """Export results to Excel with summary sheet."""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Create detailed results sheet
                rows = []
                
                for group_type in ["duplicates", "review"]:
                    for idx, group in enumerate(groups.get(group_type, []), 1):
                        group_id = f"G{idx:03d}"
                        
                        for image_path in group["images"]:
                            rows.append({
                                "Group ID": group_id,
                                "Image Path": image_path,
                                "Image Filename": os.path.basename(image_path),
                                "Product Similarity": round(group["product_similarity"], 3),
                                "Color Similarity": round(group["color_similarity"], 3),
                                "Confidence": round(group["confidence"], 3),
                                "Status": group["status"]
                            })
                
                if rows:
                    df = pd.DataFrame(rows)
                    df.to_excel(writer, sheet_name="Duplicates", index=False)
                
                # Create summary sheet
                summary_data = []
                for key, value in summary.items():
                    summary_data.append({"Metric": key, "Value": value})
                
                if summary_data:
                    df_summary = pd.DataFrame(summary_data)
                    df_summary.to_excel(writer, sheet_name="Summary", index=False)
            
            logger.info(f"Excel exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")