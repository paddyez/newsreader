import feedparser
import time
import torch
from TTS.api import TTS

#https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best
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
    i = 0
    full_text = "----\n"
    for entry in parsed.entries:
        # Last 18 h
        if time.time() - time.mktime(entry.published_parsed) < (86400 * .75):
            text = ''
            text += entry.title + "\n"
            text += entry.summary
            full_text = append_to_fulltext(entry, full_text, text)
            file_path = "nachrichten/" + str(i) + ".wav"
            # Replace all "Durchkopplungen" because it does not seem to work with tts and makes it crash!
            text = text.replace('K.o.-Schlag','KO Schlag')
            text = text.replace('"Starliner"-Kapsel', 'Starliner Kapsel')
            try:
                tts.tts_to_file(text=text, file_path=file_path)
            except Exception as e:
                print("There was an error: ", e)
            i += 1
    print(full_text)

def append_to_fulltext(entry, full_text, text):
    """
    Just the whole Text output
    """
    full_text += text
    full_text += "\n" + entry.link + "\n"
    full_text += entry.published + "\n"
    full_text += "----\n"
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
