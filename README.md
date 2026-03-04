Script for downloading folders from an archive site.

# Read first
- The script does not currently check the size of the folder before starting.
- No error handling implemented yet. If a file fails to download, it'll stop the script, and you will have to begin downloading again starting from the failed file.


# Instructions for use:
1. Clone the repository `git clone https://github.com/I-Like-Fire/myrient-downloader.git`
2. Create the virtual environment `python -m venv venv`
3. Activate the virtual environment `. venv/bin/activate`
4. Install the dependencies `pip install -r requirements`
5. Run the script `python /path/to/script/main.py <folder url>`
