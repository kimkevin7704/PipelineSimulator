import sys, getopt

ifile = ''
ofile = ''


myopts, args = getopt.getopt(sys.argv[1:], 'i:o:')

for o, a in myopts:
        if o == '-i':
                ifile = a
        elif o == '-o':
                ofile = a


outfile = open(ofile + "_sim.txt", 'w')


#read each line of file and put in list
#with open(ifile, 'r') as infile:
#    data = infile.read()
#my_list = data.splitlines()

output_file = open(ofile + "_dis.txt", "w")
