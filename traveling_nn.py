import neat.config
import math
import neat.genome
import pandas as pd
from classes import Package, FileReporter
from datetime import datetime
import visualize 
import datetime
import neat
import os
import configparser

settings = configparser.ConfigParser()

settings.read('settings.ini')

IMPORT_GENOME = settings['DEFAULT']['import_genome']

MAX_PACKAGES = int(settings['DEFAULT']['max_packages'])
EOD_TIME = datetime.time(23,0)
AVERAGE_SPEED = int(settings['DEFAULT']['average_speed'])
GENERATIONS = int(settings['DEFAULT']['generations'])
OPTION = int(settings['DEFAULT']['option'])
#shortest distance algorithom min/max
SHORT_PENALTY = 0.0
LONG_PENALTY = 9.2

excel_file1 = 'WGUPS Distance Table.xlsx'
excel_file2 = 'WGUPS Package File.xlsx'
log_filename = 'log.txt'

config_path = 'Config.txt'
#build datasets
#destnations
destinations = pd.read_excel(excel_file1,header=7,index_col=0)
destinations.index = destinations.index.str.replace('\n', ' ',regex=True)
destinations.columns = destinations.columns.str.replace('\n', ' ',regex=True)
destinations['Unnamed: 1'] = destinations['Unnamed: 1'].str.split('\n').str[0]

packageList = pd.read_excel(excel_file2,header=7,)
packageList = packageList.replace('\n', ' ',regex=True)
packageList.columns = packageList.columns.str.replace('\n', ' ',regex=True)
#conver time to seconds

def concatenate_args_simple(*args):
    return ' '.join(str(arg) for arg in args)

#file reporter

def time_to_seconds(t: datetime.time) -> float:
    """Convert a datetime.time object to the number of seconds since midnight."""
    total_seconds = t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6
    return total_seconds
# convert time to float
def time_to_normalized_float(t: datetime.time) -> float:
    """Convert a datetime.time object to a normalized float (0 to 1)."""
    total_seconds = time_to_seconds(t)
    max_seconds_in_a_day = 24 * 3600
    return total_seconds / max_seconds_in_a_day
