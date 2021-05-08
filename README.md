# AutoClip video generator
Generate video clips / compilations from AutoClip datasets. Requires Python, youtube-dl and ffmpeg. 
Optionally requires the vcsi Python package for thumbnail generation. [This YouTube channel](https://www.youtube.com/channel/UC6sfBMKXtwZBJ7j5WPyvf6g/videos) has examples of generated videos.

## Usage

1. Use the dataset from https://github.com/mipacd/auto-clip or [generate your own](https://github.com/mipacd/auto-clip-tool).
2. Run on a CSV to generate a compilation: `python3 ./auto-clip-vid-gen.py -s hlen -t ../auto-clip/csv/hl/humor/2021-4-25.csv hlen-funny-comp-2021-04-25.mp4`
3. One minute clips from each stream are downloaded to ./clips/. Timestamps and channel citations are saved in description.txt.


## Options
--length, -l Length of clip. Clip starts from 30 seconds before region of interest and continues for 1 minute by default. 

--streamer, -s Channel/Streamer. Use individual names seperated by commas or use a grouping defined in streamers.py  

--no-concat, -n Download clips without concatinating into a compilation. Clips can be modified and combined in a subsequent run without the -n flag, given that all videos remain in the same format and the -d flag is not used.  

--delete, -d Delete all clips from ./clips/ directory  

--thumb, -t Lazy thumbnail generation. Requires the vcsi Python package: `pip3 install vcsi`  
