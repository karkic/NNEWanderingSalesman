import neat
from datetime import datetime

class Package:
    def __init__(self,dID, dAddress, dDeadline : datetime.time, dStatus, dTime):
        self.dID = dID
        self.dAddress = dAddress
        self.dDeadline = dDeadline
        self.dStatus = dStatus
        self.dTime = dTime

class FileReporter(neat.reporting.BaseReporter):
    def __init__(self, filename):
        self.filename = filename

    def start_generation(self, generation):
        with open(self.filename, 'a') as f:
            f.write(datetime.now().strftime("%H:%M:%S"))
            f.write(f": Starting generation {generation}\n")

    def post_evaluate(self, config, population, species, best_genome):
        best_fitness = best_genome.fitness
        with open(self.filename, 'a') as f:
            f.write(datetime.now().strftime("%H:%M:%S"))
            f.write(f": Post evaluate: Best fitness {best_fitness}\n")

    def complete_extinction(self):
        with open(self.filename, 'a') as f:
            f.write("All species extinct.\n")

    def found_solution(self, config, generation, best):
        with open(self.filename, 'a') as f:
            f.write(f"Found solution in generation {generation}\n")

    def end_generation(self, config, population, species):
        with open(self.filename, 'a') as f:
            f.write(datetime.now().strftime("%H:%M:%S"))
            f.write(f": End of generation\n")
