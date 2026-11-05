import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
import numpy as np

def generate_spectrogram_barcode(wav_file, output_file):
    print(f"Processing {wav_file}...")
    
    # 1. Read the audio
    rate, data = wav.read(wav_file)
    if len(data.shape) > 1:
        data = data[:, 0]  # Mono

    # 2. Setup the Plot
    plt.figure(figsize=(12, 4))
    
    # 3. Generate Spectrogram
    # NFFT=256 reduces vertical resolution (making it look like bars)
    # cmap='gray_r' makes loud sounds BLACK and quiet sounds WHITE (Barcode style)
    # vmin/vmax forces high contrast to remove background noise
    plt.specgram(data, NFFT=256, Fs=rate, noverlap=0, cmap='gray_r', vmin=-100, vmax=10)
    
    # 4. Clean up the image (Remove axes, labels, whitespace)
    plt.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    # 5. Save
    plt.savefig(output_file, dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close()
    
    print(f"Success! Saved {output_file}")

try:
    generate_spectrogram_barcode('challenge.wav', 'final_solution.png')
except Exception as e:
    print(f"Error: {e}")