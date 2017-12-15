+++How to make a dat file for custom fortunes

1. Install fortune (apt-get install fortune-mod)
2. Create a text file with % as the delimiter between texts. 
3. Create a dat file by running strfile -c% <inputfilename> <inputfilename>.dat
4. Run fortune <pathtoinputfile> to get a fortune
