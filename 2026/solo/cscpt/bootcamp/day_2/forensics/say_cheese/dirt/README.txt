Digital Image Resizer Toy README
================================


This 'toy' is a program that implements the seam carving algorithms from
"Seam Carving for Content-Aware Image Resizing".  The authors of this 
paper, Shai Avidan and Ariel Shamir, are responsible for the algorithm
design.  This program allows you to remove seams from an image step
by step by using the left and up arrow keys, or add seams by using
the right and down arrow keys.  You can also add areas of the image
to preserve and remove, however this is not implemented as described
in the paper.  You may also retarget the size of the image, or erase
entire portions (i.e. not stepping through it yourself).  The algorithm
to enlarge areas of the image (section 4.4 of the paper) is not
implemented here.  Erase is not guaranteed to erase all selected portions
of the image, you may need to run it more than once.


System Requirements
-------------------

You must be running Java 1.5 or higher in order to run DIRT.


Running DIRT
------------

Either double click the jar file (in Windows), double click the bat
file (Windows) or run the following command at a prompt from the folder
you extracted DIRT to (all other os'es):

java -jar dirt.jar

or if you have memory issues, try this:

java -jar -Xmx512m dirt.jar

Where 512 is the amount of RAM memory in Megabytes you wish to allocate
to the program.  It must be smaller than your physical ram size.