from tqdm import tqdm
from time import sleep
import string

for i in tqdm(range(100)):
    sleep(0.02)


# A list from A to Z wrapped around TQDM function
progress_bar = tqdm(list(string.ascii_lowercase))
for letter in progress_bar:
    progress_bar.set_description(f'Processing {letter}...')
    sleep(0.09)
