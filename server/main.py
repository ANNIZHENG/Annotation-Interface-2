import uuid
from sqlalchemy import *
from sqlalchemy.sql import *
from datetime import datetime
from flask import *
from db_tables import ses,eng,Survey,Interaction,Confirmation,Annotation,Location
from random import randrange
app = Flask(__name__,static_folder="../templates",template_folder="..")


# home() directs user to the starter frontend page (the consent form page)
# it also checks if enough annotations are collected

@app.route('/')
def home():
    result = eng.execute('''select num_annotation from "Recording" order by num_annotation asc limit 1''')
    for r in result:
        least_annotation = int(dict(r)['num_annotation'])
        if (least_annotation >= 3):
            return render_template('/templates/interface/finish.html')
        else:
            return render_template('/templates/index.html')

# start() receives AJAX request from the frontend if that user agrees the consent form
# once the request is received, it gives each user a survey id

@app.route('/annotation_interface', methods=['GET', 'POST'])
def start():
    survey_id = uuid.uuid4()
    data = request.json
    timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)
    entry = Survey(survey_id, timestamp)
    ses.add(entry)
    ses.commit()
    return str(survey_id)

# interaction() receives AJAX request from the frontend to record user interactions
# types of interaction: "agree consent", "play audio", "azimuth", "elevation", etc.

@app.route('/interaction', methods=['GET', 'POST'])
def interaction():
    if request.method == 'POST':
        data = request.json
        action_type = data['action_type']
        value = data['value']
        survey_id = data['survey_id']
        practice = bool(int(data['practice']))
        timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)
        entry = Interaction(survey_id,action_type,value,timestamp,practice)
        ses.add(entry)
        ses.commit()
    return 'success'

# interaction() receives AJAX request from the frontend to record the annotated azimuths and elevations
# those data would be pushed to the Location table and Annotation table
# interaction() also records the "submit annotation" action 
# and pushed the data into the Interaction table
# this method is triggered when the "SUBMIT" button is clicked, 
# after a user clicks the button, it would direct him/her to the Confirmation page

@app.route('/next', methods=['GET', 'POST'])
def next():
    if request.method == 'POST':
        data = request.json
        recording_name = data['recording_name']
        survey_id = data['survey_id']

        if (data['vertical'] == 2): # practice round
            vertical = None
            exec = '''select id from "Recording" where recording_name = ''' + "'" + recording_name + "' and vertical is null"
        else:
            vertical = bool(data['vertical'])
            exec = '''select id from "Recording" where recording_name = ''' + "'" + recording_name + "' and vertical is " + str(vertical)

        recording_id = -1
        result_recording_id = eng.execute(exec)
        for r in result_recording_id:
            recording_id = int(dict(r)['id'])

        source_count = data['source_count']
        user_note = data['user_note']
        practice = bool(int(data['practice']))

        timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)
        entry = Interaction(survey_id,"submit annotation", None,timestamp,practice)
        ses.add(entry)
        ses.commit()

        entry1 = Annotation(survey_id,recording_id,source_count,user_note,practice,vertical)
        ses.add(entry1)
        ses.commit()

        azimuth_list = data['azimuth']
        elevation_list = data['elevation']

        json_index = 0
        index = 0
        while (index < len(azimuth_list)):
            if (azimuth_list[index] != None):
                entry2 = Location(survey_id, azimuth_list[index], elevation_list[index], index+1, practice)
                ses.add(entry2)
                ses.commit()
                json_index += 1
            index += 1
        
        result = eng.execute('''select id from "Annotation" where survey_id = ''' + "'" + survey_id + "' order by id desc limit 1")

        for r in result:
            annotation_id = str(dict(r)['id'])
        
        eng.execute('''update "Interaction" set annotation_id = ''' + "'" + annotation_id + "' where annotation_id = '" + survey_id + "'")
        eng.execute('''update "Location" set annotation_id = ''' + "'" + annotation_id + "' where annotation_id = '" + survey_id + "'")

    return 'success'

# select_recording() receives AJAX request from the frontend to randomly select a recording

