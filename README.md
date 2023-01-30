# AV-Summarization-GPT-Whisper

**AV Summarization GPT Whisper** is a python library for summarizing audio/video files. There is also built in support for YouTube, with support for YouTube caption tracks.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required libraries.

```bash
pip install -r requirements.txt
```

or

```bash
pip install openai openai-whisper pytube nltk summarizer
```

## Setup

### Config

You must input your OpenAI API key in `config.py`. Additionally, you can change a lot of the default options in `config.py`. This includes the prompts that are used, and some other useful options.

### pytube error

The `pytube` library has an error that will prevent this program from working. To fix this, navigate to `captions.py` in the `pytube` site-package folder. Add `import json` to the top of `captions.py` to fix the error.

## Usage

### Command Line

The included `main.py` acts as a command line utility. Run `py ./main.py -h` for a full list of arguments. Note that you must provide either a filepath or a YouTube URL.

```bash
py ./main.py -fp ./example.mp4 -t "Example Input Video Title"
```

### Python

There is an included `main.ipynb` that you can use to interact with the python code. It also serves as a decent example of how you could utilize this in your own code. There are some additional explantions there as well. Here is an brief excerpt of the code:

```python
from handlers import AVHandler, SummaryHandler
transcript_handler = AVHandler(
    filepath='./example.mp4',
    title='Example Input Video Title'
)
summary_handler: SummaryHandler = transcript_handler.get_summary_handler()
summary = summary_handler.get_summary()
print(summary)
```

## Explanation of Process

AV Summarization GPT Whisper works in a 3-step process.

### 1. Get Audio Transcript

First, we need to get a transcript of the audio file. If it is a YouTube video, there is the option of using YouTube's caption tracks. Otherwise, process the file using Whisper.

### 2. Get Truncated Transcript

In order to process with GPT-3, we must shorten the transcript if it is over a certain length. We do this via extractive text summarization. First, we preserve a set number of sentences at the front and back of the transcript. Then, we use the summarizer library to score every sentence. The scores are calculated using a global word frequency dictionary, with additional points awarded if the sentence shares words with the title. We keep adding the next top sentence (in the correct position) until the token limit is reached.

This method is not without it's flaws. Extractive text summarization by it's nature means that some sentences will lose their context. Also, the method of ranking sentences is somewhat archaic. However, I chose this method allows us to process arbitrarily long transcripts.

### 3. Generate Summary

We then send the truncated summary, along with an initial prompt, to the GPT-3 API. Out comes a summary!

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
