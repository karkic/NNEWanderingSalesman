import neat.config
import math
import pandas as pd
from classes import Package
from datetime import datetime
import datetime
import neat
import os

MAX_PACKAGES = 8
EOD_TIME = datetime.time(23,0)
AVERAGE_SPEED = 20
GENERATIONS = 15

excel_file1 = 'WGUPS Distance Table.xlsx'
excel_file2 = 'WGUPS Package File.xlsx'

config_path = 'Config.txt'

destinations = pd.read_excel(excel_file1,header=7,index_col=0)
destinations.index = destinations.index.str.replace('\n', ' ',regex=True)
destinations.columns = destinations.columns.str.replace('\n', ' ',regex=True)
destinations['Unnamed: 1'] = destinations['Unnamed: 1'].str.split('\n').str[0]

packageList = pd.read_excel(excel_file2,header=7,)
packageList = packageList.replace('\n', ' ',regex=True)
packageList.columns = packageList.columns.str.replace('\n', ' ',regex=True)

#print(destinations.index)

def time_to_seconds(t: datetime.time) -> float:
    """Convert a datetime.time object to the number of seconds since midnight."""
    total_seconds = t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6
    return total_seconds

def time_to_normalized_float(t: datetime.time) -> float:
    """Convert a datetime.time object to a normalized float (0 to 1)."""
    total_seconds = time_to_seconds(t)
    max_seconds_in_a_day = 24 * 3600
    return total_seconds / max_seconds_in_a_day