@app.route('/select_recording', methods=['GET', 'POST'])
def select_recording():
    while (True):
        # know the recording level to be annotated
        all_ids = None
        data = request.json
        recording_level = int(data['recording_level'])
        annotated_recording_list = data['annotated_recording_list']

        # id of recordings that are available to be annotated
        if (recording_level == 1 or recording_level == 2):
            # level 1
            # all_ids = [15,7,6,1,12,14,5,16,2,3,9,112,105,108,111,110,99,97,98,2002,2000,101,102,103,2044,2050]
            all_ids = [112,105,108,111,110,99,97,98,101,102,103,2050]
        elif (recording_level == 3 or recording_level == 4):
            # level 2
            # all_ids = [18,17,116,114,124,119,113,2003,2004,126,28,20,2005,31,2032,2034,127,30,128,23,32,2006,2033,2054,2053,2056,2082]
            all_ids = [116,114,124,119,113,126,127,128,2054,2053,2056,2082]
        elif (recording_level == 5 or recording_level == 6):
            # level 3
            # all_ids = [37,131,38,48,44,138,2035,2007,42,143,133,35,130,36,132,144,34,47,134,140,2057,2084,2045,2097]
            all_ids = [131,138,143,133,130,132,144,134,140,2057,2084,2097]
        elif (recording_level == 7 or recording_level == 8):
            # level 4
            # all_ids = [2014,50,2038,2011,2012,160,2009,52,2013,64,148,146,2037,62,2036,158,2063,2086,2095,2092,2059,2062,2046,2085,2064]
            all_ids = [160,148,146,158,2063,2086,2095,2092,2059,2062,2085,2064]
        elif (recording_level == 9 or recording_level == 10):
            # level 5
            # all_ids = [2039,2018,2019,2041,2020,170,2015,74,167,71,70,169,73,2016,2040,2021,166,2069,2093,2096,2072,2071,2066,2047,2088,2022,2068]
            all_ids = [170,167,169,166,2069,2093,2096,2072,2071,2066,2088,2068]
        elif (recording_level == 11 or recording_level == 12):
            # level 6
            # all_ids = [95,86,178,2024,2023,2026,84,182,2030,2025,2028,191,180,2029,82,2076,2043,2074,2048,2089,2090,2075,2078,2042,2049,2079,2099]
            all_ids = [178,182,191,180,2076,2074,2089,2090,2075,2078,2079,2099]

        recording = all_ids[randrange(len(all_ids))]
        
        result = eng.execute('''select num_annotation, recording_name from "Recording" where id = ''' + str(recording))

        for r in result:
            if ((int(dict(r)['num_annotation']) < 3) and (recording not in annotated_recording_list)):
                vertical = 0
                return "{" + '''"recording_name":{"0":''' + '"' + str(dict(r)['recording_name']) + '"' + "}," + '''"vertical":{"0":''' + str(vertical) + "}," + '''"id":{"0":''' + str(recording) + "}" + "}"
            else:
                break

# select_recording() receives AJAX request from the frontend to update the Confirmation table
# It also updates the recording id, the folder name, and the completed status of the Survey table
# which indicates what recording have the user done, and if the user completes the task
# This method is triggered when the "SUBMIT" button is clicked on Confirmation page

@app.route('/submit_confirmation', methods=['GET', 'POST'])
def submit_confirmation():
    if (request.method == 'POST'):
        data = request.json
        recording_name = data['recording_name']
        source_id = data['source_id'].split(',')
        location_id = data['location_id'].split(',')
        survey_id = str(data['survey_id'])
        annotated_recording_list = data['annotated_recording_list']

        # set up the variable first
        vertical = None
        vertical_exec = "null"
        practice = True
        if (recording_name == 'sources_3_recording_19.wav' or recording_name == 'sources_3_recording_130.wav' or recording_name == 'sources_3_recording_160.wav' or recording_name == 'sources_3_recording_57.wav' or recording_name == 'sources_3_recording_150.wav'):
            vertical = None
            vertical_exec = "null"
            practice = True
        else:
            vertical = bool(data['vertical'])
            vertical_exec = str(vertical)
            practice = False
        
        recording_name = data['recording_name']
        result_recording_id = eng.execute('''select id from "Recording" where recording_name = ''' + "'" + recording_name + "' and vertical is " + vertical_exec)

        for r in result_recording_id:
            recording_id = int(dict(r)['id'])

        for i in range (len(source_id)):
            if (i >= len(location_id)):
                entry = Confirmation(recording_id, source_id[i], None, survey_id, practice)
            else:
                if (location_id[i] != 'undefined'):
                    entry = Confirmation(recording_id, source_id[i], location_id[i], survey_id, practice)
                else:
                    entry = Confirmation(recording_id, source_id[i], None, survey_id, practice)
            ses.add(entry)
            ses.commit()

        result = eng.execute('''select id from "Annotation" where survey_id = ''' + "'" + survey_id + "' order by id desc limit 1")

        for r in result:
            annotation_id = str(dict(r)['id'])
        
        eng.execute('''update "Confirmation" set annotation_id = ''' + "'" + annotation_id + "' where annotation_id = '" + survey_id + "'")

        timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)
        entry1 = Interaction(survey_id,"submit confirmation", None, timestamp, practice)
        ses.add(entry1)
        ses.commit()

        eng.execute('''update "Interaction" set annotation_id = ''' + "'" + annotation_id + "' where annotation_id = '" + survey_id + "'")

        if (not practice and len(annotated_recording_list) == 12):
            for recording_id in annotated_recording_list:
                eng.execute('''update "Recording" set num_annotation = num_annotation + 1 where id = '''+ str(recording_id))
            
            eng.execute('''update "Survey" set completed = true where survey_id = ''' + "'" + survey_id + "'")

            #? DO I STILL NEED THIS COLUMN?
            # if (recording_id <= 96):
            #     place_folder = "horizontal_vertical"
            # elif (recording_id >= 97 and recording_id <= 192):
            #     place_folder = "horizontal"
            # elif (recording_id >= 2000 and recording_id <= 2049):
            #     place_folder = "horizontal_vertical"
            # else:
            #     place_folder = "horizontal"
            place_folder = "horizontal"
            
            eng.execute('''update "Survey" set recording_id = ''' + str(recording_id) + " where survey_id = '" + survey_id + "' and recording_id is null")
            eng.execute('''update "Survey" set horizontal_or_vertical = ''' + "'" + place_folder + "'" + ''' where survey_id = ''' + "'" + survey_id + "' and (recording_id < 193 or recording_id > 197)")

        return 'success'

