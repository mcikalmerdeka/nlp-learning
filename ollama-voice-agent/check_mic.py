import pyaudio

def check_microphones():
    try:
        p = pyaudio.PyAudio()
        
        print("Available Audio Input Devices:\n")
        print(f"{'Index':<8} {'Name':<50} {'Channels':<10} {'Default'}")
        print("-" * 80)
        
        default_input = p.get_default_input_device_info()['index']
        input_devices = []
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            
            # Only show input devices (microphones)
            if info['maxInputChannels'] > 0:
                is_default = " [DEFAULT]" if i == default_input else ""
                print(f"{i:<8} {info['name']:<50} {info['maxInputChannels']:<10} {is_default}")
                input_devices.append(info)
        
        print(f"\nTotal input devices: {len(input_devices)}")
        
        if input_devices:
            print(f"\nDefault microphone: {default_input} - {default_input_info['name']}" 
                  if (default_input_info := p.get_default_input_device_info()) else "")
        
        p.terminate()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: You may need to install PyAudio:")
        print("pip install pyaudio")

if __name__ == "__main__":
    check_microphones()
