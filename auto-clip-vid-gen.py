import argparse
import csv
import datetime
import subprocess
import os
import shutil

#arguments
parser = argparse.ArgumentParser(description="AutoClip CSV to Video")
parser.add_argument('path', type=str, help="Path to AutoClip CSV")
parser.add_argument('output', type=str, help="Output video file path (MP4 file)")
parser.add_argument('--length', '-l', type=int, default=60, help="Length of each clip in seconds (default: 60)")
parser.add_argument('--streamer', '-s', type=str, help="Specify one or more streamers, comma separated or group: hljp, hlen, hlid, hstars")
parser.add_argument("--no-concat", '-n', action="store_true", help="Download clips without concatenation")
parser.add_argument("--delete", '-d', action="store_true", help="Delete video cache")
parser.add_argument("--thumb", '-t', action="store_true", help="Generate thumbnail for concatinated video, requires vcsi package")

args = parser.parse_args()

#grouping lists
hljp = ['AZki', 'Miko', 'Roboco', 'Sora', 'Suisei', 'Mel', 'Haato', 'Fubuki', 'Matsuri', 'Aki', 'Shion', 'Aqua',
    'Ayame', 'Choco', 'Subaru', 'Korone', 'Mio', 'Okayu', 'Noel', 'Rushia', 'Pekora', 'Flare', 'Marine',
    'Luna', 'Coco', 'Watame', 'Kanata', 'Towa', 'Lamy', 'Nene', 'Botan', 'Polka']
hlen = ['Calli', 'Kiara', 'Ina', 'Gura', 'Amelia']
hlid = ['Risu', 'Moona', 'Iofi', 'Reine', 'Anya', 'Ollie']
hstars = ['Miyabi', 'Kira', 'Izuru', 'Aruran', 'Rikka', 'Astel', 'Temma', 'Roberu', 'Shien', 'Oga']

if args.delete:
    shutil.rmtree("vidtmp/")
    os.mkdir("vidtmp/")

#open csv, make clip from each line
with open(args.path, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    filelist = open("filelist.txt", 'w')
    cliplist = open("cliplist.txt", 'w')
    count = 0
    streamer_tstamp = datetime.timedelta(seconds=0)
    last_streamer = ""
    
    #build streamer list
    streamer_list = []
    if args.streamer:
        arg_list = args.streamer.split()
        for item in arg_list:
            if item == 'hljp':
                streamer_list += hljp
            elif item == 'hlen':
                streamer_list += hlen
            elif item == 'hlid':
                streamer_list += hlid
            elif item == 'hstars':
                streamer_list += hstars
            else:
                streamer_list.append(item)
                
    for row in csvreader:
        full_url = row[2]
        streamer = row[0]
        title = row[1]
        url_list = []
        if full_url != 'link':
        
            #only process streamers in list if specified
            if streamer_list:
                if streamer not in streamer_list:
                    continue

            #skip covers
            if "cover" in title.lower():
                continue
                    
            #write new streamer timestamp for YT descriptions
            if streamer != last_streamer:
                cliplist.write(str(streamer_tstamp) + " - " + streamer + '\n')
                last_streamer = streamer
                
            url = full_url.split('&')[0]
            vid_id = url.split('=')[1]
            timecode = full_url.split('=')[2]
            filename = f"vidtmp/{vid_id}.mp4"
            url_list.append(url)
            
            #process stream if file doesn't exist
            if not os.path.exists(filename):
                proc = subprocess.Popen(f"/usr/local/bin/youtube-dl --youtube-skip-dash-manifest -g \"{url}\"", stdout=subprocess.PIPE, shell=True)
                vid_strm = proc.communicate()[0]
                vid_strm = vid_strm.decode('utf-8').split('\n')
                
                #timecode adjustments for start of stream and iframe detection
                ss = 30
                if int(timecode) > 30:
                    start_time = str(datetime.timedelta(seconds=int(timecode)-30))
                else:
                    start_time = str(datetime.timedelta(seconds=int(timecode)))
                    ss = 0
                end_time = str(datetime.timedelta(seconds=int(timecode)) + datetime.timedelta(seconds=args.length))
                length = str(datetime.timedelta(seconds=args.length))
                
                proc = subprocess.Popen(f"ffmpeg -ss {start_time} -i \"{vid_strm[0]}\" -ss {start_time} -i \"{vid_strm[1]}\" -map 0:v -map 1:a -ss {str(ss)} -t {length} -c:v libx264 -r 30 -c:a aac -ar 48000 -b:a 192k -avoid_negative_ts make_zero -fflags +genpts \"{filename}\"", shell=True)
                out = proc.communicate()
                
            
            filelist.write(f"file \'{filename}\'\n")
            streamer_tstamp += datetime.timedelta(seconds=60)


            
    if not args.no_concat:
        #concat files
        filelist.close()
        proc = subprocess.Popen(f"ffmpeg -f concat -segment_time_metadata 1 -i filelist.txt -vf select=concatdec_select -af aselect=concatdec_select,aresample=async=1 {args.output}", shell=True)
        out = proc.communicate()
        
        if args.thumb:
            proc = subprocess.Popen(f"vcsi {args.output} -g 2x2 -w 1280 --metadata-position hidden", shell=True)
            out = proc.communicate()