# select_recording() receives AJAX request from the frontend to retrieve color / sub-audios (of the full audio) / full audio
# and the location of the annotations and send them back to the frontend for Confirmation page set up

@app.route('/confirm_annotation', methods=['GET', 'POST'])
def confirm_annotation():
    if (request.method == 'POST'):
        data = request.json
        survey_id = data['survey_id']

        if (data['vertical'] == 2):
            vertical = None
            vertical_exec = "null"
        else:
            vertical = bool(data['vertical'])
            vertical_exec = str(vertical)

        recording_id = -1
        recording_name = data['recording_name']
        result_recording_id = eng.execute('''select id from "Recording" where recording_name = ''' + "'" + recording_name + "' and vertical is " + vertical_exec)

        for r in result_recording_id:
            recording_id = int(dict(r)['id'])

        annotation_id = ''
        result_get_recording = eng.execute('''select id from "Annotation" where survey_id = ''' + "'" + survey_id + "' order by id desc limit 1")

        for r1 in result_get_recording:
            annotation_id = str(dict(r1)['id'])
    
        file_name = '''"file_name":{'''
        source_id = '''"source_id":{'''
        filename_json_index = 0
        result_file_name = eng.execute( '''with cte as (select "Recording".id as recording_id, "Recording_Joint_Source".source_id as source_id from "Recording" inner join "Recording_Joint_Source" on "Recording".id = "Recording_Joint_Source".recording_id) select "Source".id as source_id, "Source".file_name as file_name from "Source" inner join cte on "Source".id = cte.source_id where recording_id = '''+ str(recording_id))

        for r in result_file_name:
            file_name = file_name + '"' + str(filename_json_index) + '":' + '"' + dict(r)['file_name'] + '",'
            source_id = source_id + '"' + str(filename_json_index) + '":' + '"' + str(dict(r)['source_id']) + '",'
            filename_json_index += 1
    
        file_name = file_name[:len(file_name)-1] + "}"
        source_id = source_id[:len(source_id)-1] + "}"
        actual_num_source = '''"actual_num_source":{"0":"''' + str(filename_json_index) + '"}'

        azimuth = '''"azimuth":{'''
        elevation = '''"elevation":{'''
        color = '''"color":{'''
        location_id = '''"location_id":{'''
        json_index = 0
        result_get_location = eng.execute('''select id, azimuth, elevation, color from "Location" where annotation_id = '''+ "'" + annotation_id + "'")

        for r2 in result_get_location:
            azimuth = azimuth + '"' + str(json_index) + '":"' + str(dict(r2)['azimuth']) + '",'
            elevation = elevation + '"' + str(json_index) + '":"' + str(dict(r2)['elevation']) + '",'
            color = color + '"' + str(json_index) + '":"' + str(dict(r2)['color']) + '",'
            location_id = location_id + '"' + str(json_index) + '":"' + str(dict(r2)['id']) + '",'
            json_index += 1
    
        azimuth = azimuth[:len(azimuth)-1] + "}"
        elevation = elevation[:len(elevation)-1] + "}"
        color = color[:len(color)-1] + "}"
        location_id = location_id[:len(location_id)-1] + "}"
        user_num_source = '''"user_num_source":{"0":"''' + str(json_index) + '"}'

        return "{" + file_name + "," + azimuth + "," + elevation + "," + color + "," + user_num_source + "," + actual_num_source + "," + source_id + "," + location_id + "}"


if __name__ =='__main__':
    app.run(debug=True)