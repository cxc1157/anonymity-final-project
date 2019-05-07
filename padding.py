"""
padding.py

This program reads in a file containing instances of different
circuit types and pads them according to the CC scheme, whose goal
is to make it harder to distinguish HS-RP and Client-RP circuits
from general circuits.

This program is currently only designed to provide padding for a
dataset in the same format as the seq10-50-only200RPs.arff file.

author: Caroline Caceci
"""

import random
import sys

def pad_sequence(seq):
    """
    This function takes in a sequences of in and out cells represented by 
    +1 and -1 and pads it.
    :param seq:
    :return: padded sequence, original number of cells in sequence,
             number of added incoming cells, and number of added outgoing cells
    """
    seq_split = seq.strip().split("1")
    last = seq_split[0]
    new_seq = last + "1"
    inc_added = 0
    out_added = 0
    for i in range(1, len(seq_split)-1):
        current = seq_split[i]

        # break up the intial sequences that leak information by adding padding
        if current == last:
            if last == "-":
                new_seq += "+1"
                inc_added += 1
                last = "+"
            else:
                new_seq += "-1"
                out_added += 1
                last = "-"
        else:
            new_seq += current + "1"
            last = current

        # 30% chance to inject randomness
        coin = random.randint(1, 101)
        if coin <= 30:
            if coin % 2 == 0:
                new_seq += "+1"
            else:
                new_seq += "-1"
    
    # return padded sequence, original number of cells, 
    # number of incoming padding cells, and number of outgoing padding cells
    return new_seq, len(seq_split), inc_added, out_added

def pad_instance(line):
    """
    This function takes in a line from the data file and pads it.
    :param line:
    :return: padded the padded instance, initial total number of cells,
             and number of cells after padding
    """
    
    # split the line and extract attributes
    attributes = line.split(",")
    seq = attributes[0].strip()
    inc = int(attributes[1])
    out = int(attributes[2])
    lifetime = float(attributes[3])
    classify = attributes[4]
    inc_50 = int(attributes[5])
    out_50 = int(attributes[6])

    # how many cells were sent/received before any padding
    initial_num_cells = inc + out

    # the ratio of outgoing cells to incoming cells
    out_in_ratio = float(out)/float(inc)
    new_seq, orig_seq_length, inc_added, out_added = pad_sequence(seq)
    
    # account for added beginning sequence padding in overall total
    inc += inc_added
    out += out_added

    # account for added beginning sequence padding in first 50 or so cells
    inc_50 += inc_added
    out_50 += out_added

    out_padding = 0
    in_padding = 0
    
    # flip a coin
    coin = random.randint(1, 9)
    
    # if the circuit has more incoming cells than outgoing cells 
    # (typical of Client-RP)
    if classify != "noise" and out_in_ratio < 0.98:
        
        # pad the outgoing cells to bring the ratios closer
        if coin <= 4:
            out_padding = int(out / out_in_ratio * 0.85)
        else:
            out_padding = int(out / out_in_ratio * 1.05)
    
    # if there are more outgoing than incoming cells 
    # (typical of HS-RP)
    elif classify != "noise" and out_in_ratio > 1.02:
        
        # pad the incoming cells to bring the ratios closer
        if coin <= 4:
            in_padding = int(inc * out_in_ratio * 0.9)
        else:
            in_padding = int(inc * out_in_ratio * 1.05)

    # add the appropriate padding to the overall totals
    inc += in_padding
    out += out_padding

    # we have to account for how padding would affect the first 50 or so cells
    first_cells = inc_50 + out_50
    first_ratio = float(inc_50)/first_cells
    if first_cells > 50:
        first_cells = 50
  
    # the first 50 cells should have a similar ratio to the padding
    new_inc_percent = float(inc) / (inc + out)
    
    # add a bit of randomness to the first 50 if they are not noise
    first_random = random.randint(1, 201) / 1000.0
    flip = random.randint(1, 11)
    if flip % 2 == 0:
        if new_inc_percent + new_inc_percent * first_random < 1:
            new_inc_percent += new_inc_percent * first_random
    else:
        if new_inc_percent - new_inc_percent * first_random < 1:
            new_inc_percent -= new_inc_percent * first_random

    general = False
    # don't mess with the ratio if we didn't pad the whole thing
    if classify == "noise":
        general = True
        new_inc_percent = first_ratio

    # the first 50 cells should follow the padded ratio
    inc_50 = int(new_inc_percent * first_cells)
    out_50 = first_cells - inc_50

    # the padded instance for the new file
    padded_instance = new_seq + "," + str(inc) + "," + str(out) + "," \
        + str(lifetime) + "," + classify + "," + str(inc_50) + "," + str(out_50)

    num_cells_with_padding = inc + out

    # return the padded instance, the initial number of cells for the circuit,
    # and the number of cells after padding, because we need to know
    # how much overhead the padding adds
    return padded_instance, initial_num_cells, num_cells_with_padding, general

def process_file(filename):
    """
    This function processes a data file and creates a new file that has
    padded data. It also calculates how much overhead is added overall.
    :param filename:
    :return: None
    """
    
    # create a new file to write to
    nfn = "padded-" + filename
    new_file = open(nfn, "w")
    data = False

    # track the number of real cells and the number of cells including padding
    num_real_cells = 0
    num_cells_with_padding = 0
    num_special_initial = 0
    num_special_with_padding = 0
    with open(filename) as f:
        for line in f:
            line = line.strip()

            # if the line contains instance data, pad it
            if data == True and "," in line:
                padded_instance, initial_cells, padded_cells, general = \
                    pad_instance(line)
                num_real_cells += initial_cells
                num_cells_with_padding += padded_cells

                # track how much overhead is added to special circuits
                if not general:
                    num_special_initial += initial_cells
                    num_special_with_padding += padded_cells
                new_file.write(padded_instance + "\n")

            # otherwise, write line to file (i.e. attributes)
            else:
                new_file.write(line + "\n")
            if line == "@DATA":
                data = True
    new_file.close()
    
    # print overhead details about only special circuits
    print("number of unpadded cells (only special circuits):", \
        num_special_initial)
    print("number of cells including padding (only special circuits):", \
        num_special_with_padding)
    special_padding_cells = num_special_with_padding - num_special_initial
    special_overhead = special_padding_cells/num_special_initial * 100
    print("added special circuit overhead from padding cells:", \
        round(special_overhead, 2), "percent\n")
    
    # print overhead details about all circuits
    print("number of unpadded cells (all circuit types):", num_real_cells)
    print("number of cells including padding (all circuit types):", \
        num_cells_with_padding)
    padding_cells = num_cells_with_padding - num_real_cells
    network_overhead = padding_cells/num_real_cells * 100
    print("added network overhead from padding cells:", \
        round(network_overhead, 2), "percent")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 padding.py <.arff file name>")
    else:
        process_file(sys.argv[1])

main()
