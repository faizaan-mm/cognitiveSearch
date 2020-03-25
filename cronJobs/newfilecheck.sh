inotifywait -m ./ -e create -e moved_to | # Path of the directory
    while read path action file; do
        if [[ "$file" =~ .*doc$  || "$file" =~ .*docx$ || "$file" =~ .*pdf$ ]]; then # Does the file end with .xml?
            echo "$PWD/$file" >> newfiles # If so, do your thing here!
        	echo python3 /home/ramrathi/Desktop/SIH/pdfextract.py "$PWD/$file"
        	/home/ramrathi/Desktop/SIH/pdfextract.py "$PWD/$file"
        fi
    done