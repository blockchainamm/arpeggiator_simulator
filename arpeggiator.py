# Program to simulate a arpeggiator matching the frequencies of notes in piano

# Import required packages
import numpy as np
import pyaudio
import time
import pandas as pd
import ezodf

# Open open office calc file containing piano note frequencies into a variable
doc = ezodf.opendoc('piano_notes.ods')
print("Spreadsheet contains %d sheet(s)." % len(doc.sheets))
for sheet in doc.sheets:
    print("-"*40)
    print("   Sheet name : '%s'" % sheet.name)
    print("Size of Sheet : (rows=%d, cols=%d)" % (sheet.nrows(), sheet.ncols()) )

# convert the first sheet to a pandas.DataFrame
sheet = doc.sheets[0]
df_dict = {}
for i, row in enumerate(sheet.rows()):
    # row is a list of cells
    # assume the header is on the first row
    if i == 0:
        # columns as lists in a dictionary
        df_dict = {cell.value:[] for cell in row}
        # create index for the column headers
        col_index = {j:cell.value for j, cell in enumerate(row)}
        continue
    for j, cell in enumerate(row):
        # use header instead of column index
        df_dict[col_index[j]].append(cell.value)


# and convert to a DataFrame
pianonotes_df = pd.DataFrame(df_dict)


# Create a new column with index values
pianonotes_df['index_column'] = pianonotes_df.index

# Using reset_index() to set index into column
notes_df=pianonotes_df.reset_index()

# drop column which are not required
notes_df.drop('index_column', axis=1, inplace=True)

# Drop all rows with NaN values
pnotes_df=notes_df.dropna()
pnotes_df=notes_df.dropna(axis=0)

# Reset index after drop
pnotes_df=notes_df.dropna().reset_index(drop=True)


# Set sample rate either to 44100 or 48000
SAMPLE_RATE = 44100


def generate_sample(freq, duration, volume):

    amplitude = 2000
    total_samples = np.round(SAMPLE_RATE * duration)
    w = 2.0 * np.pi * freq / SAMPLE_RATE
    k = np.arange(0, total_samples)

    return np.round(amplitude * np.sin(k * w))

# Function to load notes into a list object
def load_notes(notestep):
    
    # Interval of notes for a major chords
    notes_interval = [4, 3, 5, 0]
    
    tones_fwd = []
    
    print(f'The frequencies of ascending notes of the major chords for note {notescale}')
    for note in notes_interval: 
        # print the frequency ascending notes of the major chords        
        print(rev_freq[notestep])
        
        # Call function to generate the equivalent tone for the given frequency
        tone = np.array(generate_sample(rev_freq[notestep], 0.6, 0.5), dtype=np.int16)    
        notestep = note + notestep

        # Appending the ascending tones of the scale to a list
        tones_fwd.append(tone)
    
    # Return list of frequencies in the ascending notes of the major chords    
    return tones_fwd


# Function to play the sounds from the generated tones
def fmain(tones_fwd):
    # Instantiate PyAudio and initialize PortAudio system resources
    p = pyaudio.PyAudio()

    # Open stream 
    stream = p.open(format=p.get_format_from_width(width=2), 
                    channels=3, 
                    rate=SAMPLE_RATE,
                    output=True)
 
    arp_cycl = 10
    nbr = 1

    # Loop arpeggio sequence 10 times non stop to produce arpeggiator effect
    while nbr <= arp_cycl:
        # Play samples from the tones list with a interval between successive notes
        # This list is the ascending order. That is from lower to higher frequency octave
        for tone in tones_fwd:
            stream.write(tone)
            time.sleep(0.05) # wait for 50 milli seconds between tones
               
        nbr += 1 
        
    stream.stop_stream()
    # Close stream 
    stream.close()
    
    # Release PortAudio system resources 
    p.terminate()


# Function to locate the rows and columbs in the dataframe for the given notes in the scale list
def locate_in_df(pnotes_df, value):
    a = pnotes_df.to_numpy()
    row = np.where(a == value)[0][0]
    col = np.where(a == value)[1][0]
    return row, col

# Note list to produce arpeggiator pattern sequence
scale_list = ['C4', 'A3', 'G4', 'C3', 'E5', 'F4', 'C4']

notestep = 0

# Function to play the scales for the given notes in the scale list
for notescale in scale_list:
    row, col= locate_in_df(pnotes_df, notescale)
    print('-----')
    print(f"Row : {row} and column : {col}  of note {notescale} in the data frame pnotes_df")    
                    
    # Use the where method to select rows where index >= selected row
    df_filtered = pnotes_df.where(pnotes_df['index'] <= row).dropna()

    notelist = df_filtered['FrequencyHz'].values.tolist()

    rev_freq = notelist[::-1] 

    tones_fwd = load_notes(notestep)

    # Calling function to play the frequencies converted into tones 
    fmain(tones_fwd)