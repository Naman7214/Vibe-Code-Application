import os
import json
import glob
from typing import List, Dict, Any

from backend.app.utils.logger import loggers

def save_individual_screens(screens: List[Dict[str, Any]], dir_path: str, base_file_name: str) -> List[str]:
        """
        Save each screen individually as separate JSON files
        
        :param screens: List of screen dictionaries
        :param base_file_name: Base name for the files
        :return: List of file paths where screens were saved
        """
        file_paths = []
        
        os.makedirs(dir_path, exist_ok=True)
        print(f"Saving screens to {dir_path}")
        
        for index, screen in enumerate(screens):
            try:
                    
                screen_id = screen.get('id', f'{index + 1}')
                screen_id = screen_id.replace("-", "_")
                file_name = f"{base_file_name}_{screen_id}.json"
                file_path = os.path.join(dir_path, file_name)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(screen, f, indent=2, ensure_ascii=False)
                
                file_paths.append(file_path)
                loggers["screen_generation"].info(f"Successfully saved screen '{screen_id}' to {file_path}")
                
            except Exception as e:
                loggers["screen_generation"].error(f"Failed to save screen {index + 1}: {str(e)}")
                continue
        
        return file_paths
    
def load_screens_from_directory(screens_dir: str) -> List[Dict[str, Any]]:
        """Load all screen JSON files from the specified directory and combine them into a list"""
        
        if not os.path.exists(screens_dir):
            raise FileNotFoundError(f"Directory not found: {screens_dir}")
        
        if not os.path.isdir(screens_dir):
            raise ValueError(f"Path is not a directory: {screens_dir}")
        
        json_files = glob.glob(os.path.join(screens_dir, "*.json"))
        
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in directory: {screens_dir}")
        
        screens = []
        
        for json_file in json_files:  # Sort for consistent ordering
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    screen_data = json.load(f)
                    
                if isinstance(screen_data, dict):
                    screens.append(screen_data)
                    loggers["navigation_context"].info(f"📄 Loaded screen from {os.path.basename(json_file)}")
                else:
                    loggers["navigation_context"].warning(f"⚠️  Skipping {os.path.basename(json_file)}: not a JSON object")
                    
            except json.JSONDecodeError as e:
                loggers["navigation_context"].error(f"❌ Error parsing JSON file {os.path.basename(json_file)}: {str(e)}")
                raise json.JSONDecodeError(f"Invalid JSON in file {json_file}: {str(e)}", "", 0)
            except Exception as e:
                loggers["navigation_context"].error(f"❌ Error reading file {os.path.basename(json_file)}: {str(e)}")
                raise Exception(f"Error reading file {json_file}: {str(e)}")
        
        if not screens:
            raise ValueError(f"No valid screen objects found in directory: {screens_dir}")
        
        loggers["navigation_context"].info(f"📊 Successfully loaded {len(screens)} screen(s) from {len(json_files)} file(s)")
        
        return screens 