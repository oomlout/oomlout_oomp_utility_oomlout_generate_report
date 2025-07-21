import os
import yaml



parts = {}
configuration = {}

def get_configuration(**kwargs):
    global configuration
    folder = kwargs.get("folder", f"{os.path.dirname(__file__)}/parts")
    #first try a configuration fodler one up from the parts folder supplied
    folder = folder.replace("\\","/")
    folder = folder.replace("parts","")
    folder_configuration = "configuration"
    folder_configuration = os.path.join(folder, folder_configuration)
    file_configuration = os.path.join(folder_configuration, "oomlout_oomp_utility_oomlout_generate_report_configuration.yaml")
    if not os.path.exists(file_configuration):    
        folder_configuration = "configuration"
        folder_configuration = os.path.join(os.path.dirname(__file__), folder_configuration)
        file_configuration = os.path.join(folder_configuration, "configuration.yaml")
        #check if exists
        if not os.path.exists(file_configuration):
            print(f"no configuration.yaml found in {folder_configuration} using default")
            file_configuration = os.path.join(folder_configuration, "configuration_default.yaml")



    #import configuration

    with open(file_configuration, 'r') as stream:
        try:
            configuration = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:   
            print(exc)
    kwargs["configuration"] = configuration


def main(**kwargs):
    get_configuration(**kwargs)
    folder = kwargs.get("folder", f"{os.path.dirname(__file__)}/parts")
    folder = folder.replace("\\","/")
    
    filt = kwargs.get("filter", "")

    kwargs["configuration"] = configuration
    print(f"running utility oomlout_oomp_utility_oomlout_generate_report: {folder}")
    if filt == "":
        create_recursive(**kwargs) ## load all parts into parts dictionary
        #all parts loaded now make csv
        print(f"creating csv")
        create_csv(**kwargs)
        create_md(**kwargs)
    else:
        print(f"******  skipping because filter is present  ******")
        

def create_csv(**kwargs):
    import csv
    folder = kwargs.get("folder", os.path.dirname(__file__))
    folder = folder.replace("\\","/").replace("parts","")
    
    
    outputs = configuration.get("outputs", {})
    for output in outputs:
        name = output.get("name", "report")
        print(f"creating csv for {name}")
        file_csv = os.path.join(folder, f"report/{name}.csv")
        #create folder if it does not exist
        os.makedirs(os.path.dirname(file_csv), exist_ok=True)
        #go through parts and get all unique keys
        keys = output.get("keys", [])
        if keys == []:
            keys = set()
            for key in parts:
                for k in parts[key]:
                    keys.add(k)        
        with open(file_csv, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["id"] + list(keys))
            for key in parts:
                row = [key]
                for k in keys:
                    row.append(parts[key].get(k, ""))
                writer.writerow(row)
        
def create_md(**kwargs):
    folder = kwargs.get("folder", os.path.dirname(__file__))
    folder = folder.replace("\\","/").replace("parts","")
    outputs = configuration.get("outputs", {})
    for output in outputs:
        name = output.get("name", "report")
        print(f"creating md for {name}")
        file_md = os.path.join(folder, f"report/{name}.md")
        #create folder if it does not exist
        os.makedirs(os.path.dirname(file_md), exist_ok=True)
        with open(file_md, 'w') as file:
            mode = "normal"
            mode = "table"
            if mode == "normal":
                for key in parts:
                    file.write(f"## {key}\n")
                    for k in parts[key]:
                        file.write(f"### {k}\n")
                        file.write(f"{parts[key][k]}\n")
                    file.write("\n")
            if mode == "table":
                keys = output.get("keys", [])
                if keys == []:
                    keys = set()
                    for key in parts:
                        for k in parts[key]:
                            keys.add(k)        
                file.write("| id |")
                for key in keys:
                    file.write(f" {key} |")
                file.write("\n")
                file.write("|---|")
                for key in keys:
                    file.write("---|")
                file.write("\n")
                for key in parts:
                    file.write(f"| {key} |")
                    for k in keys:
                        file.write(f" {parts[key].get(k, '')} |")
                    file.write("\n")
                file.write("\n")

def create_recursive(**kwargs):
    folder = kwargs.get("folder", os.path.dirname(__file__))
    kwargs["folder"] = folder
    filter = kwargs.get("filter", "")
    #if folder exists
    if os.path.exists(folder):        
        count = 0
        for item in os.listdir(folder):
            if filter in item:
                directory_absolute = os.path.join(folder, item)
                directory_absolute = directory_absolute.replace("\\","/")
                if os.path.isdir(directory_absolute):
                    #if working.yaml exists in the folder
                    if os.path.exists(os.path.join(directory_absolute, "working.yaml")):
                        kwargs["directory_absolute"] = directory_absolute
                        create(**kwargs)
                        count += 1
                        if count % 100 == 0:
                            break
                            print(f"    {count} parts loaded")
    else:
        print(f"no folder found at {folder}")

def create(**kwargs):
    directory_absolute = kwargs.get("directory_absolute", os.getcwd())    
    kwargs["directory_absolute"] = directory_absolute    
    generate(**kwargs)
    

def generate(**kwargs):    
    directory_absolute = kwargs.get("directory_absolute")
    file_absolute_working_yaml = os.path.join(directory_absolute, "working.yaml")
    #load yaml file
    with open(file_absolute_working_yaml, 'r') as stream:
        try:
            working = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:   
            print(exc)
    pass
    id = working.get("id", "no_id")
    parts[id] = working

if __name__ == '__main__':
    #folder is the path it was launched from
    
    kwargs = {}
    folder = os.path.dirname(__file__)
    #folder = "C:/gh/oomlout_oomp_builder/parts"
    folder = "C:/gh/oomlout_oomp_part_generation_version_1/parts"
    #folder = "C:/gh/oomlout_oobb_version_4/things"
    #folder = "C:/gh/oomlout_oomp_current_version"
    kwargs["folder"] = folder
    overwrite = False
    kwargs["overwrite"] = overwrite
    main(**kwargs)