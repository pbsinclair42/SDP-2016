
if __name__ == "__main__":
    
    motors1 = []
    motors2 = []
    motors3 = []
    
    all_motors = [motors1, motors2, motors3]

    filename = "motorX"
    with open(filename, "r") as f_obj:
        for line in f_obj:
            line_vals = line.split()
            motors1.append(float(line_vals[0]))
            motors2.append(float(line_vals[1]))
            motors3.append(float(line_vals[2]))
    
    print ("Motor1 = {0}".format(sum(motors1) / len(motors1)))
    print ("Motor2 = {0}".format(sum(motors2) / len(motors2)))
    print ("Motor3 = {0}".format(sum(motors3) / len(motors3)))
