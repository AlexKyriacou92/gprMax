import numpy as np
import matplotlib.pyplot as pl
import sys
import os
from properties import material, mu0, epsilon0, c0, Z0
import datetime

sys.path.append('/home/alex/gprMax')
c0 = 3e8

freq_max = 5e8
airHeight = 25
iceLength = 100
iceDepth = 100
totalHeight = airHeight + iceDepth

wavelength_min = c0/freq_max
dx = wavelength_min/10.
dy = dx
dz = dy

time_window = 1e-6

freq_centre = 2.5e8
amplitude = 1.0
waveform_type = "ricker"
waveform_name = "my_ricker"

ice = material(3.2, 1, 0, 0, 'ice')
vacuum = material(1, 1, 0, 0, 'vacuum')

sourceDepth = 50.
sourceRange = 0.
fname = "example.in"

rxRange = 20.
rxDepth = sourceDepth

#Cluster Settings
NODES_MIN = 1
NODES_MAX = 4
PARTITION = 'normal'
DAYS = 3
HOURS = 0
MEMORY = 4000 # in MB

def make_infile(fname, sim_title, source_range = sourceRange, source_depth = sourceDepth, rx_range = rxRange, rx_depth = rxDepth):
    sourceHeight_domain = iceDepth - source_depth

    input_file = open(fname, "w")
    #Domain, resolution and time
    input_file.write("#title: " + sim_title + "\n")
    input_file.write("#domain: " + str(iceLength) + " " + str(totalHeight) + " " + str(dz) + "\n")
    input_file.write("#dx_dy_dz: " + str(dx) + " " + str(dy) + " " + str(dz) + "\n")
    input_file.write("#time_window: " + str(time_window) + "\n")

    #Materials
    input_file.write(ice.get_string())
    input_file.write(vacuum.get_string())

    #Source
    input_file.write("#waveform: " + waveform_type + " " + str(amplitude) + " " + str(freq_centre) + " " + waveform_name + "\n")
    input_file.write("#hertzian_dipole: z " + str(source_range) + " " + str(sourceHeight_domain) + " " + str(0) + " " + waveform_name + "\n")

    #Receiver
    input_file.write("#rx: " + str(rx_range) + " " + str(rx_depth) + " " + str(0) + "\n")

    #Set Geometry
    input_file.write("box: " + str(0) + " " + str(0) + " " + str(0) + " " + str(iceLength) + " " + str(iceDepth) + " " + str(dz) + " " + ice.name + "\n")
    input_file.write("box: " + str(0) + " " + str(iceDepth) + " " + str(0) + " " + str(iceLength) + " " + str(totalHeight) + " " + str(dz) + " " + vacuum.name + "\n")
    input_file.close()

def make_shell(sh_name, input_file, output_file, jobname, nNodes_min, nNodes_max, partition, days, hours, nodeMemory):
    """
    sh_name = shell file name -> to submit to pleaides
    input_file = the input file for the simulation
    output_file = the slurm output file -> where all the print statements go
    jobname = name of the simulation
    """

    sbatch = "#SBATCH"
    fout = open(sh_name, "w")
    fout.write("#!/bin/sh\n")

    minutes = 0
    seconds = 0

    fout.write(sbatch + " --job-name=" + jobname + "\n")
    fout.write(sbatch + " --partition=" + partition + "\n")
    fout.write(sbatch + " --time=" + str(days) + "-" + str(hours) + ":" + str(minutes) + ":" + str(
        seconds) + " # days-hours:minutes:seconds\n")
    if nNodes_min == nNodes_max:
        fout.write(sbatch + " --nodes=" + str(nNodes_min) + "\n")
    else:
        fout.write(sbatch + " --nodes=" + str(nNodes_min) + "-" + str(nNodes_max) + "\n")
    fout.write(sbatch + " --mem-per-cpu=" + str(nodeMemory) + " # in MB\n")
    fout.write(sbatch + " -o " + str(output_file) + "\n")

    jobline = "python -m gprMax " + input_file
    fout.write(jobline)
    fout.close()
    makeprogram = "chmod u+x " + sh_name
    os.system(makeprogram)

rx_ranges = np.arange(0, rxRange, 1.)
nRX = len(rx_ranges)
if __name__ == "__main__":
    #Get current directory
    cwd = os.getcwd()
    now = datetime.datetime.now()
    tstring = now.strftime("%y%m%d-%H:%M:%S")
    sim_list = "sim-list-" + tstring + ".txt"
    fout = open(sim_list, "w")
    for i in range(nRX):
        R = rx_ranges[i]
        sim_name = "pure-ice-" + str(R)
        fname = cwd + "/" + sim_name + ".in"
        sh_fname = cwd + "/" + sim_name + ".sh"
        slurm_file = cwd + "/" + "slurm-" + sim_name + ".out"
        make_infile(fname, sim_name, sourceRange, sourceDepth, R, rxDepth)
        #nNodes_min, nNodes_max, partition, days, hours, nodeMemory):
        make_shell(sh_fname, fname, slurm_file, sim_name, NODES_MIN, NODES_MAX, PARTITION, DAYS, HOURS, MEMORY)
        line = fname + "\t" + sh_fname + "\t" + slurm_file + "\n"
        fout.write(line)
    fout.close()