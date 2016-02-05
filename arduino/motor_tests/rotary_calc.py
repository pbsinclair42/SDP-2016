# Used to calculate the efficiency of a motor by averaging out the outputs
# from rotary_master's output.
# Assumes output has been copied into a file with motorX


if __name__ == "__main__":
    
    motors1 = []
    motors2 = []
    motors3 = []
    
    prev1 = 0.0
    prev2 = 0.0
    prev3 = 0.0

    all_motors = [motors1, motors2, motors3]

    filename = "motorX.txt"
    with open(filename, "r") as f_obj:
        for line in f_obj:
            line_vals = line.split()
            motors1.append(float(line_vals[0]) - prev1)
            motors2.append(float(line_vals[1]) - prev2)
            motors3.append(float(line_vals[2]) - prev3)
            
            prev1 = float(line_vals[0])
            prev2 = float(line_vals[1])
            prev3 = float(line_vals[2])

    print ("Motor1 = {0}".format(sum(motors1) / len(motors1)))
    print ("Motor2 = {0}".format(sum(motors2) / len(motors2)))
    print ("Motor3 = {0}".format(sum(motors3) / len(motors3)))
