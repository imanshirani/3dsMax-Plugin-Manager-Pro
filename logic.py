import os
import json
import sys
from pymxs import runtime as rt



class PluginManagerLogic:
    def __init__(self):
        
        self.max_version = self._detect_max_version()
        
        self.max_version = self._detect_max_version()
        self.search_paths = [
            fr"C:\Program Files\Autodesk\3ds Max {self.max_version}\Plugins",
            fr"C:\Program Files\Autodesk\3ds Max {self.max_version}\ApplicationPlugins",
            
            os.path.join(os.environ.get('PROGRAMDATA', ''), r"Autodesk\ApplicationPlugins"),
            os.path.join(os.getenv('APPDATA'), r"Autodesk\ApplicationPlugins")
        ]

    def _detect_max_version(self):        
        v_code = rt.maxversion()[0]       
        
        internal_version = v_code // 1000        
        
        actual_year = 1998 + internal_version
        
        print(f"[SYSTEM] Running inside 3ds Max {actual_year}")
        return str(actual_year)
        
        

    def _get_ini_path(self):
        
        user_dir = rt.pathConfig.getDir(rt.name("userSettings"))
        return os.path.join(user_dir, "Plugin.UserSettings.ini")

    def get_all_plugins(self):
        plugins = []
        valid_exts = ('.dlo', '.dlm', '.dlt', '.dle', '.dlr')

        for base_path in self.search_paths:
            if not os.path.exists(base_path): 
                print(f"Path Missing: {base_path}") 
                continue
            
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    low_file = file.lower()
                    if any(low_file.endswith(ext) for ext in valid_exts) or low_file.endswith('.disabled'):
                        
                        
                        if "Program Files" in root:
                            source = "Plugins" 
                        elif "ProgramData" in root:
                            source = "Modern"
                        elif "AppData" in root:
                            source = "User"
                        else:
                            source = "Other"

                        plugins.append({
                            "name": file.replace('.disabled', ''),
                            "path": os.path.join(root, file), 
                            "is_enabled": not low_file.endswith('.disabled'),
                            "source": source
                        })
        return plugins

    def toggle_plugin(self, full_path, enable):
        
        try:
            if enable and full_path.endswith('.disabled'):
                new_path = full_path.replace('.disabled', '')
                os.rename(full_path, new_path)
                return new_path
            elif not enable and not full_path.endswith('.disabled'):
                new_path = full_path + '.disabled'
                os.rename(full_path, new_path)
                return new_path
        except Exception as e:
            print(f"Permission Error: {e}")
        return full_path

    def load_profiles(self):
        if os.path.exists(self.profiles_path):
            with open(self.profiles_path, 'r') as f: return json.load(f)
        return {}

    def save_profile(self, name, active_paths):
        profiles = self.load_profiles()
        profiles[name] = active_paths
        with open(self.profiles_path, 'w') as f: json.dump(profiles, f)

    def save_to_ini(self, plugin_states):
        
        if not os.path.exists(self.ini_path): return
        with open(self.ini_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            line_content = line.strip().lstrip(";")
            match_found = False
            for path, enabled in plugin_states.items():
                if path in line:
                    prefix = "" if enabled else ";"
                    new_lines.append(f"{prefix}{line_content}\n")
                    match_found = True
                    break
            if not match_found:
                new_lines.append(line)

        with open(self.ini_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)