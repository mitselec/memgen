# Legacy artifact - kept for historical reference only.
# This 2017 snippet never ran as written (see legacy/README.md for the
# known defects). Use the `memgen` tool instead - see ../README.md.
#**********************************************************
#COE file creation
#This code snippet is used to create an initialization file
#for the BRAM module that is created.
#**********************************************************
fo = open("filename.coe","wb")
fo.write(";******************************************************************\n");
fo.write(";******** Example of Single Port Block Memory .COE file *********\n");
fo.write(";******************************************************************\n");
fo.write("; Sample memory initialization file for Single Port Block Memory, \n");
fo.write("; v3.0 or later. \n");
fo.write("; This .COE file specifies initialization values for a block \n");
fo.write("; memory of depth=*define this*, and width=16. In this case, values are \n");
fo.write("; specified in hexadecimal format. \n");
#Initialization radix can only be 2,4,8 and 16
fo.write("memory_initialization_radix=16;\n");
fo.write("memory_initialization_vector=\n");
 
#Insert a function of your choice to fill line after line the designated value
#with a comma and a newline in the end
 
fo.close;
 
#Remove last comma in file and replace it with a ";"
with open('filename.coe', 'rb+') as fo:
fo.seek(-2, os.SEEK_END)
fo.truncate()
fo.write(";\n")
fo.close;