#get distance from location to hub
def get_distance_to_hub(destination:str):
    distance = destinations.loc[destination, 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107']
    #print(distance)
    return distance
#get distace to package
def get_distance(package: Package, destiation : str = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107' ):
    result = destinations[destinations['Unnamed: 1']== package.dAddress]
    distance = destinations.loc[destiation,result.index].iloc[0]
    if math.isnan(distance):
        distance = destinations.loc[result.index,destiation]
    return distance

def run_NNetwork(net: neat.nn.FeedForwardNetwork, post = False):
    #starting values
    route=[]
    route.append("HUB")
    genome_fitness = 0
    shortest_distance = 100.0
    longest_distance = 0.0
    packages=[]    
    current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
    current_time = datetime.time(8,0)

    for index, row in packageList.iterrows():
        package = Package(index,' '+row['Address'],row['Delivery Deadline'],'atHub', math.nan)
        #quick fix for missmatch package TODO: fix excel sheets
        if package.dAddress == ' 5383 South 900 East #104':
            package.dAddress = ' 5383 S 900 East #104'
        packages.append(package)
        #runs each packages through network
    finished = False
    while finished == False:
        package_list = []
        while len(package_list) <= MAX_PACKAGES: 
            #clear arrays
            distances= []
            genome_package_scores = []
            genome_hub_scores = []
            for package in packages:
            #needed distance,package distance to hub, current time, current distance to hub, size of package list,current time,package deadline
                distance = get_distance(package,current_destination)
                package_distance_toHub = get_distance(package)
                package_list_size = len(package_list)
                distance_to_hub = get_distance_to_hub(current_destination)
                normailized = time_to_normalized_float(current_time)
                if package.dDeadline == 'EOD':
                    package.dDeadline = EOD_TIME
                normilized_deadline = time_to_normalized_float(package.dDeadline)
                inputs = [distance.item(),package_distance_toHub.item(),package_list_size,distance_to_hub.item(),normailized,normilized_deadline]
                    #print(inputs)
                output = net.activate(inputs)
                    #list of distances that match packages
                distances.append(distance.item())
                    #print(output) matches packages
                genome_package_scores.append(output[0])
                genome_hub_scores.append(output[1])
    
            #get best score
            best_package = None
            best_score = -1
            best_hub_score = -1
                #tests that genomes score list
            for score,package,distance,hub_score in zip(genome_package_scores,packages,distances,genome_hub_scores):
                if score >= best_score and package.dStatus == 'atHub':
                    best_score = score
                    best_package = package
                    best_distance = distance
                    best_hub_score = hub_score

                #if not at hub
            if current_destination != 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107':
                #return to hub if best_package hub score is greater that the travel score
                if best_hub_score > best_score:
                        #discurage overuse
                    genome_fitness -=5
                    break

                    
                
            package_list.append(best_package)
            if best_package == None:
                finished = True
                break
            best_package.dStatus = "delivered"
            route.append(best_package.dAddress)
                #test if longest path or shortest path
            if best_distance > longest_distance:
                longest_distance = best_distance
            if best_distance < shortest_distance:
                shortest_distance = best_distance
                #distance bounus/penalty points
            if best_distance == 0.0:
                genome_fitness += 5
            if best_distance > LONG_PENALTY:
                genome_fitness -= 5
            #get time to destination
            broken_index_location = str(destinations[destinations['Unnamed: 1']== best_package.dAddress].index).split("'")
            current_destination = broken_index_location[1]
            time_taken = datetime.timedelta(hours=best_distance/AVERAGE_SPEED)
            start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
            end_datetime = start_datetime + time_taken
            current_time = end_datetime.time()
            best_package.dTime = current_time
        #go back to hub
        distance_to_hub = get_distance_to_hub(current_destination)
        #test if longest path or shortest path
        if distance_to_hub > longest_distance:
            longest_distance = distance_to_hub
        if distance_to_hub < shortest_distance:
            shortest_distance = distance_to_hub
        if distance_to_hub > LONG_PENALTY:
            genome_fitness -= 5
            
            
        # get time to destination  
        time_taken = datetime.timedelta(hours=distance_to_hub.item()/AVERAGE_SPEED)
        start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
        end_datetime = start_datetime + time_taken
        current_time = end_datetime.time()
        current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
        route.append("HUB")
        #bonus_points = 0
    eod_datetime = datetime.datetime(1900,1,1,EOD_TIME.hour,EOD_TIME.minute,EOD_TIME.second)
    current_datetime=datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
    total_datetime =eod_datetime - current_datetime
    #score genome
    genome_fitness += (LONG_PENALTY - longest_distance)*2
    genome_fitness += (SHORT_PENALTY - shortest_distance)*2
    genome_fitness += total_datetime.total_seconds()/100
    #test for late packages
    missed_packages = 0
    for package in packages:
        if package.dDeadline != EOD_TIME:
            if package.dTime > package.dDeadline:
                missed_packages += 1
                genome_fitness -= 100
    #print
    if post:
        #post route
        with open(log_filename,"a") as f:
            #TODO: post route to different textfile
            #for destination in route:
                #destination_string = concatenate_args_simple(destination , "\n")
                #f.write(destination_string)

            output_string= concatenate_args_simple("time:", current_time,' : Late:', missed_packages,"\nshortest:", shortest_distance,"longest:", longest_distance, "\n")
            f.write(output_string)
    return genome_fitness

    
#main function
def eval_genomes(genomes, config):
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
    for genome, net in zip (ge,nets):
        genome.fitness = run_NNetwork(net)
    

#neat setup
def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    node_names = {-1: 'Distance to Package',-2: 'Package distance to hub',-3: 'Current loop package',-4: 'Distance to hub', -5: 'Current Time',-6: 'Package Deadline', 1: 'hub output', 0: 'package output'}

    #selected generation
    failed= False
    try:
        pop = neat.Checkpointer.restore_checkpoint(IMPORT_GENOME)
    except:
        with open(log_filename, "a" ) as f:
            f.write("Could not find file running new generations\n")
        pop = neat.Population(config)
        
    if OPTION == 1:
        try:
            pop = neat.Checkpointer.restore_checkpoint(IMPORT_GENOME)
            best_genome = pop.run(eval_genomes, 1)
            winner_net = neat.nn.FeedForwardNetwork.create(best_genome,config)
            run_NNetwork(winner_net,True) 
            visualize.draw_net(config, best_genome, True, node_names=node_names)
        except:
            failed = True
    else:
    # Add a stdout reporter to show progress in the terminal.
        pop.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()

        pop.add_reporter(FileReporter(log_filename))

        pop.add_reporter(stats)
        checkpointer = neat.Checkpointer(5)
        pop.add_reporter(checkpointer)

    #visualize.draw_net(config,best_genome,True,node_names=node_names)
        winner = pop.run(eval_genomes,GENERATIONS)

    # Display the winning genome.
        print('\nBest genome:\n{!s}'.format(winner))
        winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    #run winner
        run_NNetwork(winner_net,True)
        checkpointer.save_checkpoint(config,pop.population,pop.species,pop.generation)
    
    #compare to sortest distance algorithm
    if failed == False:
        print("shortest path compare:")

        current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
        current_time = datetime.time(8,0)
        longest_distance = 0.0
        packages =[]
        route = []

        for index, row in packageList.iterrows():
            package = Package(index,' '+row['Address'],row['Delivery Deadline'],'atHub', math.nan)
        #quick fix for missmatch package TODO: fix excel sheets
            if package.dAddress == ' 5383 South 900 East #104':
                package.dAddress = ' 5383 S 900 East #104'
            packages.append(package)
    
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
                    distances.append(distance.item())
                best_package = None
                best_distance = 100
                best_time = EOD_TIME
                for package,distance in zip(packages,distances):
                    if package.dStatus == 'atHub':
                        if package.dDeadline < best_time:
                            best_package = package
                            best_distance = distance
                            best_time = package.dDeadline
                        elif package.dDeadline == best_time:
                            if distance < best_distance and package.dStatus == 'atHub':
                                best_package = package
                                best_distance = distance
                                best_time = package.dDeadline
                if best_package == None:
                    finished = True
                    break
                if best_distance > longest_distance:
                    longest_distance = best_distance
                best_package.dStatus = "delivered"
                package_list.append(best_package)
                route.append(best_package.dAddress)
                broken_index_location = str(destinations[destinations['Unnamed: 1']== best_package.dAddress].index).split("'")
                current_destination = broken_index_location[1]
                time_taken = datetime.timedelta(hours=best_distance/AVERAGE_SPEED)
                start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
                end_datetime = start_datetime + time_taken
                current_time = end_datetime.time()
                best_package.dTime = current_time
            #go back to hub
            time_taken = datetime.timedelta(hours=distance_to_hub.item()/AVERAGE_SPEED)
            if distance_to_hub.item() > longest_distance:
                longest_distance = distance_to_hub
            start_datetime = datetime.datetime(1900,1,1,current_time.hour,current_time.minute,current_time.second)
            end_datetime = start_datetime + time_taken
            current_time = end_datetime.time()
       
            current_destination = 'Western Governors University 4001 South 700 East,  Salt Lake City, UT 84107'
            route.append('HUB')
        #late package total
        missed_packages = 0
        for package in packages:
            if package.dDeadline != EOD_TIME:
                if package.dTime > package.dDeadline:
                    missed_packages+=1
        with open(log_filename, "a" ) as f:
            f.write("Compare to Shortest route algorithm:\n")
            f.write(concatenate_args_simple( "time:", current_time,' : Late:', missed_packages))
            f.write(concatenate_args_simple("\nshortest: 0.0 ","longest:", longest_distance, "\n"))

    

#visulizer
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)



if __name__ == '__main__':

   

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,'config.txt')
    run(config_path)

