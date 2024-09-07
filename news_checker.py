import feedparser
import time
import torch
from TTS.api import TTS
from pathlib import Path

#RSS_URI = 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best'
RSS_URI = 'https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml'
device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=True).to(device)

def are_there_updates():
    """
    Should check for new News…
    """
    parsed = feedparser.parse(RSS_URI)
    if parsed.status == 200:
        possible_to_reduce_bandwidth(parsed)
        create_audio_for_entries(parsed)
    else:
        print(f"Parsing URI failed. Http Status: {parsed.status}")

def create_audio_for_entries(parsed):
    """
    For each news entry in the last 18 hours, create audio file and save to nachrichten als *.wav
    """
    new_items = []
    full_text = "= News\n\n"
    for entry in parsed.entries:
        # Last 18 h
        published_time = entry.published_parsed
        if time.time() - time.mktime(published_time) < (86400 * .75):
            text = ''
            text += entry.title + "\n"
            text += entry.summary
            full_text = append_to_fulltext(entry, full_text)
            date_string = time.strftime("%Y-%m-%d_%H-%M-%S", published_time)
            file_path = "nachrichten/" + date_string + "_" + entry.title + ".wav"
            # Replace all "Durchkopplungen" because it does not seem to work with tts and makes it crash!
            text = text.replace('K.o.-Schlag','KO Schlag')
            text = text.replace('"Starliner"-Kapsel', 'Starliner Kapsel')
            try:
                file = Path(file_path)
                if not file.exists():
                    new_items.append(file_path)
                    tts.tts_to_file(text=text, file_path=file_path)
            except Exception as e:
                print("There was an error: ", e)
    file = open("News.adoc", "w")
    file.write(full_text)
    for new_item in new_items:
        print(f"New news item: {new_item}")

def append_to_fulltext(entry, full_text):
    """
    Just the whole Text output
    """
    full_text += "== " + entry.link + "[" + entry.title.replace('+', '{plus}') + "]\n\n"
    full_text += entry.summary + "\n\n"
    full_text += entry.published + "\n\n"
    return full_text

def possible_to_reduce_bandwidth(parsed):
    """
    https://feedparser.readthedocs.io/en/latest/http-etag.html#using-last-modified-headers-to-reduce-bandwidth
    """
    if hasattr(parsed, 'etag'):
        print(f"Etag: {parsed.etag}")
    elif hasattr(parsed, 'modified'):
        print(f"Modified: {parsed.modified}")
    else:
        print(f"No etag or modified found! Therefore not possible to use with this feed.")
