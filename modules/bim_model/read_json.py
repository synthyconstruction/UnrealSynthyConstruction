import unreal

# TODO:
# This function is meant for manipulating a profile.json of all parsed information from DataSmith BIM model. Modifications need to be made so it calls the right variables, and gets everything it needs passed when called from the main.py

def load_json_profile():
    file_path = PROFILE_PATH + "profile.json"
    with open(file_path, 'r') as f:
        data = json.load(f)
        for obj in data:
            name = obj['name']
            if name in object_to_ignore:
                continue

            # get all the light objects from the project
            # keep the name of the light source object unique so that other unwanted objects don't get added
            if "light_source" in name.lower() or "lightsource" in name.lower():
                lighting_objects.append(name)  # if the object is a lighting object then it to the list

            try:
                if ("floor" in name.lower() or "floor" in obj['Element_Category']) and sum(obj['bound']) != 0:
                    floor_obj_names.append(name)  # if the object has "floor" in it then add it to the floor obj names
            except Exception as e:
                # not handled (don't care if something doesn't make it to floor obj)
                pass
            object_names.append(name)
            object_dict[name] = BIM_Object(name, obj['color'], obj['position'], obj['rotation'], obj['bound'])
            # print((k, v))

#