def get_distance_to_hub(destination:str):
    distance = destinations.loc[destination, 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107']
    #print(distance)
    return distance

def get_distance(package: Package, destiation : str = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107' ):
    #print (package.dAddress)
    result = destinations[destinations['Unnamed: 1']== package.dAddress]
    #print(result)
    distance = destinations.loc[destiation,result.index].iloc[0]
    #print(distance)
    if math.isnan(distance):
        distance = destinations.loc[result.index,destiation]
    return distance

    
#main function
def eval_genomes(genomes, config):
    #print(packages[0].dDeadline)
     #genome list
    ge = []
    #nurel net of each genome
    nets = []
#build genomes
    for genome_id, genome in genomes:

        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome,config)
        nets.append(net)
        genome.fitness = 0

    
#run algorithim of each genome
    i = 0
    for genome_id, genome in genomes:
        packages= []
        
        current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
        current_time = datetime.time(8,0)

        for index, row in packageList.iterrows():
            pass
        #print(row)
            #print(index)
            package = Package(index,' '+row['Address'],row['Delivery Deadline'],'atHub', math.nan)
        #quick fix for missmatch package TODO: fix excel sheets
            if package.dAddress == ' 5383 South 900 East #104':
                package.dAddress = ' 5383 S 900 East #104'
            packages.append(package)
            genome_package_scores = []
        #runs each packages through network
        finished = False
        while finished == False:
            package_list = []
            while len(package_list) <= 15: 
                distances= []
                for package in packages:
            #needed distance,package distance to hub, current time, current distance to hub, size of package list,current time,package deadline
                    distance = get_distance(package,current_destination)
                #print(genome_id)
                    package_distance_toHub = get_distance(package)
                    package_list_size = len(package_list)
                    distance_to_hub = get_distance_to_hub(current_destination)
                    normailized = time_to_normalized_float(current_time)
                    if package.dDeadline == 'EOD':
                        package.dDeadline = EOD_TIME
                    normilized_deadline = time_to_normalized_float(package.dDeadline)
                    inputs = [distance.item(),package_distance_toHub.item(),package_list_size,distance_to_hub.item(),normailized,normilized_deadline]
                    #print(inputs)
                    output = nets[i].activate(inputs)
                    #list of distances that match packages
                    distances.append(distance.item())
                    #print(output) matches packages
                    genome_package_scores.append(output[0])
                #print(distance_to_hub.item())
    
        #get best score
                best_package = None
                best_score = -1
                #tests that genomes score list
                #print(j)
                for score,package,distance in zip(genome_package_scores,packages,distances):
                    if score >= best_score and package.dStatus == 'atHub':
                        best_score = score
                        best_package = package
                        best_distance = distance
                #print(best_package)
                package_list.append(best_package)
                if best_package == None:
                    for package in packages:
                        pass
                        finished = True
                        #print(package.dStatus)
                    break
                best_package.dStatus = "delivered"

                broken_index_location = str(destinations[destinations['Unnamed: 1']== best_package.dAddress].index).split("'")
                #print(current_destination)
                current_destination = broken_index_location[1]
                time_taken = datetime.timedelta(hours=best_distance/AVERAGE_SPEED)
                start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
                end_datetime = start_datetime + time_taken
                current_time = end_datetime.time()
                best_package.dTime = current_time
                #print(genome_id,': ',best_package.dID, ' : ', best_package.dAddress, ' : ', best_package.dTime)
            #go back to hub
            distance_to_hub = get_distance_to_hub(current_destination)
            
            time_taken = datetime.timedelta(hours=distance_to_hub.item()/AVERAGE_SPEED)
            start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
            end_datetime = start_datetime + time_taken
            current_time = end_datetime.time()
            current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
        #print(current_time)
        #bonus_points = 0
        eod_datetime = datetime.datetime(1900,1,1,EOD_TIME.hour,EOD_TIME.minute,EOD_TIME.second)
        current_datetime=datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
        total_datetime =eod_datetime - current_datetime
        #print(current_time)
        genome.fitness += total_datetime.total_seconds()/100
        for package in packages:
            if package.dDeadline != EOD_TIME:
                if package.dTime > package.dDeadline:
                    #print('lost points')
                    genome.fitness -= 50
        i+=1
        



    
        
    #print("next gen")

#neat setup
def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)
    # Add a stdout reporter to show progress in the terminal.
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(5))


    winner = pop.run(eval_genomes,GENERATIONS)

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

  

    route=[]
    route.append('HUB')
    packages= []
        
    current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
    current_time = datetime.time(8,0)

    for index, row in packageList.iterrows():
        #build pacage list
        package = Package(index,' '+row['Address'],row['Delivery Deadline'],'atHub', math.nan)
    #quick fix for missmatch package TODO: fix excel sheets
        if package.dAddress == ' 5383 South 900 East #104':
            package.dAddress = ' 5383 S 900 East #104'
        packages.append(package)
    genome_package_scores = []
        #run
    finished = False
    while finished == False:
        package_list = []
        while len(package_list) <= MAX_PACKAGES: 
            distances= []
            for package in packages:
            #needed distance,package distance to hub, current time, current distance to hub, size of package list 
                distance = get_distance(package,current_destination)
            #print(genome_id)
                package_distance_toHub = get_distance(package)
                package_list_size = len(package_list)
                distance_to_hub = get_distance_to_hub(current_destination)
                normailized = time_to_normalized_float(current_time)
                if package.dDeadline == 'EOD':
                    package.dDeadline = EOD_TIME
                normilized_deadline = time_to_normalized_float(package.dDeadline)
                inputs = [distance.item(),package_distance_toHub.item(),package_list_size,distance_to_hub.item(),normailized,normilized_deadline]
                #print(inputs)
                output = winner_net.activate(inputs)
                #list of distances that match packages
                distances.append(distance.item())
                #print(output) matches packages
                genome_package_scores.append(output[0])
                #print(distance_to_hub.item())
    
        #get best score
            best_package = None
            best_score = -1
                #tests that genomes score list
                #print(j)
            for score,package,distance in zip(genome_package_scores,packages,distances):
                if score >= best_score and package.dStatus == 'atHub':
                    best_score = score
                    best_package = package
                    best_distance = distance
            #print(best_package)
            
            if best_package == None:
                for package in packages:
                    pass
                finished = True
                #print(package.dStatus)
                break
            best_package.dStatus = "delivered"
            package_list.append(best_package)
            route.append(best_package.dAddress)
            broken_index_location = str(destinations[destinations['Unnamed: 1']== best_package.dAddress].index).split("'")
            #print(current_destination)
            current_destination = broken_index_location[1]
            time_taken = datetime.timedelta(hours=best_distance/AVERAGE_SPEED)
            start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
            end_datetime = start_datetime + time_taken
            current_time = end_datetime.time()
            best_package.dTime = current_time
            #print(genome_id,': ',best_package.dID, ' : ', best_package.dAddress, ' : ', best_package.dTime)
            #go back to hub
        distance_to_hub = get_distance_to_hub(current_destination)
            
        time_taken = datetime.timedelta(hours=distance_to_hub.item()/AVERAGE_SPEED)
        start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
        end_datetime = start_datetime + time_taken
        current_time = end_datetime.time()
        current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
        route.append('HUB')
        #print(current_time)
        #bonus_points = 0
    eod_datetime = datetime.datetime(1900,1,1,EOD_TIME.hour,EOD_TIME.minute,EOD_TIME.second)
    current_datetime=datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
    total_datetime =eod_datetime - current_datetime
        #print(current_time)
    missed_packages = 0
    for package in packages:
        if package.dDeadline != EOD_TIME:
            if package.dTime > package.dDeadline:
                    #print('lost points')
                missed_packages+=1
    print("time:", current_time,' : Late:', missed_packages)
    #for i in route:
        #print(i)
    #shortest path
    route=[]
    route.append('HUB')
    packages=[]
    for index, row in packageList.iterrows():
        #build pacage list
        package = Package(index,' '+row['Address'],row['Delivery Deadline'],'atHub', math.nan)
    #quick fix for missmatch package TODO: fix excel sheets
        if package.dAddress == ' 5383 South 900 East #104':
            package.dAddress = ' 5383 S 900 East #104'
        #print(package.dStatus)
        packages.append(package)


    print("shortest path compare:")

    current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
    current_time = datetime.time(8,0)
    
    #print(current_time)
    finished = False
    while finished == False:
        package_list = []
        while len(package_list) <= MAX_PACKAGES: 
            distance_to_hub = get_distance_to_hub(current_destination)
            distances=[]
            for package in packages:
                if package.dDeadline == 'EOD':
                    package.dDeadline = EOD_TIME
                distance = get_distance(package,current_destination)
                #print(distance)
                distances.append(distance.item())
            best_package = None
            best_distance = 100
            #print(distances)
            best_time = EOD_TIME


            for package,distance in zip(packages,distances):
                #print(package.dID, " : ", package.dDeadline)
                if package.dStatus == 'atHub':
                    if package.dDeadline < best_time:
                        best_package = package
                        best_distance = distance
                        best_time = package.dDeadline
                        #print("changed to ",best_time)
                    elif package.dDeadline == best_time:
                        if distance < best_distance and package.dStatus == 'atHub':
                            best_package = package
                            best_distance = distance
                            best_time = package.dDeadline
                

            #print("break")
            if best_package == None:
                finished = True
                break
            best_package.dStatus = "delivered"
            package_list.append(best_package)
            route.append(best_package.dAddress)
            broken_index_location = str(destinations[destinations['Unnamed: 1']== best_package.dAddress].index).split("'")
            #print(current_destination)
            current_destination = broken_index_location[1]
            time_taken = datetime.timedelta(hours=best_distance/AVERAGE_SPEED)
            start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
            end_datetime = start_datetime + time_taken
            current_time = end_datetime.time()
            best_package.dTime = current_time
            #print(best_package.dDeadline)
            #print(best_package.dTime) 
            #print("deilvery time:",current_time)
        #go back to hub
        time_taken = datetime.timedelta(hours=distance_to_hub.item()/AVERAGE_SPEED)
        start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
        end_datetime = start_datetime + time_taken
        current_time = end_datetime.time()
       
        current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
        route.append('HUB')
    missed_packages = 0
    for package in packages:
        #print(package.dTime)
        if package.dDeadline != EOD_TIME:
            #print(package.dTime)
            #print(package.dDeadline)
            if package.dTime > package.dDeadline:
                #print('lost points')
                missed_packages+=1
    print("time:", current_time,' : Late:', missed_packages)

    #for i in route:
        #print(i)

     

if __name__ == '__main__':

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config.txt')
    run(config_path)

