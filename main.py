import argparse
from argparse import Namespace
from handlers import AVHandler, YouTubeHandler
from config import *

def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description='Summarize an AV file, or a YouTube video. You must provide ONE of filepath or yturl.')
    parser.add_argument('-fp', '--filepath', help='Filepath to the local AV file.')
    parser.add_argument('-url', '--youtubeurl', help='YouTube Video URL.')
    parser.add_argument('-o', '--output', default=OUTPUT_PATH, help='Set path to outputted summary. If not provided, output will only be prinited to console.')
    parser.add_argument('-t', '--title', default='', help='Set the video title. If YouTube, will use video title. Otherwise, it will improve results to provide one here. (defaults to none)')
    
    parser.add_argument('-ttl', '--texttokenlimit', default=TEXT_TOKEN_LIMIT, help="Set the token limit for the text to be summarized by GPT. Remember that GPT-3's total limit is 4096, and you must leave room for it's response. Also, about 200 tokens of prompt are added on top of this. (defaults to 2048)")
    parser.add_argument('-rtl', '--responsetokenlimit', default=RESPONSE_TOKEN_LIMIT, help="Set the token limit for the summary returned by GPT. Remember that GPT-3's total limit is 4096, including this response length. (defaults to 1024)")
    
    parser.add_argument('-fsp', '--frontsentencespreserved', default=FRONT_SENTENCES_PRESERVED, help="Number of front sentences to be preserved when doing extractive summarization. (defaults to 5)")
    parser.add_argument('-bsp', '--backsentencespreserved', default=BACK_SENTENCES_PRESERVED, help="Number of back sentences to be preserved when doing extractive summarization. (defaults to 5)")
    
    parser.add_argument('-ytc', '--youtubecaptions', action='store_true', default=YOUTUBE_CAPTIONS, help=f'If flagged will use YouTube creator-provided captions, if available. (defaults to {YOUTUBE_CAPTIONS})')
    parser.add_argument('-ytac', '--youtubeautocaptions', action='store_true', default=YOUTUBE_AUTO_CAPTIONS, help=f'If flagged will use YouTube auto-generated captions, if creator-provided captions are not available. (defaults to {YOUTUBE_AUTO_CAPTIONS})')
    parser.add_argument('-wm', '--whispermodel', default=WHISPER_MODEL, choices=['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large'], help=f'Choose the pretrained Whisper model. (defaults to {WHISPER_MODEL})')
    
    args = parser.parse_args()
    
    if bool(args.filepath) is bool(args.youtubeurl):
        raise ValueError('You must provide ONE of filepath or youtubeurl.')
    
    return args

def main():
    args = parse_args()
    transcript_handler = AVHandler(args.filepath, args.title, args.whispermodel) if args.filepath else YouTubeHandler(args.youtubeurl)
    summary_handler = transcript_handler.get_summary_handler()
    summary = summary_handler.get_summary()
    with open(args.output, 'w') as outfile:
        outfile.write(summary)

if __name__ == '__main__':
    main()